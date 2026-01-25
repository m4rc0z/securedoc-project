import logging
import os
from pathlib import Path
from llama_index.readers.docling import DoclingReader
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.schema import Document
from .factory import RAGFactory

logger = logging.getLogger("rag_ingestion")

class IngestionService:
    @staticmethod
    def process_file(file_path: str, metadata: dict = None):
        """
        Parses file and processes into hierarchical chunks.
        """
        try:
            # Parse document layout and content
            logger.info(f"Starting ingestion for {file_path}")
            reader = DoclingReader()
            docs = reader.load_data(file_path=file_path)
            
            logger.info(f"Parsed {len(docs)} document objects.")

            # Enrich with metadata
            base_metadata = metadata or {}
            for doc in docs:
                doc.metadata.update(base_metadata)
                doc.metadata["filename"] = base_metadata.get("filename", os.path.basename(file_path))
                # Filter out utility keys from embedding
                doc.excluded_embed_metadata_keys = ["filename", "page_label"]

            # Semantic Chunking for better context preservation
            embed_model = RAGFactory.get_embedding_model()
            node_parser = SemanticSplitterNodeParser(
                buffer_size=1, 
                breakpoint_percentile_threshold=95, 
                embed_model=embed_model
            )
            
            # Generate nodes
            nodes = node_parser.get_nodes_from_documents(docs)
            
            logger.info(f"Generated {len(nodes)} semantic chunks.")

            pipeline = IngestionPipeline(
                transformations=[embed_model],
                vector_store=RAGFactory.get_vector_store()
            )

            result_nodes = pipeline.run(nodes=nodes)
            
            logger.info(f"Ingestion complete. Processing complete.")
            return result_nodes

        except Exception as e:
            logger.error(f"Ingestion failed for {file_path}: {e}")
            raise e
        
    @staticmethod
    def process_text(text: str, metadata: dict = None):
        """
        Process raw text input.
        Bypasses Docling (as layout is lost), but applies Semantic Chunking and Embedding.
        """
        try:
            logger.info("Starting ingestion for raw text.")
            doc = Document(text=text, metadata=metadata or {})
            
            # Semantic Chunking & Embedding
            embed_model = RAGFactory.get_embedding_model()
            # Use Semantic Chunking for text as well for consistency
            node_parser = SemanticSplitterNodeParser(
                buffer_size=1, 
                breakpoint_percentile_threshold=95, 
                embed_model=embed_model
            )
            
            # Generate nodes
            nodes = node_parser.get_nodes_from_documents([doc])

            # Embed nodes
            for node in nodes:
                node.embedding = embed_model.get_text_embedding(node.get_content())
            
            logger.info(f"Text ingestion complete. Generated {len(nodes)} semantic chunks.")
            return nodes
            
        except Exception as e:
            logger.error(f"Text ingestion failed: {e}")
            raise e


