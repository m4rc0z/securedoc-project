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
            logger.info(f"Starting ingestion for {file_path}")
            
            # 1. Parsing with Docling
            # DoclingReader automatically handles layout and table extraction
            reader = DoclingReader()
            # Loading file
            docs = reader.load_data(file_path=file_path)
            
            logger.info(f"Docling parsed {len(docs)} document objects.")

            # 2. Enrich Metadata
            # Ensure every doc has the base metadata
            base_metadata = metadata or {}
            for doc in docs:
                doc.metadata.update(base_metadata)
                # Ensure essential keys
                doc.metadata["filename"] = base_metadata.get("filename", os.path.basename(file_path))
                doc.excluded_embed_metadata_keys = ["filename", "page_label"] # Don't embed filename, but keep for filtering

            # 3. Hierarchical Chunking
            # Create Parent (1024), Child (256/128) hierarchy.
            from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
            
            # 1024 tokens ~ 4k chars, 256 ~ 1k chars
            node_parser = HierarchicalNodeParser.from_defaults(
                chunk_sizes=[1024, 256, 128]
            )
            
            # Generate all nodes (parents + children)
            nodes = node_parser.get_nodes_from_documents(docs)
            leaf_nodes = get_leaf_nodes(nodes)
            
            logger.info(f"Generated {len(nodes)} hierarchical nodes ({len(leaf_nodes)} leaves).")

            # 4. Pipeline Execution
            # We need to store everything in the Docstore (which Qdrant serves as if we add all nodes)
            # But for Parent-Retriever to work, we verify that the Vector Store contains the parents map.
            
            pipeline = IngestionPipeline(
                transformations=[
                    RAGFactory.get_embedding_model(), 
                    # For RAG, we search leaves (small) and retrieve parents (big).
                    # So we embed leaves mostly, but storing all is safer for Qdrant flexible retrieval.
                ],
                vector_store=RAGFactory.get_vector_store()
            )

            # Important: Hierarchical retrieval needs a storage where we can look up parents by ID.
            # QdrantVectorStore handles nodes.
            result_nodes = pipeline.run(nodes=nodes)
            
            logger.info(f"Ingestion complete. Stored {len(result_nodes)} nodes in Qdrant.")
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
            splitter = SemanticSplitterNodeParser(
                buffer_size=1, 
                breakpoint_percentile_threshold=95, 
                embed_model=embed_model
            )
            
            pipeline = IngestionPipeline(
                transformations=[splitter, embed_model],
                vector_store=RAGFactory.get_vector_store()
            )
            
            nodes = pipeline.run(documents=[doc])
            logger.info(f"Text ingestion complete. Stored {len(nodes)} nodes in Qdrant.")
            return nodes
            
        except Exception as e:
            logger.error(f"Text ingestion failed: {e}")
            raise e


