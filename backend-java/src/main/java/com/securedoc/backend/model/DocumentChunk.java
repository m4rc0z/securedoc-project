package com.securedoc.backend.model;

import com.pgvector.PGvector;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "document_chunks")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DocumentChunk {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(columnDefinition = "TEXT")
    private String content;

    @Column(name = "embedding", columnDefinition = "vector")
    @JdbcTypeCode(SqlTypes.VECTOR)
    private PGvector embedding;

    public DocumentChunk(String content, PGvector embedding) {
        this.content = content;
        this.embedding = embedding;
    }
}
