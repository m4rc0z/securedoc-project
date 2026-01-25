package com.securedoc.backend.controller;

import com.securedoc.backend.client.AIServiceClient;
import com.securedoc.backend.client.AIServiceClient.IngestResponse; // Assuming this DTO exists based on controller usage
import com.securedoc.backend.client.AIServiceClient.ChunkData; // Assuming this inner DTO exists
import com.securedoc.backend.repository.DocumentChunkRepository;
import com.securedoc.backend.service.IngestionService;
import com.securedoc.backend.service.PdfService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.mock.web.MockMultipartFile;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class UploadControllerTest {

    @Mock
    private IngestionService ingestionService;

    @InjectMocks
    private UploadController uploadController;

    @Test
    public void testUploadDocument_Success() throws IOException {
        // Arrange
        MockMultipartFile file = new MockMultipartFile("file", "test.pdf", "application/pdf",
                "dummy content".getBytes());

        doNothing().when(ingestionService).processDocument(any());

        // Act
        ResponseEntity<Map<String, Object>> response = uploadController.uploadDocument(file);

        // Assert
        assertEquals(HttpStatus.ACCEPTED, response.getStatusCode());
        assertEquals("processing_started", response.getBody().get("status"));

        // Verify interactions
        verify(ingestionService, times(1)).processDocument(any());
    }
}
