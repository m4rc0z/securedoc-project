package com.securedoc.backend.service;

import com.securedoc.backend.client.AIServiceClient;
import com.securedoc.backend.dto.ChatRequest;
import com.securedoc.backend.dto.ChatResponse;
import com.securedoc.backend.repository.ChunkProjection;
import com.securedoc.backend.repository.DocumentChunkRepository;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;
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

        // Query planning and rewriting
        var plan = aiClient.plan(request.question());
        String effectiveQuestion = plan.rewrittenQuestion();
        String intent = plan.intent();
        log.info("Query Plan - Intent: {}, Rewritten: {}", intent, effectiveQuestion);

        // Generate embedding for the rewritten question
        var embeddingResponse = aiClient.embed(effectiveQuestion);
        String vectorString = embeddingResponse.getAsVector().toString();

        // Hybrid Search (Vector + Keyword)
        log.debug("Executing hybrid search...");
        Set<ChunkProjection> combinedChunks = new HashSet<>();

        try {
            // Using CompletableFuture to run searches in parallel
            java.util.concurrent.CompletableFuture<List<ChunkProjection>> vectorFuture = java.util.concurrent.CompletableFuture
                    .supplyAsync(() -> {
                        try {
                            String filtersJson = new com.fasterxml.jackson.databind.ObjectMapper()
                                    .writeValueAsString(plan.filters());
                            if (filtersJson.equals("{}")) {
                                return chunkRepository.findNearest(vectorString, 15);
                            } else {
                                return chunkRepository.findNearestWithFilters(vectorString, filtersJson, 15);
                            }
                        } catch (Exception e) {
                            log.error("Vector search failed", e);
                            return new ArrayList<>();
                        }
                    });

            java.util.concurrent.CompletableFuture<List<ChunkProjection>> keywordFuture = java.util.concurrent.CompletableFuture
                    .supplyAsync(() -> {
                        try {
                            return chunkRepository.findNearestKeyword(effectiveQuestion, 15);
                        } catch (Exception e) {
                            log.error("Keyword search failed", e);
                            return new ArrayList<>();
                        }
                    });

            // Wait for both to complete
            java.util.concurrent.CompletableFuture.allOf(vectorFuture, keywordFuture).join();

            combinedChunks.addAll(vectorFuture.get());
            combinedChunks.addAll(keywordFuture.get());

        } catch (Exception e) {
            log.warn("Search execution failed: {}", e.getMessage());
            // Fallback if critical failure, but usually we just proceed with what we have
        }

        log.info("Hybrid Search found {} unique candidates.", combinedChunks.size());

        // Reranking candidates
        List<String> candidates = combinedChunks.stream()
                .map(ChunkProjection::getContent)
                .collect(Collectors.toList());

        List<String> finalContextChunks;
        if (candidates.isEmpty()) {
            finalContextChunks = new ArrayList<>();
        } else {
            try {
                var rerankResponse = aiClient.rerank(effectiveQuestion, candidates);
                finalContextChunks = rerankResponse.results().stream()
                        .map(AIServiceClient.RerankResult::content)
                        .limit(10) // Optimize context window size
                        .collect(Collectors.toList());
                log.info("Reranking reduced {} candidates to top {}.", candidates.size(), finalContextChunks.size());
            } catch (Exception e) {
                log.error("Reranking failed, falling back to top 10 vector results: {}", e.getMessage());
                finalContextChunks = candidates.stream().limit(10).collect(Collectors.toList());
            }
        }

        // Generate response using LLM
        String context = finalContextChunks.stream()
                .collect(Collectors.joining("\n---\n"));
        log.debug("Calling AI Service for generation...");
        var ragResponse = aiClient.ask(effectiveQuestion, context);
        log.info("AI Service responded successfully.");

        // Dynamic Sources (Note: We lose source file info after Reranking as currently
        // implemented unless we map it back)
        // To fix this: RerankResult should include metadata or we map map content ->
        // ChunkProjection.
        // For now, let's map content back to ChunkProjection to get sources.
        List<String> sources = finalContextChunks.stream()
                .map(content -> combinedChunks.stream()
                        .filter(c -> c.getContent().equals(content))
                        .findFirst()
                        .map(c -> "📄 " + c.getSourceFile())
                        .orElse("Unknown Source"))
                .distinct()
                .collect(Collectors.toList());

        if (sources.isEmpty()) {
            sources.add("Internal Knowledge Base");
        }

        return new ChatResponse(ragResponse.answer(), sources);
    }
}
