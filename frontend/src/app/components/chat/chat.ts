import { Component } from '@angular/core';
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
  messages: Message[] = [];
  question = '';
  loading = false;

  constructor(private api: ApiService) { }

  sendMessage() {
    if (!this.question.trim()) return;

    const userQuestion = this.question;
    this.messages.push({ text: userQuestion, sender: 'user' });
    this.question = '';
    this.loading = true;

    this.api.chat(userQuestion).subscribe({
      next: (response: ChatResponse) => {
        this.messages.push({
          text: response.answer,
          sender: 'bot',
          sources: response.sources
        });
        this.loading = false;
      },
      error: (err) => {
        this.messages.push({ text: 'Error: Could not get response.', sender: 'bot' });
        this.loading = false;
        console.error(err);
      }
    });
  }
}
