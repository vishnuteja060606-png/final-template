from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseEmbeddingService(ABC):
    """
    Abstract Interface for Semantic Embedding Generation and Vector Retrieval.
    Assigned to: Member 2
    Technology: Local FastEmbed (ONNX bge-small-en-v1.5) with SQLite Cosine Similarity
    """

    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate a 384-dimensional dense float vector for a given text snippet.
        Must handle empty strings and whitespace safely without raising uncaught exceptions.
        """
        pass

    @abstractmethod
    def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Batch generate embeddings efficiently for bulk indexing of creators, portfolios, and jobs.
        """
        pass

    @abstractmethod
    def compute_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """
        Compute cosine similarity between two normalized float vectors (range 0.0 to 1.0).
        """
        pass

    @abstractmethod
    def search_similar(
        self,
        query: str,
        entity_type: str = "creator",
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Convert query to embedding and retrieve the top_k most similar records from embedding_records.
        Returns a list of dicts with:
        {'entity_id': int, 'entity_type': str, 'similarity_score': float, 'headline': str, 'matched_tags': list}
        """
        pass
