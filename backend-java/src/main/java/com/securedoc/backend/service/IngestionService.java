package com.securedoc.backend.service;

import com.securedoc.backend.client.AIServiceClient;
import com.securedoc.backend.model.Document;
import com.securedoc.backend.model.DocumentChunk;
import com.securedoc.backend.model.FileStatus;
import com.securedoc.backend.model.IngestionStatusUpdate;
import com.securedoc.backend.repository.DocumentChunkRepository;
import com.securedoc.backend.repository.DocumentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor
public class IngestionService {

    private final PdfService pdfService;
    private final AIServiceClient aiClient;
    private final DocumentChunkRepository chunkRepository;
    private final DocumentRepository documentRepository;
    private final SimpMessagingTemplate messagingTemplate;

    @Transactional
    @Async
    public void processDocument(String filePath, String originalFilename) {
        log.info("Starting async ingestion for file: {}", originalFilename);

        File file = new File(filePath);
        Document doc = Document.builder()
                .id(java.util.UUID.randomUUID())
                .filename(originalFilename != null ? originalFilename : "unknown_file")
                .status(FileStatus.PROCESSING)
                .build();
        try {
            documentRepository.save(doc);
            sendUpdate(doc);

            // 1. Extract Text
            String text;
            if (originalFilename != null && originalFilename.toLowerCase().endsWith(".txt")) {
                text = new String(Files.readAllBytes(file.toPath()), java.nio.charset.StandardCharsets.UTF_8);
            } else {
                text = pdfService.extractText(file);
            }

            // 2. Process via Python AI Service (Split & Embed)
            var response = aiClient.ingest(text, Map.of("filename", originalFilename));

            // 3. Save Document Metadata
            String metadataJson = new com.fasterxml.jackson.databind.ObjectMapper()
                    .writeValueAsString(response.documentMetadata());

            doc = doc.toBuilder()
                    .filename(originalFilename)
                    .content(Files.readAllBytes(file.toPath()))
                    .uploadDate(java.time.LocalDateTime.now())
                    .metadata(metadataJson)
                    .build();

            documentRepository.save(doc);

            // 4. Save Chunks (Linked to Document)
            for (var chunk : response.chunks()) {
                chunkRepository.saveChunk(
                        chunk.content(),
                        originalFilename,
                        chunk.getEmbeddingAsVector().toString(),
                        doc.getId());
            }

            doc.setStatus(FileStatus.COMPLETED);
            documentRepository.save(doc);
            sendUpdate(doc);

            log.info("Finished ingestion for file: {}. Chunks created: {}", originalFilename, response.chunks().size());

        } catch (Exception e) {
            doc = doc.toBuilder()
                    .status(FileStatus.FAILED)
                    .errorMessage(e.getMessage())
                    .build();
            documentRepository.save(doc);
            sendUpdate(doc);
            log.error("Failed to ingest file: {}", originalFilename, e);
            // Ideally: Update a status in DB or notify user via WebSocket
        } finally {
            if (file != null && file.exists()) {
                file.delete();
            }
        }
    }

    void sendUpdate(Document doc) {
        IngestionStatusUpdate update = new IngestionStatusUpdate(
                doc.getId(),
                doc.getFilename(),
                doc.getStatus(),
                doc.getErrorMessage());
        messagingTemplate.convertAndSend("/topic/ingestion-status", update);
    }
}
