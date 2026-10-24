import re
import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.services.interfaces.base_ner import BaseNERService
from app.schemas.advanced import NERExtractResponse, EntityItem
from app.models.sidecar import ExtractedEntity

import os
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class CanonicalNERService(BaseNERService):
    """
    Hybrid Named Entity Recognition (NER) & Normalization Engine.
    Combines high-speed canonical dictionary matching with Groq LLM structured JSON extraction.
    Tracks provenance ('creator_claim' vs 'platform_verified' vs 'brief_requirement').
    """

    # Comprehensive canonical tool dictionary mapping aliases -> canonical name
    CANONICAL_TOOLS = {
        "runway": "Runway Gen-3 Alpha",
        "runway gen 3": "Runway Gen-3 Alpha",
        "runway gen-3": "Runway Gen-3 Alpha",
        "gen-3": "Runway Gen-3 Alpha",
        "gen 3": "Runway Gen-3 Alpha",
        "midjourney": "Midjourney v6",
        "midjourney v6": "Midjourney v6",
        "mj": "Midjourney v6",
        "mj v6": "Midjourney v6",
        "kling": "Kling AI v1.5",
        "kling ai": "Kling AI v1.5",
        "flux": "Flux.1 Dev",
        "flux.1": "Flux.1 Dev",
        "flux dev": "Flux.1 Dev",
        "flux schnell": "Flux.1 Schnell",
        "comfyui": "ComfyUI Pipeline",
        "comfy ui": "ComfyUI Pipeline",
        "sora": "OpenAI Sora",
        "openai sora": "OpenAI Sora",
        "pika": "Pika Labs 1.0",
        "pika labs": "Pika Labs 1.0",
        "elevenlabs": "ElevenLabs Voice AI",
        "eleven labs": "ElevenLabs Voice AI",
        "topaz": "Topaz Video AI",
        "topaz video ai": "Topaz Video AI",
        "luma": "Luma Dream Machine",
        "dream machine": "Luma Dream Machine",
        "stable diffusion": "Stable Diffusion XL",
        "sdxl": "Stable Diffusion XL",
        "suno": "Suno AI Music",
        "udio": "Udio AI Music",
        "premiere": "Adobe Premiere Pro",
        "after effects": "Adobe After Effects",
        "photoshop": "Adobe Photoshop",
    }

    CANONICAL_SKILLS = {
        "prompt engineering": "Prompt Engineering",
        "prompting": "Prompt Engineering",
        "storyboard": "AI Storyboarding",
        "storyboarding": "AI Storyboarding",
        "character consistency": "Character Consistency",
        "consistent characters": "Character Consistency",
        "motion design": "Motion Design",
        "camera control": "Camera Motion Control",
        "camera motion": "Camera Motion Control",
        "inpainting": "AI Inpainting & Outpainting",
        "outpainting": "AI Inpainting & Outpainting",
        "upscaling": "Spatial / Temporal Upscaling",
        "video upscaling": "Spatial / Temporal Upscaling",
        "lora": "LoRA Fine-Tuning & Training",
        "lora training": "LoRA Fine-Tuning & Training",
        "color grading": "Color Grading & Finishing",
        "sound design": "AI Sound Design & Voiceover",
    }

    CANONICAL_STYLES = {
        "cinematic": "Cinematic & Hyper-Realistic",
        "hyper-realistic": "Cinematic & Hyper-Realistic",
        "photorealistic": "Photorealistic Studio Quality",
        "anime": "Stylized Anime & Manga",
        "manga": "Stylized Anime & Manga",
        "3d": "3D CGI & VFX",
        "cartoon": "Stylized 2D Cartoon",
        "minimalist": "Clean Minimalist Commercial",
        "cyberpunk": "Cyberpunk / Sci-Fi Neon",
        "retro": "Retro Vintage Film Aesthetic",
    }

    CANONICAL_FORMATS = {
        "16:9": "16:9 Widescreen",
        "widescreen": "16:9 Widescreen",
        "horizontal": "16:9 Widescreen",
        "9:16": "9:16 Vertical Reel",
        "vertical": "9:16 Vertical Reel",
        "reel": "9:16 Vertical Reel",
        "tiktok": "9:16 Vertical Reel",
        "1:1": "1:1 Square",
        "square": "1:1 Square",
        "4:5": "4:5 Social Feed",
        "mp4": "MP4 Deliverable",
        "prores": "Apple ProRes 422HQ",
        "png": "Lossless PNG",
        "4k": "4K Ultra-HD",
        "1080p": "1080p Full-HD",
    }

    CANONICAL_LICENSES = {
        "commercial buyout": "Full Commercial Buyout Rights",
        "commercial": "Full Commercial Buyout Rights",
        "full commercial": "Full Commercial Buyout Rights",
        "buyout": "Full Commercial Buyout Rights",
        "non-exclusive": "Non-Exclusive Commercial License",
        "exclusivity": "Exclusive Commercial Buyout",
        "attribution": "Creative Commons with Attribution",
        "personal": "Personal / Non-Commercial Portfolio Only",
    }

    def normalize_to_canonical(self, category: str, raw_token: str) -> str:
        token_clean = raw_token.strip().lower()
        if category == "tool":
            return self.CANONICAL_TOOLS.get(token_clean, raw_token.strip().title())
        elif category == "skill":
            return self.CANONICAL_SKILLS.get(token_clean, raw_token.strip().title())
        elif category == "style":
            return self.CANONICAL_STYLES.get(token_clean, raw_token.strip().title())
        elif category == "format":
            return self.CANONICAL_FORMATS.get(token_clean, raw_token.strip())
        elif category == "license":
            return self.CANONICAL_LICENSES.get(token_clean, raw_token.strip().title())
        return raw_token.strip()

    def _extract_regex_entities(self, text: str, source_type: str) -> NERExtractResponse:
        t_lower = text.lower()
        tools: List[EntityItem] = []
        skills: List[EntityItem] = []
        styles: List[EntityItem] = []
        formats: List[EntityItem] = []
        licensing: List[EntityItem] = []
        metadata: Dict[str, Any] = {}

        # 1. Tools
        seen_tools = set()
        for alias, canonical in sorted(self.CANONICAL_TOOLS.items(), key=lambda x: len(x[0]), reverse=True):
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, t_lower) and canonical not in seen_tools:
                seen_tools.add(canonical)
                tools.append(EntityItem(
                    category="tool",
                    raw_value=alias,
                    canonical_value=canonical,
                    provenance=source_type,
                    confidence=0.96
                ))

        # 2. Skills
        seen_skills = set()
        for alias, canonical in sorted(self.CANONICAL_SKILLS.items(), key=lambda x: len(x[0]), reverse=True):
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, t_lower) and canonical not in seen_skills:
                seen_skills.add(canonical)
                skills.append(EntityItem(
                    category="skill",
                    raw_value=alias,
                    canonical_value=canonical,
                    provenance=source_type,
                    confidence=0.92
                ))

        # 3. Styles
        seen_styles = set()
        for alias, canonical in sorted(self.CANONICAL_STYLES.items(), key=lambda x: len(x[0]), reverse=True):
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, t_lower) and canonical not in seen_styles:
                seen_styles.add(canonical)
                styles.append(EntityItem(
                    category="style",
                    raw_value=alias,
                    canonical_value=canonical,
                    provenance=source_type,
                    confidence=0.90
                ))

        # 4. Formats & Aspect Ratios
        seen_formats = set()
        for alias, canonical in sorted(self.CANONICAL_FORMATS.items(), key=lambda x: len(x[0]), reverse=True):
            pattern = r'(?:\b|(?<=\s))' + re.escape(alias) + r'(?:\b|(?=\s))'
            if re.search(pattern, t_lower) and canonical not in seen_formats:
                seen_formats.add(canonical)
                formats.append(EntityItem(
                    category="format",
                    raw_value=alias,
                    canonical_value=canonical,
                    provenance=source_type,
                    confidence=0.98
                ))

        # 5. Licensing & Commercial Requirements
        seen_lic = set()
        for alias, canonical in sorted(self.CANONICAL_LICENSES.items(), key=lambda x: len(x[0]), reverse=True):
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, t_lower) and canonical not in seen_lic:
                seen_lic.add(canonical)
                licensing.append(EntityItem(
                    category="license",
                    raw_value=alias,
                    canonical_value=canonical,
                    provenance=source_type,
                    confidence=0.95
                ))

        # 6. Budget & Duration parsing via regex
        budget_match = re.search(r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?', text)
        if budget_match:
            metadata["budget_extracted"] = budget_match.group(0)

        duration_match = re.search(r'\b\d+\s*(?:s|sec|seconds|minute|min)\b', text, re.IGNORECASE)
        if duration_match:
            metadata["duration_extracted"] = duration_match.group(0)

        metadata["extraction_engine"] = "CanonicalRegex_Matcher"
        return NERExtractResponse(
            tools=tools,
            skills=skills,
            styles=styles,
            formats=formats,
            licensing=licensing,
            metadata=metadata
        )

    def extract_entities(self, text: str, source_type: str = "creator_claim") -> NERExtractResponse:
        """
        Primary NER extraction pipeline. Fast deterministic dictionary matcher
        augmented with Groq LLM if API key is active.
        """
        base_result = self._extract_regex_entities(text, source_type)

        # If Groq API key is configured, use Groq to extract additional subtle entities
        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                client = Groq(api_key=settings.GROQ_API_KEY)
                prompt = (
                    f"Extract AI creation entities from the following text into JSON.\n"
                    f"Categories: tools, skills, styles, formats, licensing.\n"
                    f"Text: '{text}'\n"
                    f"Return JSON strictly adhering to: {{\"tools\": [\"name\"], \"skills\": [\"name\"], \"styles\": [\"name\"], \"formats\": [\"name\"], \"licensing\": [\"name\"]}}"
                )
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a specialized AI creative entity extractor. Output valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    model= os.getenv("GROQ_MODEL"),
                    response_format={"type": "json_object"},
                    temperature=0.1,
                    max_tokens=500
                )
                data = json.loads(chat_completion.choices[0].message.content or "{}")

                # Merge Groq LLM entities with canonical normalization
                for t in data.get("tools", []):
                    canonical = self.normalize_to_canonical("tool", t)
                    if not any(item.canonical_value == canonical for item in base_result.tools):
                        base_result.tools.append(EntityItem(
                            category="tool", raw_value=t, canonical_value=canonical,
                            provenance=source_type, confidence=0.88
                        ))

                for s in data.get("skills", []):
                    canonical = self.normalize_to_canonical("skill", s)
                    if not any(item.canonical_value == canonical for item in base_result.skills):
                        base_result.skills.append(EntityItem(
                            category="skill", raw_value=s, canonical_value=canonical,
                            provenance=source_type, confidence=0.85
                        ))

                base_result.metadata["llm_augmented"] = True
            except Exception as e:
                logger.warning(f"Groq NER extraction fallback invoked due to error: {e}")
                base_result.metadata["llm_augmented"] = False

        return base_result

    def persist_extracted_entities(
        self,
        entity_type: str,
        entity_id: int,
        extracted: NERExtractResponse,
        db: Optional[Session] = None
    ) -> None:
        """Persists extracted entities into the extracted_entities sidecar table."""
        if db is None:
            return

        # Clear existing entities for this record to prevent duplicates
        db.query(ExtractedEntity).filter(
            ExtractedEntity.entity_type == entity_type,
            ExtractedEntity.entity_id == entity_id
        ).delete()

        all_items = (
            extracted.tools +
            extracted.skills +
            extracted.styles +
            extracted.formats +
            extracted.licensing
        )

        for item in all_items:
            db_entity = ExtractedEntity(
                entity_type=entity_type,
                entity_id=entity_id,
                category=item.category,
                raw_value=item.raw_value[:255],
                canonical_value=item.canonical_value[:255],
                provenance=item.provenance,
                confidence=item.confidence
            )
            db.add(db_entity)

        db.commit()

ner_service = CanonicalNERService()
