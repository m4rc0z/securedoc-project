package com.securedoc.backend.service;

import com.securedoc.backend.model.Document;
import com.securedoc.backend.repository.DocumentRepository;
import com.securedoc.backend.repository.DocumentChunkRepository; // Will add delete method here
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
public class DocumentService {

    private final DocumentRepository documentRepository;
    private final DocumentChunkRepository documentChunkRepository;

    public DocumentService(DocumentRepository documentRepository, DocumentChunkRepository documentChunkRepository) {
        this.documentRepository = documentRepository;
        this.documentChunkRepository = documentChunkRepository;
    }

    public List<Document> getAllDocuments() {
        return documentRepository.findAll();
    }

    @Transactional
    public void deleteDocument(UUID id) {
        // 1. Delete Chunks first (Manual Cascade)
        documentChunkRepository.deleteByDocumentId(id);

        // 2. Delete Document
        documentRepository.deleteById(id);
    }
}
