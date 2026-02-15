package com.securedoc.backend.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "documents")
@Data
@Builder(toBuilder = true)
@NoArgsConstructor
@AllArgsConstructor
public class Document {
    @Id
    private UUID id;

    @Column(nullable = false)
    private String filename;

    @Column(name = "upload_date")
    private LocalDateTime uploadDate;

    @Column(columnDefinition = "jsonb")
    @org.hibernate.annotations.JdbcTypeCode(org.hibernate.type.SqlTypes.JSON)
    private String metadata;

    @Lob
    @Basic(fetch = FetchType.LAZY)
    @Column(name = "content")
    private byte[] content;

    @Column(name = "status")
    private FileStatus status;

    @Column(name = "errorMessage")
    private String errorMessage;
    
}
