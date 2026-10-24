import json
import logging
from app.config import settings
from app.schemas.ai import AIBriefRequest, AIBriefResponse

logger = logging.getLogger(__name__)

class AIService:
    @staticmethod
    def _generate_fallback_brief(prompt: str, company_context: str | None = None) -> AIBriefResponse:
        """
        Deterministic, high-quality brief generator when Groq is unavailable,
        unconfigured, or returns an error.
        """
        p_lower = prompt.lower()

        # Deduce content type and format
        if any(w in p_lower for w in ["video", "film", "commercial", "clip", "cinematic", "trailer"]):
            content_type = "Video"
            style = "Cinematic & Hyper-Realistic"
            aspect_ratio = "16:9"
            fmt = "MP4 (ProRes available upon request)"
            skills = "AI Video Generation, Prompt Engineering, Motion Design, Storyboarding, Color Grading"
            tools = "Runway Gen-3, Kling AI, Topaz Video AI, Adobe Premiere"
            spec = "AI Video & Generative Advertising"
        elif any(w in p_lower for w in ["animat", "cartoon", "anime", "motion"]):
            content_type = "Animation"
            style = "Stylized 3D / Anime Fusion"
            aspect_ratio = "16:9"
            fmt = "MP4"
            skills = "AI Animation, Character Consistency, Keyframing, Prompting"
            tools = "Runway, Pika Labs, Stable Diffusion, After Effects"
            spec = "AI Animation"
        elif any(w in p_lower for w in ["social", "tiktok", "reel", "short", "instagram"]):
            content_type = "Video"
            style = "High-Energy Social Hook"
            aspect_ratio = "9:16"
            fmt = "MP4"
            skills = "Short-form Video, Hook Pacing, Sound Design, AI Upscaling"
            tools = "Runway, Midjourney, CapCut, ElevenLabs"
            spec = "Social Media Creatives"
        else:
            content_type = "Image"
            style = "Studio Commercial Grade"
            aspect_ratio = "1:1"
            fmt = "PNG"
            skills = "Prompt Engineering, Lighting Control, Inpainting, Product Photography"
            tools = "Midjourney v6, Stable Diffusion XL, Flux, Photoshop"
            spec = "Generative Advertising & Graphics"

        title = f"AI {content_type} Campaign: {prompt[:40].strip()}..."
        description = (
            f"Production requirement based on: '{prompt}'. "
            f"The goal is to produce engaging, high-end {content_type.lower()} content showcasing creative "
            f"excellence with AI generation workflows. "
            f"{f'Brand Context: {company_context}' if company_context else ''}"
        )
        campaign_requirements = (
            f"1. Conceptual treatment and storyboard approval before generation.\n"
            f"2. Consistent character, brand colors, and high-fidelity output.\n"
            f"3. Full delivery in {aspect_ratio} ({fmt}) with source prompt documentation.\n"
            f"4. Two rounds of revision allowed."
        )

        return AIBriefResponse(
            title=title,
            description=description,
            campaign_requirements=campaign_requirements,
            content_type=content_type,
            style=style,
            format=fmt,
            aspect_ratio=aspect_ratio,
            commercial_use="Full Commercial Buyout",
            required_skills=skills,
            required_tools=tools,
            specialization=spec,
            budget_range="₹1,50,000 - ₹3,50,000",
            source="fallback_template",
            model_used="deterministic_expert_template"
        )

    @classmethod
    async def generate_brief(cls, request: AIBriefRequest) -> AIBriefResponse:
        """
        Calls Groq API with structured JSON output if configured,
        otherwise safely falls back to high quality deterministic template.
        Supports model fallback chain for resilience.
        """
        api_key = (request.api_key or settings.GROQ_API_KEY or "").strip()

        # Check if key is placeholder or empty
        if not api_key or api_key.startswith("your_") or "your_groq_api_key" in api_key:
            logger.info("GROQ_API_KEY not configured or placeholder. Using deterministic brief template.")
            return cls._generate_fallback_brief(request.prompt, request.company_context)

        system_prompt = (
            "You are an expert creative director specializing in AI-native advertising and media production. "
            "Turn the user's rough idea into a structured creative brief for hiring AI content creators. "
            "You MUST return ONLY valid JSON matching this schema: \n"
            "{\n"
            '  "title": "string",\n'
            '  "description": "string",\n'
            '  "campaign_requirements": "string",\n'
            '  "content_type": "Video | Animation | Image | Graphic",\n'
            '  "style": "string",\n'
            '  "format": "MP4 | PNG | JPG | WebM",\n'
            '  "aspect_ratio": "16:9 | 9:16 | 1:1 | 4:5",\n'
            '  "commercial_use": "Full Commercial Buyout | Online Only | Internal",\n'
            '  "required_skills": "comma-separated skills",\n'
            '  "required_tools": "comma-separated tools like Runway, Midjourney, Flux",\n'
            '  "specialization": "target creator specialization",\n'
            '  "budget_range": "e.g. ₹2,00,000 - ₹5,00,000"\n'
            "}"
        )

        user_content = f"Rough Concept: {request.prompt}\n"
        if request.company_context:
            user_content += f"Company / Brand Context: {request.company_context}\n"

        # Model hierarchy: request model -> settings model -> fallbacks
        candidate_models = []
        if request.model and request.model.strip():
            candidate_models.append(request.model.strip())
        if settings.GROQ_MODEL and settings.GROQ_MODEL not in candidate_models:
            candidate_models.append(settings.GROQ_MODEL)
        for fb in getattr(settings, "GROQ_FALLBACK_MODELS", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]):
            if fb not in candidate_models:
                candidate_models.append(fb)

        from groq import Groq
        client = Groq(api_key=api_key)

        last_error = None
        for model in candidate_models:
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7,
                    max_tokens=1000
                )

                raw_text = completion.choices[0].message.content
                parsed = json.loads(raw_text)

                return AIBriefResponse(
                    title=parsed.get("title", f"AI Campaign: {request.prompt[:30]}"),
                    description=parsed.get("description", request.prompt),
                    campaign_requirements=parsed.get("campaign_requirements", "High fidelity deliverables with revisions."),
                    content_type=parsed.get("content_type", "Video"),
                    style=parsed.get("style", "Cinematic"),
                    format=parsed.get("format", "MP4"),
                    aspect_ratio=parsed.get("aspect_ratio", "16:9"),
                    commercial_use=parsed.get("commercial_use", "Full Commercial Buyout"),
                    required_skills=parsed.get("required_skills", "AI Generation, Prompt Engineering"),
                    required_tools=parsed.get("required_tools", "Runway Gen-3, Midjourney"),
                    specialization=parsed.get("specialization", "AI Video"),
                    budget_range=parsed.get("budget_range", "₹2,00,000 - ₹5,00,000"),
                    source="groq",
                    model_used=model
                )

            except Exception as e:
                last_error = e
                logger.warning(f"Groq API call with model '{model}' failed: {str(e)}. Trying next model if available.")
                continue

        logger.warning(f"All Groq models failed. Last error: {last_error}. Using fallback deterministic brief.")
        return cls._generate_fallback_brief(request.prompt, request.company_context)

ai_service = AIService()
