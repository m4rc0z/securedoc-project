import { Injectable, signal } from '@angular/core';
import { Client, Message, IFrame } from '@stomp/stompjs';
import SockJS from 'sockjs-client';

@Injectable({
    providedIn: 'root'
})
export class WebSocketService {
    private client: Client;

    // Signal to emit ingestion updates
    ingestionUpdates = signal<any>(null);

    constructor() {
        console.log('🚀 WebSocketService: Initializing with SockJS...');
        const url = `${window.location.protocol}//${window.location.host}/ws`;
        console.log('🔗 WebSocketService: Target SockJS URL:', url);

        this.client = new Client({
            // For SockJS, we use webSocketFactory instead of brokerURL
            webSocketFactory: () => new SockJS(url),
            reconnectDelay: 5000,
            heartbeatIncoming: 4000,
            heartbeatOutgoing: 4000,
            debug: (str) => {
                console.log('🛠 STOMP Debug:', str);
            }
        });

        this.client.onConnect = (frame: IFrame) => {
            console.log('✅ Connected to WebSocket');
            this.client.subscribe('/topic/ingestion-status', (message: Message) => {
                if (message.body) {
                    console.log('📬 Received ingestion status update:', message.body);
                    this.ingestionUpdates.set(JSON.parse(message.body));
                }
            });
        };

        this.client.onStompError = (frame: IFrame) => {
            console.error('❌ STOMP error:', frame);
        };

        this.client.onWebSocketClose = () => {
            console.warn('⚠️ WebSocket connection closed');
        };

        this.client.onWebSocketError = (error) => {
            console.error('❌ WebSocket error:', error);
        };

        this.client.activate();
    }
}
