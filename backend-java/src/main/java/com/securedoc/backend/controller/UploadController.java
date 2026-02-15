package com.securedoc.backend.controller;

import com.securedoc.backend.service.IngestionService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.UUID;

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
            String fileName = file.getOriginalFilename();
            Path uploadPath = Path.of("/app/uploads"); // Matches Docker Config
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            String savedFileName = UUID.randomUUID() + "_" + fileName;
            Path targetLocation = uploadPath.resolve(savedFileName);
            file.transferTo(targetLocation);

            ingestionService.processDocument(targetLocation.toString(), fileName);

            return ResponseEntity.accepted().body(Map.of(
                    "status", "processing_started",
                    "message", "Document ingestion started in background.",
                    "filename", fileName));

        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", "Failed to initiate processing: " + e.getMessage()));
        }
    }
}
