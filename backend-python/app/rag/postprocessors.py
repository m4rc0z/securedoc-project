from typing import List, Optional
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore, QueryBundle
from flashrank import Ranker, RerankRequest
import logging

logger = logging.getLogger("rag_postprocessor")

class FlashRankRerank(BaseNodePostprocessor):
    """
    Reranks nodes using FlashRank (Lite-weight cross-encoder).
    """
    model_name: str = "ms-marco-MiniLM-L-12-v2"
    top_n: int = 5
    _ranker: Optional[Ranker] = None

    def __init__(self, model_name: str = "ms-marco-MiniLM-L-12-v2", top_n: int = 5):
        super().__init__()
        self.model_name = model_name
        self.top_n = top_n
        self._ranker = Ranker(model_name=model_name, cache_dir="./ollama_data/flashrank")

    @classmethod
    def class_name(cls) -> str:
        return "FlashRankRerank"

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        
        if not nodes or not query_bundle:
            return nodes

        query = query_bundle.query_str
        
        # FlashRank expects: [{"id": 1, "text": "..."}]
        # We need to map back to original nodes
        
        input_data = []
        node_map = {}
        
        for i, node_with_score in enumerate(nodes):
            node_id = str(i) # Use index as temporary ID
            text = node_with_score.node.get_content()
            input_data.append({"id": node_id, "text": text, "meta": node_with_score.node.metadata})
            node_map[node_id] = node_with_score

        try:
            logger.info(f"Reranking {len(nodes)} nodes using FlashRank...")
            request = RerankRequest(query=query, passages=input_data)
            results = self._ranker.rerank(request)
            
            # Format: [{"id": "...", "score": 0.9, ...}]
            # Sort by score desc just in case
            results.sort(key=lambda x: x["score"], reverse=True)
            
            new_nodes = []
            for item in results[:self.top_n]:
                node_id = str(item["id"])
                score = float(item["score"])
                
                original_node = node_map.get(node_id)
                if original_node:
                    original_node.score = score
                    new_nodes.append(original_node)
            
            return new_nodes
            
        except Exception as e:
            logger.error(f"FlashRank failed: {e}")
            # Fallback to original nodes, maybe sliced
            return nodes[:self.top_n]
