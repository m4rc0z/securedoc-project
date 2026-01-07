-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table for storing document chunks and embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id BIGSERIAL PRIMARY KEY,
    content TEXT,
    -- 384 dimensions for all-MiniLM-L6-v2. If using a larger model, update this.
    embedding vector(384),
    metadata JSONB DEFAULT '{}',
    -- Hybrid Search: Automatically generated tsvector from content
    search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);

-- HNSW Index for fast vector search (Ops: vector_cosine_ops)
CREATE INDEX IF NOT EXISTS embedding_hnsw_idx ON document_chunks USING hnsw (embedding vector_cosine_ops);

-- GIN Index for fast keyword search (Hybrid Search)
CREATE INDEX IF NOT EXISTS content_search_idx ON document_chunks USING GIN (search_vector);
