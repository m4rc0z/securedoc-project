import { Component, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, ChatResponse } from '../../services/api';

interface Message {
  text: string;
  sender: 'user' | 'bot';
  sources?: string[];
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css'
})
export class ChatComponent {
  private api = inject(ApiService);

  messages = signal<Message[]>([]);
  question = signal('');
  loading = signal(false);

  sendMessage() {
    const currentQuestion = this.question();
    if (!currentQuestion.trim()) return;

    // Optimistic Update
    this.messages.update(msgs => [...msgs, { text: currentQuestion, sender: 'user' }]);
    this.question.set('');
    this.loading.set(true);

    this.api.chat(currentQuestion).subscribe({
      next: (response: ChatResponse) => {
        this.messages.update(msgs => [...msgs, {
          text: response.answer,
          sender: 'bot',
          sources: response.sources
        }]);
        this.loading.set(false);
      },
      error: (err) => {
        this.messages.update(msgs => [...msgs, { text: 'Error: Could not get response.', sender: 'bot' }]);
        this.loading.set(false);
        console.error(err);
      }
    });
  }
}
