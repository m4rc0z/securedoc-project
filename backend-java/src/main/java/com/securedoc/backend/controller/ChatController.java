package com.securedoc.backend.controller;

import com.securedoc.backend.dto.ChatRequest;
import com.securedoc.backend.dto.ChatResponse;
import com.securedoc.backend.service.ChatService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    @PostMapping
    public ResponseEntity<ChatResponse> chat(@RequestBody ChatRequest request) {
        System.out.println("Received chat request: " + request.question());
        return ResponseEntity.ok(chatService.chat(request));
    }
}
