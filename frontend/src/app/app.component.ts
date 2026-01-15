import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { UploadComponent } from './components/upload/upload';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, UploadComponent],
  template: `
    <div class="min-h-screen bg-gray-100 flex flex-col">
      <header class="bg-white shadow p-4">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold text-blue-900">SecureDoc Intelligence</h1>
            <nav class="flex space-x-4">
                <a routerLink="/" 
                   routerLinkActive="text-blue-600 border-b-2 border-blue-600" 
                   [routerLinkActiveOptions]="{exact: true}"
                   class="px-3 py-2 text-gray-600 hover:text-blue-600 font-medium transition-colors">
                   Chat
                </a>
                <a routerLink="/documents" 
                   routerLinkActive="text-blue-600 border-b-2 border-blue-600" 
                   class="px-3 py-2 text-gray-600 hover:text-blue-600 font-medium transition-colors">
                   Documents
                </a>
            </nav>
        </div>
      </header>
      <main class="flex-1 container mx-auto p-4 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-1">
          <app-upload></app-upload>
        </div>
        <div class="lg:col-span-2">
            <!-- Router Outlet handles Chat / Documents switch -->
            <router-outlet></router-outlet>
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
