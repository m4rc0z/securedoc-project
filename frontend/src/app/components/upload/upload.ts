import { Component } from '@angular/core';
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
  selectedFile: File | null = null;
  uploading = false;
  message = '';
  error = false;

  constructor(private api: ApiService) { }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  upload() {
    if (!this.selectedFile) return;

    this.uploading = true;
    this.message = '';
    this.error = false;

    this.api.uploadDocument(this.selectedFile).subscribe({
      next: (response) => {
        this.uploading = false;
        this.message = 'Upload successful!';
        this.selectedFile = null;
      },
      error: (err) => {
        this.uploading = false;
        this.error = true;
        this.message = 'Upload failed. Please try again.';
        console.error(err);
      }
    });
  }
}
