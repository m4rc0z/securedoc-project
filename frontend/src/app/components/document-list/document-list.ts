import { Component, signal, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, Document } from '../../services/api';

@Component({
    selector: 'app-document-list',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-semibold text-gray-800">Document Management</h2>
        <button (click)="loadDocuments()" class="text-blue-600 hover:text-blue-800 text-sm">
          Refresh List
        </button>
      </div>

      <!-- Loading State -->
      <div *ngIf="loading()" class="text-center py-4 text-gray-500">
        Loading documents...
      </div>

      <!-- Empty State -->
      <div *ngIf="!loading() && documents().length === 0" class="text-center py-8 text-gray-500 bg-gray-50 rounded">
        No documents found. Upload a file to get started.
      </div>

      <!-- Document Table -->
      <div *ngIf="!loading() && documents().length > 0" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Filename</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr *ngFor="let doc of documents()" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ doc.filename }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                  {{ getDocType(doc) }}
                </span>
              </td>
               <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ doc.uploadDate | date:'mediumDate' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button 
                  (click)="deleteDocument(doc)" 
                  class="text-red-600 hover:text-red-900 bg-red-50 hover:bg-red-100 px-3 py-1 rounded transition-colors"
                  [disabled]="isDeleting(doc.id)">
                  {{ isDeleting(doc.id) ? 'Deleting...' : 'Delete' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
})
export class DocumentListComponent implements OnInit {
    private api = inject(ApiService);

    documents = signal<Document[]>([]);
    loading = signal<boolean>(false);
    deletingIds = signal<Set<string>>(new Set());

    ngOnInit() {
        this.loadDocuments();
    }

    loadDocuments() {
        this.loading.set(true);
        this.api.getDocuments().subscribe({
            next: (docs) => {
                this.documents.set(docs);
                this.loading.set(false);
            },
            error: (err) => {
                console.error('Failed to load documents:', err);
                this.loading.set(false);
            }
        });
    }

    deleteDocument(doc: Document) {
        if (!confirm(`Are you sure you want to delete "${doc.filename}"?`)) return;

        this.toggleDeleting(doc.id, true);

        this.api.deleteDocument(doc.id).subscribe({
            next: () => {
                // Remove from list locally
                this.documents.update(current => current.filter(d => d.id !== doc.id));
                this.toggleDeleting(doc.id, false);
            },
            error: (err) => {
                console.error('Failed to delete document:', err);
                alert('Failed to delete document.');
                this.toggleDeleting(doc.id, false);
            }
        });
    }

    private toggleDeleting(id: string, busy: boolean) {
        this.deletingIds.update(ids => {
            const newIds = new Set(ids);
            if (busy) newIds.add(id);
            else newIds.delete(id);
            return newIds;
        });
    }

    isDeleting(id: string): boolean {
        return this.deletingIds().has(id);
    }

    getDocType(doc: Document): string {
        if (!doc.metadata) return 'File';
        try {
            const meta = JSON.parse(doc.metadata);
            return meta.document_type || 'Unknown';
        } catch {
            return 'File';
        }
    }
}
