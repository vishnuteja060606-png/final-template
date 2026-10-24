from typing import List, Dict, Any
from app.services.interfaces.base_ner import BaseNERService
from app.schemas.advanced import NERExtractResponse, EntityItem

class MockNERService(BaseNERService):
    """
    Day 1 Working Stub for Member 3.
    Extracts canonical tools, skills, formats, and licenses using a baseline dictionary.
    """

    CANONICAL_TOOLS = {
        "runway": "Runway Gen-3 Alpha",
        "gen-3": "Runway Gen-3 Alpha",
        "midjourney": "Midjourney v6",
        "mj": "Midjourney v6",
        "kling": "Kling AI v1.5",
        "flux": "Flux.1 Dev",
        "comfyui": "ComfyUI Pipeline",
        "sora": "OpenAI Sora",
        "pika": "Pika Labs 1.0",
        "elevenlabs": "ElevenLabs Voice AI",
    }

    CANONICAL_FORMATS = {
        "16:9": "16:9 Widescreen",
        "9:16": "9:16 Vertical Reel",
        "1:1": "1:1 Square",
        "mp4": "MP4 Deliverable",
        "prores": "Apple ProRes 422HQ",
    }

    def extract_entities(self, text: str, source_type: str = "creator_claim") -> NERExtractResponse:
        t_lower = text.lower()
        tools: List[EntityItem] = []
        formats: List[EntityItem] = []
        skills: List[EntityItem] = []
        licensing: List[EntityItem] = []

        # Tool extraction
        for key, canonical in self.CANONICAL_TOOLS.items():
            if key in t_lower:
                tools.append(EntityItem(
                    category="tool",
                    raw_value=key,
                    canonical_value=canonical,
                    provenance=source_type,
                    confidence=0.95
                ))

        # Format extraction
        for key, canonical in self.CANONICAL_FORMATS.items():
            if key in t_lower:
                formats.append(EntityItem(
                    category="format",
                    raw_value=key,
                    canonical_value=canonical,
                    provenance=source_type,
                    confidence=0.98
                ))

        # Skill heuristics
        if "storyboard" in t_lower:
            skills.append(EntityItem(
                category="skill", raw_value="storyboard", canonical_value="AI Storyboarding",
                provenance=source_type, confidence=0.90
            ))
        if "prompt" in t_lower:
            skills.append(EntityItem(
                category="skill", raw_value="prompt", canonical_value="Prompt Engineering",
                provenance=source_type, confidence=0.92
            ))

        # Licensing heuristics
        if any(w in t_lower for w in ["commercial", "buyout", "rights"]):
            licensing.append(EntityItem(
                category="license", raw_value="commercial buyout",
                canonical_value="Full Commercial Buyout Rights",
                provenance=source_type, confidence=0.95
            ))

        return NERExtractResponse(
            tools=tools,
            skills=skills,
            styles=[],
            formats=formats,
            licensing=licensing,
            metadata={"source_length": len(text), "parser": "MockNER_Baseline"}
        )

    def normalize_to_canonical(self, category: str, raw_token: str) -> str:
        token_clean = raw_token.strip().lower()
        if category == "tool":
            return self.CANONICAL_TOOLS.get(token_clean, raw_token.strip().title())
        if category == "format":
            return self.CANONICAL_FORMATS.get(token_clean, raw_token.strip())
        return raw_token.strip().title()

    def persist_extracted_entities(
        self,
        entity_type: str,
        entity_id: int,
        extracted: NERExtractResponse
    ) -> None:
        # Stub: Concrete implementation will write to extracted_entities DB session
        pass
