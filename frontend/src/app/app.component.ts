import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { UploadComponent } from './components/upload/upload';
import { ChatComponent } from './components/chat/chat';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [CommonModule, UploadComponent, ChatComponent],
    template: `
    <div class="min-h-screen bg-gray-100 flex flex-col">
      <header class="bg-white shadow p-4">
        <h1 class="text-2xl font-bold text-center text-blue-900">SecureDoc Intelligence</h1>
      </header>
      <main class="flex-1 container mx-auto p-4 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-1">
          <app-upload></app-upload>
        </div>
        <div class="lg:col-span-2">
          <app-chat></app-chat>
        </div>
      </main>
      <footer class="bg-gray-200 text-center p-4 text-gray-500 text-sm">
        &copy; 2026 SecureDoc Intelligence
      </footer>
    </div>
  `
})
export class AppComponent {
    title = 'frontend';
}
