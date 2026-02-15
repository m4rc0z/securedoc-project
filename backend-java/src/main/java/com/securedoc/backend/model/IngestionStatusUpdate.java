package com.securedoc.backend.model;

import java.util.UUID;

public record IngestionStatusUpdate(
        UUID id,
        String filename,
        FileStatus status,
        String errorMessage) {
}
