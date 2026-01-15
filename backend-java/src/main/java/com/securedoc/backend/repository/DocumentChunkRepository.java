package com.securedoc.backend.repository;

import com.securedoc.backend.model.DocumentChunk;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Repository
public interface DocumentChunkRepository extends JpaRepository<DocumentChunk, Long> {

    // Native query for vector similarity search using cosine distance (<=>
    // operator)
    // We select only content and source_file to avoid mapping issues with the
    // vector column
    @Query(value = "SELECT content, source_file FROM document_chunks ORDER BY embedding <=> cast(?1 as vector) LIMIT ?2", nativeQuery = true)
    List<ChunkProjection> findNearest(String embedding, int limit);

    @Modifying
    @Transactional
    @Query(value = "INSERT INTO document_chunks (content, source_file, embedding, document_id) VALUES (?1, ?2, cast(?3 as vector), ?4)", nativeQuery = true)
    void saveChunk(String content, String sourceFile, String embedding, java.util.UUID documentId);

    // Filtered Search
    // Matches if filters (?2) is contained in metadata column.
    // If filters is '{}' (empty json), valid JSONB containment checks still work
    // (it's a subset of everything).
    @Query(value = "SELECT content, source_file FROM document_chunks WHERE metadata @> cast(?2 as jsonb) ORDER BY embedding <=> cast(?1 as vector) LIMIT ?3", nativeQuery = true)
    List<ChunkProjection> findNearestWithFilters(String embedding, String filters, int limit);

    @Modifying
    @Transactional
    @Query(value = "DELETE FROM document_chunks WHERE document_id = ?1", nativeQuery = true)
    void deleteByDocumentId(java.util.UUID documentId);
}
