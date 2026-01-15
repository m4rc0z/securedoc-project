import { Routes } from '@angular/router';
import { ChatComponent } from './components/chat/chat';
import { DocumentListComponent } from './components/document-list/document-list';

export const routes: Routes = [
    { path: '', component: ChatComponent },
    { path: 'documents', component: DocumentListComponent }
];
