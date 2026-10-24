from fastapi import APIRouter, Depends
from app.schemas.ai import AIBriefRequest, AIBriefResponse
from app.services.ai_service import ai_service
from app.models.user import User
from app.services.auth_service import get_current_user_optional

router = APIRouter(prefix="/api/ai", tags=["AI Brief Builder"])

@router.post("/brief-builder", response_model=AIBriefResponse)
async def generate_brief_ai(
    payload: AIBriefRequest,
    current_user: User | None = Depends(get_current_user_optional)
):
    """
    Generate a structured creative brief draft from a rough concept.
    Uses Groq if configured, with automatic fallback to intelligent template.
    Does not persist automatically; user can review and edit before saving as a brief.
    """
    # Augment with company context if user has a company profile
    context = payload.company_context
    if current_user and current_user.company_profile and not context:
        context = f"{current_user.company_profile.company_name} ({current_user.company_profile.industry or 'Advertising'})"

    req = AIBriefRequest(prompt=payload.prompt, company_context=context)
    return await ai_service.generate_brief(req)
