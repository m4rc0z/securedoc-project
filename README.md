# SecureDoc Intelligence (Local RAG)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-production--ready-green)

**SecureDoc Intelligence** is a privacy-first RAG (Retrieval-Augmented Generation) system. It runs entirely on your local machine, ensuring sensitive documents never leave your secure environment.

## 🏗 System Architecture

We adhere to a strict **Separation of Concerns** principle:

| Component | Technology | Role |
|-----------|------------|------|
| **Core API** | Java (Spring Boot) | **The Orchestrator**. Manages business logic, user sessions, and security. |
| **AI Worker** | Python (FastAPI) | **The Brain**. Handles ingestion, embedding generation, and LLM orchestration. |
| **Data Store** | PostgreSQL | **Structured Data**. Stores users, chat history, and document metadata. |
| **Vector Store** | PostgreSQL (pgvector) | **Integrated Memory**. Vectors stored alongside data for consistency. |
| **Inference** | Ollama (Native) | **Intelligence**. Runs the Llama 3 model directly on Mac Metal (GPU) for maximum speed. |

### Architecture: Single Source of Truth

We use a **Single-Store Architecture**:

**PostgreSQL (with `pgvector`)**:
*   **Role**: The All-in-One Database.
*   **Why**: It stores both the application data (users, documents) and the vector embeddings (for AI search).
*   **Benefit**: Simplifies the stack. No need to manage a separate vector database. Data consistency is guaranteed (delete a doc = delete its vectors).
*   **Image**: We use `ankane/pgvector` to enable the `vector` extension.

### Network Flow (`extra_hosts` explained)
To achieve <10s inference on Mac, we bypass Docker's slow virtualization for the LLM.
1. **Ollama** runs natively on macOS (port 11434).
2. The **Python Container** connects to the host via `host.docker.internal`.
3. This "bridge" allows the containerized app to leverage the Mac's full GPU power.

## 🚀 Getting Started

### Prerequisites
1. **Docker Installed**: [Get Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. **Ollama Installed** (Mac):
   ```bash
   brew install ollama
   ollama serve
   ```
   *Keep this terminal window open!*

3. **Pull Model**:
   Open a new terminal and run:
   ```bash
   ollama pull llama3
   ```

### Installation
1. Clone the repository.
2. Start the application stack:
   ```bash
   docker compose up -d
   ```
3. Access the application:
   - **Frontend**: http://localhost:4200 (if running) / Backend: http://localhost:8081

## 🛠 Features
- **Semantic Chunking**: Intelligently splits text by meaning, not just character count.
- **Hybrid Search**: Combines Keyword Search (BM25) with Vector Search for best accuracy.
- **Reranking**: Uses a second AI pass to strictly filter irrelevant results.
- **Privacy First**: No data ever sent to OpenAI or Cloud APIs.

---
*Built for privacy. Powered by local AI.*
