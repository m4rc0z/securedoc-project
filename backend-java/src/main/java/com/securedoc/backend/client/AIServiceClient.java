package com.securedoc.backend.client;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.pgvector.PGvector;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.List;
import java.util.Map;

@Service
public class AIServiceClient {

    private final RestClient restClient;

    public AIServiceClient(@Value("${ai-service.url}") String aiServiceUrl) {
        var httpClient = java.net.http.HttpClient.newBuilder()
                .version(java.net.http.HttpClient.Version.HTTP_1_1)
                .connectTimeout(java.time.Duration.ofSeconds(60))
                .build();

        var factory = new org.springframework.http.client.JdkClientHttpRequestFactory(httpClient);
        factory.setReadTimeout(600000); // 10 minutes

        this.restClient = RestClient.builder()
                .baseUrl(aiServiceUrl)
                .requestFactory(factory)
                .build();
    }

    public IngestResponse ingest(String text, Map<String, Object> metadata) {
        IngestRequest request = new IngestRequest(text, metadata);
        return restClient.post()
                .uri("/ingest")
                .contentType(MediaType.APPLICATION_JSON)
                .body(request)
                .retrieve()
                .body(IngestResponse.class);
    }

    public EmbedResponse embed(String text) {
        return restClient.post()
                .uri("/embed")
                .contentType(MediaType.APPLICATION_JSON)
                .body(new EmbedRequest(text))
                .retrieve()
                .body(EmbedResponse.class);
    }

    public RAGResponse ask(String question, String context) {
        return restClient.post()
                .uri("/ask")
                .contentType(MediaType.APPLICATION_JSON)
                .body(new RAGRequest(question, context))
                .retrieve()
                .body(RAGResponse.class);
    }

    public PlanResponse plan(String question) {
        return restClient.post()
                .uri("/plan")
                .contentType(MediaType.APPLICATION_JSON)
                .body(new PlanRequest(question))
                .retrieve()
                .body(PlanResponse.class);
    }

    public RerankResponse rerank(String query, List<String> documents) {
        // top_k=5 hardcoded as per plan, or parameterize if needed
        return restClient.post()
                .uri("/rerank")
                .contentType(MediaType.APPLICATION_JSON)
                .body(new RerankRequest(query, documents, 5))
                .retrieve()
                .body(RerankResponse.class);
    }

    // DTOs
    public record IngestRequest(String text, Map<String, Object> metadata) {
    }

    public record EmbedRequest(String text) {
    }

    public record EmbedResponse(List<Float> embedding) {
        public PGvector getAsVector() {
            if (embedding == null)
                return null;
            float[] floats = new float[embedding.size()];
            for (int i = 0; i < embedding.size(); i++) {
                floats[i] = embedding.get(i);
            }
            return new PGvector(floats);
        }
    }

    public record RAGRequest(String question, String context) {
    }

    public record RAGResponse(String answer, List<String> sources) {
    }

    public record IngestResponse(@JsonProperty("document_metadata") Map<String, Object> documentMetadata,
            List<ChunkData> chunks) {
    }

    public record ChunkData(String content, List<Float> embedding, Map<String, Object> metadata) {
        public PGvector getEmbeddingAsVector() {
            // Convert List<Float> to PGvector compatible float[]
            if (embedding == null)
                return null;
            float[] floats = new float[embedding.size()];
            for (int i = 0; i < embedding.size(); i++) {
                floats[i] = embedding.get(i);
            }
            return new PGvector(floats);
        }
    }

    public record PlanRequest(String question) {
    }

    public record PlanResponse(
            @JsonProperty("original_question") String originalQuestion,
            @JsonProperty("rewritten_question") String rewrittenQuestion,
            String intent,
            Map<String, Object> filters) {
    }

    public record RerankRequest(String query, List<String> documents, @JsonProperty("top_k") int topK) {
    }

    public record RerankResponse(List<RerankResult> results) {
    }

    public record RerankResult(String content, double score) {
    }
}
