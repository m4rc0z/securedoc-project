package com.securedoc.backend.controller;

import com.securedoc.backend.client.AIServiceClient;
import com.securedoc.backend.client.AIServiceClient.IngestResponse; // Assuming this DTO exists based on controller usage
import com.securedoc.backend.client.AIServiceClient.ChunkData; // Assuming this inner DTO exists
import com.securedoc.backend.repository.DocumentChunkRepository;
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
    private PdfService pdfService;

    @Mock
    private AIServiceClient aiClient;

    @Mock
    private DocumentChunkRepository chunkRepository;

    @InjectMocks
    private UploadController uploadController;

    @Test
    public void testUploadDocument_Success() throws IOException {
        // Arrange
        MockMultipartFile file = new MockMultipartFile("file", "test.pdf", "application/pdf", "dummy content".getBytes());
        String extractedText = "Extracted Text Content";
        when(pdfService.extractText(any())).thenReturn(extractedText);

        // Mock Ingest Response
        ChunkData chunk = new ChunkData("Extracted Text Content", List.of(0.1f, 0.2f, 0.3f), Map.of());
        IngestResponse ingestResponse = new IngestResponse(List.of(chunk));
        when(aiClient.ingest(eq(extractedText), anyMap())).thenReturn(ingestResponse);

        // Act
        ResponseEntity<Map<String, Object>> response = uploadController.uploadDocument(file);

        // Assert
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals("success", response.getBody().get("status"));
        assertEquals(1, response.getBody().get("chunks_count"));
        
        // Verify interactions
        verify(pdfService, times(1)).extractText(any());
        verify(aiClient, times(1)).ingest(eq(extractedText), anyMap());
        verify(chunkRepository, times(1)).saveAll(anyList());
    }
}
