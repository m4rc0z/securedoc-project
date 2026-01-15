package com.securedoc.backend.service;

import com.securedoc.backend.client.AIServiceClient;
import com.securedoc.backend.dto.ChatRequest;
import com.securedoc.backend.dto.ChatResponse;
import com.securedoc.backend.repository.ChunkProjection;
import com.securedoc.backend.repository.DocumentChunkRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@Slf4j
@RequiredArgsConstructor
public class ChatService {

    private final AIServiceClient aiClient;
    private final DocumentChunkRepository chunkRepository;

    public ChatResponse chat(ChatRequest request) {
        log.debug("Processing chat request for query: {}", request.question());

        // 1. Plan the query (Python Agent)
        var plan = aiClient.plan(request.question());
        String effectiveQuestion = plan.rewrittenQuestion();
        String intent = plan.intent();
        log.info("Query Plan - Intent: {}, Rewritten: {}", intent, effectiveQuestion);

        // 2. Embed the effective question (better semantic match)
        var embeddingResponse = aiClient.embed(effectiveQuestion);
        String vectorString = embeddingResponse.getAsVector().toString();

        // 3. Find relevant chunks (RAG) with Filters
        log.debug("Executing vector search...");
        List<ChunkProjection> chunks;
        try {
            String filtersJson = new com.fasterxml.jackson.databind.ObjectMapper().writeValueAsString(plan.filters());
            // If filters are empty map, JSON is "{}", which works with our query logic
            chunks = chunkRepository.findNearestWithFilters(vectorString, filtersJson, 10);
        } catch (Exception e) {
            log.warn("Filter serialization failed, falling back to unfiltered search: {}", e.getMessage());
            chunks = chunkRepository.findNearest(vectorString, 10);
        }
        log.info("Retrieved {} chunks from database.", chunks.size());

        // 4. Prepare Context (Deduplicate chunks)
        String context = chunks.stream()
                .map(ChunkProjection::getContent)
                .distinct()
                .collect(Collectors.joining("\n---\n"));

        // 5. Ask LLM (using effective question)
        log.debug("Calling AI Service for generation...");
        var ragResponse = aiClient.ask(effectiveQuestion, context);
        log.info("AI Service responded successfully.");

        // Dynamic Sources
        List<String> sources = chunks.stream()
                .map(c -> "📄 " + c.getSourceFile())
                .distinct()
                .limit(5)
                .collect(Collectors.toList());

        if (sources.isEmpty()) {
            sources.add("Internal Knowledge Base");
        }

        return new ChatResponse(ragResponse.answer(), sources);
    }
}
