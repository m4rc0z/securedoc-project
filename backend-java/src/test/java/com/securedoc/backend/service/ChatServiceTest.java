package com.securedoc.backend.service;

import com.securedoc.backend.client.AIServiceClient;
import com.securedoc.backend.client.AIServiceClient.EmbedResponse;
import com.securedoc.backend.client.AIServiceClient.RAGResponse;
import com.securedoc.backend.dto.ChatRequest;
import com.securedoc.backend.dto.ChatResponse;
import com.securedoc.backend.repository.ChunkProjection;
import com.securedoc.backend.repository.DocumentChunkRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class ChatServiceTest {

    @Mock
    private AIServiceClient aiClient;

    @Mock
    private DocumentChunkRepository chunkRepository;

    @InjectMocks
    private ChatService chatService;

    @Test
    public void testChat() {
        // Arrange
        String question = "What is the secret?";
        ChatRequest request = new ChatRequest(question, null);

        // Mock Embedding
        List<Float> embedding = List.of(0.1f, 0.2f, 0.3f);
        EmbedResponse embedResponse = new EmbedResponse(embedding);
        when(aiClient.embed(question)).thenReturn(embedResponse);

        // Mock Chunk Retrieval
        ChunkProjection p1 = mock(ChunkProjection.class);
        when(p1.getContent()).thenReturn("Secret 1");
        ChunkProjection p2 = mock(ChunkProjection.class);
        when(p2.getContent()).thenReturn("Secret 2");

        when(chunkRepository.findNearest(anyString(), eq(5))).thenReturn(List.of(p1, p2));

        // Mock LLM Response
        String expectedAnswer = "The secret is 42.";
        RAGResponse ragResponse = new RAGResponse(expectedAnswer);
        when(aiClient.ask(eq(question), anyString())).thenReturn(ragResponse);

        // Act
        ChatResponse response = chatService.chat(request);

        // Assert
        assertEquals(expectedAnswer, response.answer());
        assertEquals(1, response.sources().size());
    }
}
