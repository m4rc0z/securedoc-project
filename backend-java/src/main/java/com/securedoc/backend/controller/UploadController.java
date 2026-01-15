package com.securedoc.backend.controller;

import com.securedoc.backend.service.IngestionService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

@RestController
@RequestMapping("/api/documents")
public class UploadController {

    private final IngestionService ingestionService;

    public UploadController(IngestionService ingestionService) {
        this.ingestionService = ingestionService;
    }

    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> uploadDocument(@RequestParam("file") MultipartFile file) {
        try {
            ingestionService.processDocument(file);

            return ResponseEntity.accepted().body(Map.of(
                    "status", "processing_started",
                    "message", "Document ingestion started in background.",
                    "filename", file.getOriginalFilename()));

        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", "Failed to initiate processing: " + e.getMessage()));
        }
    }
}
