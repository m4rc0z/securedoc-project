package com.securedoc.backend.controller;

import com.securedoc.backend.client.AIServiceClient;
import com.securedoc.backend.model.DocumentChunk;
import com.securedoc.backend.repository.DocumentChunkRepository;
import com.securedoc.backend.service.PdfService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/documents")
public class UploadController {

    private final PdfService pdfService;
    private final AIServiceClient aiClient;
    private final DocumentChunkRepository chunkRepository;

    public UploadController(PdfService pdfService, AIServiceClient aiClient, DocumentChunkRepository chunkRepository) {
        this.pdfService = pdfService;
        this.aiClient = aiClient;
        this.chunkRepository = chunkRepository;
    }

    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> uploadDocument(@RequestParam("file") MultipartFile file) {
        try {
            // 1. Extract Text
            String text = pdfService.extractText(file);

            // 2. Process via Python AI Service (Split & Embed)
            var response = aiClient.ingest(text, Map.of("filename", file.getOriginalFilename()));

            // 3. Save to DB (Native Insert to avoid Hibernate Mapping Issues)
            for (var chunk : response.chunks()) {
                chunkRepository.saveChunk(
                        chunk.content(),
                        file.getOriginalFilename(),
                        chunk.getEmbeddingAsVector().toString());
            }

            return ResponseEntity.ok(Map.of(
                    "status", "success",
                    "chunks_count", response.chunks().size(),
                    "filename", file.getOriginalFilename()));

        } catch (IOException e) {
            return ResponseEntity.internalServerError().body(Map.of("error", "Failed to parse PDF: " + e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("error", "Processing failed: " + e.getMessage()));
        }
    }
}
