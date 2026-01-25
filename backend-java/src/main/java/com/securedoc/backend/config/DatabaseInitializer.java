package com.securedoc.backend.config;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

/**
 * Ensures optimal DB state on startup (Self-Healing).
 * Lightweight alternative to full migration tools like Flyway.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class DatabaseInitializer implements CommandLineRunner {

    private final JdbcTemplate jdbcTemplate;

    @Override
    public void run(String... args) throws Exception {
        log.info("Checking database indices...");

        try {
            // Ensure vector extension is enabled
            jdbcTemplate.execute("CREATE EXTENSION IF NOT EXISTS vector");

            // Ensure HNSW index exists (Robustness ensuring reproducibility)
            // This guarantees performance even if init.sql didn't run on an existing
            // volume.
            String createIndexSql = "CREATE INDEX IF NOT EXISTS embedding_hnsw_idx ON document_chunks USING hnsw (embedding vector_cosine_ops)";
            jdbcTemplate.execute(createIndexSql);

            log.info("Verified HNSW Index 'embedding_hnsw_idx': OK");
        } catch (Exception e) {
            log.error("Failed to initialize database indices: {}", e.getMessage());
            // Don't fail the app, but log it. The query might fail if pgvector is missing.
        }
    }
}
