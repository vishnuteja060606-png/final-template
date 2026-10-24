"""
Advanced Service Container: Single-source dependency injection container.
Wires concrete services: SemanticEmbeddingService, CanonicalNERService, DeterministicRankingService, GroundedRAGService.
"""

from app.services.interfaces.base_embedding import BaseEmbeddingService
from app.services.interfaces.base_ner import BaseNERService
from app.services.interfaces.base_ranking import BaseRankingService
from app.services.interfaces.base_rag import BaseRAGService

from app.services.embedding_service import embedding_service
from app.services.ner_service import ner_service
from app.services.ranking_service import ranking_service
from app.services.rag_service import rag_service

class ServiceContainer:
    def __init__(self):
        # Initialized with concrete services
        self.embedding_service: BaseEmbeddingService = embedding_service
        self.ner_service: BaseNERService = ner_service
        self.ranking_service: BaseRankingService = ranking_service
        self.rag_service: BaseRAGService = rag_service

    def set_embedding_service(self, service: BaseEmbeddingService):
        self.embedding_service = service

    def set_ner_service(self, service: BaseNERService):
        self.ner_service = service

    def set_ranking_service(self, service: BaseRankingService):
        self.ranking_service = service

    def set_rag_service(self, service: BaseRAGService):
        self.rag_service = service

container = ServiceContainer()
