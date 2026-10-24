from pydantic import BaseModel, Field

class AIBriefRequest(BaseModel):
    prompt: str = Field(..., min_length=5, description="Rough creative concept or project idea")
    company_context: str | None = Field(None, description="Optional company brand or industry context")
    api_key: str | None = Field(None, description="Optional Groq API key override")
    model: str | None = Field(None, description="Optional Groq model name")

class AIBriefResponse(BaseModel):
    title: str = Field(..., description="Generated project title")
    description: str = Field(..., description="Comprehensive creative overview")
    campaign_requirements: str = Field(..., description="Detailed campaign deliverables and goals")
    content_type: str = Field("Video", description="Video, Animation, Image, Graphic, 3D")
    style: str = Field("Cinematic", description="Visual style direction")
    format: str = Field("MP4", description="Preferred output format")
    aspect_ratio: str = Field("16:9", description="16:9, 9:16, 1:1, etc.")
    commercial_use: str = Field("Full Commercial Buyout", description="Licensing terms")
    required_skills: str = Field(..., description="Comma-separated AI creative skills")
    required_tools: str = Field(..., description="Comma-separated recommended AI tools/models")
    specialization: str = Field(..., description="Target creator specialization")
    budget_range: str | None = Field("$2,000 - $5,000", description="Estimated budget range")
    source: str = Field("groq", description="'groq' or 'fallback_template'")
    model_used: str | None = Field(None, description="Model used to generate brief")
