package com.securedoc.backend.service;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@Service
public class PdfService {

    public String extractText(MultipartFile file) throws IOException {
        try (PDDocument document = PDDocument.load(file.getBytes())) {
            if (document.isEncrypted()) {
                throw new IOException("Encrypted PDFs are not supported");
            }
            PDFTextStripper stripper = new PDFTextStripper();
            return stripper.getText(document);
        }
    }
}
