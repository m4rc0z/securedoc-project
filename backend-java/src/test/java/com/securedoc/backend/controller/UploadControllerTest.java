package com.securedoc.backend.controller;

import com.securedoc.backend.service.IngestionService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.mock.web.MockMultipartFile;

import java.io.IOException;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
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

        // Mock the new signature: processDocument(String filePath, String
        // originalFilename)
        doNothing().when(ingestionService).processDocument(anyString(), anyString());

        // Act
        ResponseEntity<Map<String, Object>> response = uploadController.uploadDocument(file);

        // Assert
        assertEquals(HttpStatus.ACCEPTED, response.getStatusCode());
        assertEquals("processing_started", response.getBody().get("status"));
        assertEquals("test.pdf", response.getBody().get("filename"));

        // Verify interactions - now expects two String arguments
        verify(ingestionService, times(1)).processDocument(anyString(), eq("test.pdf"));
    }
}
