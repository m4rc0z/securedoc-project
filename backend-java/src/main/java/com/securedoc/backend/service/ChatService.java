package com.securedoc.backend.service;

import com.securedoc.backend.client.AIServiceClient;
import com.securedoc.backend.dto.ChatRequest;
import com.securedoc.backend.dto.ChatResponse;
import com.securedoc.backend.repository.ChunkProjection;
import com.securedoc.backend.repository.DocumentChunkRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class ChatService {

    private final AIServiceClient aiClient;
    private final DocumentChunkRepository chunkRepository;

    public ChatService(AIServiceClient aiClient, DocumentChunkRepository chunkRepository) {
        this.aiClient = aiClient;
        this.chunkRepository = chunkRepository;
    }

    public ChatResponse chat(ChatRequest request) {
        System.out.println("Step 1: Embedding question...");
        // 1. Embed the question
        var embeddingResponse = aiClient.embed(request.question());
        System.out.println("Step 1: Done. Vector generated.");

        // 2. Find relevant chunks (RAG)
        System.out.println("Step 2: Searching DB for context...");
        String vectorString = embeddingResponse.getAsVector().toString();
        List<ChunkProjection> chunks = chunkRepository.findNearest(vectorString, 5);
        System.out.println("Step 2: Done. Found " + chunks.size() + " chunks.");

        // 3. Prepare Context
        // 3. Prepare Context
        String context = chunks.stream()
                .map(ChunkProjection::getContent)
                .collect(Collectors.joining("\n---\n"));

        // 4. Ask LLM
        System.out.println("Step 4: Calling LLM (this may take time)...");
        var ragResponse = aiClient.ask(request.question(), context);
        System.out.println("Step 4: LLM responded.");

        return new ChatResponse(ragResponse.answer(), List.of("Source: Internal DB (Top 5 Matches)"));
    }
}
