import math
import random
from typing import List, Dict, Any
from app.services.interfaces.base_embedding import BaseEmbeddingService

class MockEmbeddingService(BaseEmbeddingService):
    """
    Day 1 Working Stub for Member 2.
    Returns deterministic 384-dimensional normalized vectors and realistic similarity scores.
    """

    def generate_embedding(self, text: str) -> List[float]:
        if not text or not text.strip():
            return [0.0] * 384
        # Seed generator deterministically based on hash of text
        h = sum(ord(c) for c in text)
        rng = random.Random(h)
        raw = [rng.uniform(-1.0, 1.0) for _ in range(384)]
        norm = math.sqrt(sum(x * x for x in raw))
        return [x / norm for x in raw] if norm > 0 else raw

    def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self.generate_embedding(t) for t in texts]

    def compute_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        # Clamp to [0.0, 1.0] for cosine similarity
        return max(0.0, min(1.0, (dot + 1.0) / 2.0))

    def search_similar(
        self,
        query: str,
        entity_type: str = "creator",
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        # Return mock candidates so UI has immediate data
        return [
            {
                "entity_id": 1,
                "entity_type": entity_type,
                "similarity_score": 0.92,
                "headline": "Lead AI Filmmaker & Sora Specialist",
                "matched_tags": ["Runway Gen-3", "Cinematic", "16:9"]
            },
            {
                "entity_id": 2,
                "entity_type": entity_type,
                "similarity_score": 0.85,
                "headline": "3D Generative Animator & VFX Artist",
                "matched_tags": ["ComfyUI", "Kling AI", "Animation"]
            },
            {
                "entity_id": 3,
                "entity_type": entity_type,
                "similarity_score": 0.78,
                "headline": "Hyper-Realistic Commercial Media Director",
                "matched_tags": ["Midjourney v6", "Flux.1", "Commercial Buyout"]
            }
        ][:top_k]
