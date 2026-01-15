import { Pipe, PipeTransform } from '@angular/core';
import { marked } from 'marked';

@Pipe({
    name: 'markdown',
    standalone: true
})
export class MarkdownPipe implements PipeTransform {
    transform(value: string | null | undefined): string {
        if (!value) return '';
        // marked.parse returns a string or Promise<string>. 
        // Since we aren't using async extensions, it's synchronous.
        return marked.parse(value) as string;
    }
}
