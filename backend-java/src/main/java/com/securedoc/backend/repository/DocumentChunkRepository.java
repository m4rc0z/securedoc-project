package com.securedoc.backend.repository;

import com.securedoc.backend.model.DocumentChunk;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DocumentChunkRepository extends JpaRepository<DocumentChunk, Long> {

    // Native query for vector similarity search using cosine distance (<=>
    // operator)
    // We select only content and source_file to avoid mapping issues with the
    // vector column
    @Query(value = "SELECT content, source_file FROM document_chunks ORDER BY embedding <=> cast(?1 as vector) LIMIT ?2", nativeQuery = true)
    List<ChunkProjection> findNearest(String embedding, int limit);

    @org.springframework.data.jpa.repository.Modifying
    @org.springframework.transaction.annotation.Transactional
    @Query(value = "INSERT INTO document_chunks (content, source_file, embedding) VALUES (?1, ?2, cast(?3 as vector))", nativeQuery = true)
    void saveChunk(String content, String sourceFile, String embedding);
}
