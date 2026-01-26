from pydantic import BaseModel, Field
from typing import List, Optional

class AdRequest(BaseModel):
    product_name: str = Field(..., example="Silk Aura")
    description: str = Field(..., example="Hand-woven silk sarees for weddings")
    target_audience: str = Field(..., example="Women aged 25-45, wedding shoppers")
    platform: str = Field(..., example="Instagram") 
    campaign_goal: str = Field(..., example="Sales")
    tone: str = Field(..., example="Emotional")
    framework: str = Field(default="AIDA", example="PAS") # AIDA, PAS, Problem-Solution, Urgency-Scarcity

class AudienceInsight(BaseModel):
    pain_points: List[str]
    emotional_triggers: List[str]
    objections: List[str]
    competitive_angle: str = Field(..., description="How your product differs from alternatives")
    key_selling_points: List[str] = Field(..., description="Key selling points ranked by importance")
    recommended_keywords: List[str] = Field(..., description="Recommended keywords for this campaign")
    demographics: str = Field(..., description="Age range, gender, and location if applicable")
    targeting_interests: List[str] = Field(..., description="Specific interests for Meta and Google Ads targeting (e.g., 'Sustainable fashion', 'Vegan lifestyle', 'Ethical shopping')")
    behaviors: List[str] = Field(..., description="Online behaviors and purchase behaviors for ad targeting")

class AdVariation(BaseModel):
    headline: str
    primary_text: str
    cta: str
    angle: str # Emotional, Logical, Scarcity

class ComplianceCheck(BaseModel):
    risk_level: str # Low, Medium, High
    issues: List[str]
    suggestions: List[str]

class ChannelOptimization(BaseModel):
    whatsapp: str
    sms: str

class AdResponse(BaseModel):
    insights: AudienceInsight
    variations: List[AdVariation]
    compliance: ComplianceCheck
    channel_opt: ChannelOptimization
