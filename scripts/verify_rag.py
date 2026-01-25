
import requests
import json
import os
from pypdf import PdfReader
import time

BASE_URL = "http://localhost:8000"
PDF_PATH = "pdfs/quick-faint-crayfish (3).pdf"

def main():
    print("--- RAG Verification Script ---")
    
    # 1. Reset Database
    print("\n1. Resetting Database...")
    try:
        resp = requests.post(f"{BASE_URL}/reset")
        resp.raise_for_status()
        print("   Database cleared.")
    except Exception as e:
        print(f"   Failed to reset: {e}")
        return

    # 2. Extract Text (Mimic Java Backend)
    print(f"\n2. Extracting text from {PDF_PATH}...")
    if not os.path.exists(PDF_PATH):
        print(f"   File not found! {os.path.abspath(PDF_PATH)}")
        return
        
    try:
        reader = PdfReader(PDF_PATH)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        print(f"   Extracted {len(text)} characters.")
    except Exception as e:
        print(f"   Extraction failed: {e}")
        return

    # 3. Ingest
    print("\n3. Ingesting to AI Service...")
    payload = {
        "text": text,
        "metadata": {"filename": "quick-faint-crayfish (3).pdf"}
    }
    try:
        resp = requests.post(f"{BASE_URL}/ingest", json=payload)
        resp.raise_for_status()
        print("   Ingestion successful.")
    except Exception as e:
        print(f"   Ingestion failed: {e}")
        return

    # 4. Verification Query
    question = "Wie lange arbeitet Marco bei Baloise?"
    print(f"\n4. Querying: {question}")
    
    # Wait a moment for indexing
    time.sleep(2)
    
    try:
        # Using context="" to force retrieval
        payload = {"question": question, "context": ""}
        resp = requests.post(f"{BASE_URL}/ask", json=payload)
        resp.raise_for_status()
        answer = resp.json().get("answer")
        sources = resp.json().get("sources")
        
        print("\n--- ANSWER ---")
        print(answer)
        print("\n--- SOURCES ---")
        print(sources)
        
    except Exception as e:
        print(f"   Query failed: {e}")

if __name__ == "__main__":
    main()
