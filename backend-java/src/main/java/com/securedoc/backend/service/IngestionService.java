package com.securedoc.backend.service;

import com.securedoc.backend.client.AIServiceClient;
import com.securedoc.backend.model.Document;
import com.securedoc.backend.model.DocumentChunk;
import com.securedoc.backend.repository.DocumentChunkRepository;
import com.securedoc.backend.repository.DocumentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor
public class IngestionService {

    private final PdfService pdfService;
    private final AIServiceClient aiClient;
    private final DocumentChunkRepository chunkRepository;
    private final DocumentRepository documentRepository;

    @Async
    public void processDocument(MultipartFile file) {
        String filename = file.getOriginalFilename();
        log.info("Starting async ingestion for file: {}", filename);

        try {
            // 1. Extract Text
            String text;
            if (filename != null && filename.toLowerCase().endsWith(".txt")) {
                text = new String(file.getBytes(), java.nio.charset.StandardCharsets.UTF_8);
            } else {
                text = pdfService.extractText(file);
            }

            // 2. Process via Python AI Service (Split & Embed)
            var response = aiClient.ingest(text, Map.of("filename", filename));

            // 3. Save Document Metadata
            String metadataJson = new com.fasterxml.jackson.databind.ObjectMapper()
                    .writeValueAsString(response.documentMetadata());

            Document doc = Document.builder()
                    .id(java.util.UUID.randomUUID())
                    .filename(filename)
                    .uploadDate(java.time.LocalDateTime.now())
                    .metadata(metadataJson)
                    .build();

            documentRepository.save(doc);

            // 4. Save Chunks (Linked to Document)
            for (var chunk : response.chunks()) {
                chunkRepository.saveChunk(
                        chunk.content(),
                        filename,
                        chunk.getEmbeddingAsVector().toString(),
                        doc.getId());
            }

            log.info("Finished ingestion for file: {}. Chunks created: {}", filename, response.chunks().size());

        } catch (Exception e) {
            log.error("Failed to ingest file: {}", filename, e);
            // Ideally: Update a status in DB or notify user via WebSocket
        }
    }
}
