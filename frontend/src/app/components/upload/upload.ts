import { Component, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './upload.html',
  styleUrl: './upload.css'
})
export class UploadComponent {
  private api = inject(ApiService);

  selectedFile = signal<File | null>(null);
  uploading = signal(false);
  message = signal('');
  error = signal(false);

  onFileSelected(event: any) {
    this.selectedFile.set(event.target.files[0]);
  }

  upload() {
    const file = this.selectedFile();
    if (!file) return;

    this.uploading.set(true);
    this.message.set('');
    this.error.set(false);

    this.api.uploadDocument(file).subscribe({
      next: (response) => {
        this.uploading.set(false);
        this.message.set('Upload successful!');
        this.selectedFile.set(null);
      },
      error: (err) => {
        this.uploading.set(false);
        this.error.set(true);
        this.message.set('Upload failed. Please try again.');
        console.error(err);
      }
    });
  }
}
