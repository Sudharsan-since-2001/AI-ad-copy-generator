import os
import json
from groq import Groq
from dotenv import load_dotenv
from .models import AdRequest, AdResponse

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

v2_PROMPT_TEMPLATE = """
You are an expert Marketing Strategist and Ad Copywriter. Your goal is to generate a comprehensive ad campaign suite.

### INPUT DATA:
- **Product:** {product_name}
- **Description:** {description}
- **Audience:** {target_audience}
- **Platform:** {platform}
- **Goal:** {campaign_goal}
- **Tone:** {tone}
- **Framework:** {framework}

### YOUR TASK:
Follow these steps to generate the output:

1. **Audience Analysis**: identify 3 key pain points, 3 emotional triggers, and 3 common objections for this specific audience and product.
2. **Target Audience Targeting**: Create detailed targeting information for Meta (Facebook/Instagram) and Google Ads:
   - Demographics: Provide specific age range, gender, and location (if applicable). Be specific (e.g., "25-45, Female, Urban areas").
   - Targeting Interests: Generate 8-12 specific interests that can be used in Meta and Google Ads. These should be actual interest categories available in ad platforms (e.g., "Sustainable fashion", "Vegan lifestyle", "Ethical shopping", "Eco-friendly products", "Fashion accessories", "Online shopping", "Luxury brands", "Wedding planning").
   - Behaviors: List 5-7 online behaviors and purchase behaviors (e.g., "Frequent online shoppers", "Engages with fashion content", "Purchases luxury items", "Follows sustainable brands").
3. **Competitive Analysis**: Analyze how this product differs from alternatives in the market. What makes it unique? What's the competitive angle?
4. **Key Selling Points**: Identify and rank 5-7 key selling points by importance (most important first). These should be the core benefits that drive purchase decisions.
5. **Keyword Research**: Generate 8-12 recommended keywords for this campaign. Include a mix of broad, specific, and long-tail keywords relevant to the product and audience.
6. **Apply Framework**: Use the {framework} framework to structure the ad copies.
   - AIDA (Attention, Interest, Desire, Action)
   - PAS (Problem, Agitation, Solution)
   - Problem-Solution
   - Urgency-Scarcity
7. **A/B Testing Variants**: Generate 3 distinct variations with different hooks (Emotional, Logical, Scarcity).
8. **Channel Optimization**: Convert the primary copy into a highly engaging WhatsApp broadcast message (with emojis) and a concise SMS (max 160 chars).
9. **Compliance Audit**: Perform a safety check for overpromising claims or sensitive language based on {platform} policies.

### OUTPUT FORMAT (STRICT JSON ONLY):
{{
    "insights": {{
        "pain_points": ["...", "...", "..."],
        "emotional_triggers": ["...", "...", "..."],
        "objections": ["...", "...", "..."],
        "competitive_angle": "A clear explanation of how this product differs from alternatives (2-3 sentences)",
        "key_selling_points": ["Most important benefit first", "Second most important", "...", "..."],
        "recommended_keywords": ["keyword1", "keyword2", "...", "..."],
        "demographics": "Age range, gender, location (e.g., '25-45, Female, Urban areas')",
        "targeting_interests": ["Interest 1 (for Meta/Google Ads)", "Interest 2", "...", "..."],
        "behaviors": ["Behavior 1", "Behavior 2", "...", "..."]
    }},
    "variations": [
        {{
            "headline": "...",
            "primary_text": "...",
            "cta": "...",
            "angle": "Emotional"
        }},
        {{
            "headline": "...",
            "primary_text": "...",
            "cta": "...",
            "angle": "Logical"
        }},
        {{
            "headline": "...",
            "primary_text": "...",
            "cta": "...",
            "angle": "Scarcity"
        }}
    ],
    "compliance": {{
        "risk_level": "Low/Medium/High",
        "issues": ["..."],
        "suggestions": ["..."]
    }},
    "channel_opt": {{
        "whatsapp": "...",
        "sms": "..."
    }}
}}
"""

async def generate_ad_copies(request: AdRequest) -> AdResponse:
    prompt = v2_PROMPT_TEMPLATE.format(
        product_name=request.product_name,
        description=request.description,
        target_audience=request.target_audience,
        platform=request.platform,
        campaign_goal=request.campaign_goal,
        tone=request.tone,
        framework=request.framework
    )
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a world-class marketing engine. Return ONLY JSON. Make sure to include ALL required fields in the insights object: pain_points, emotional_triggers, objections, competitive_angle, key_selling_points, recommended_keywords, demographics, targeting_interests, and behaviors."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = completion.choices[0].message.content
        data = json.loads(content)
        
        # Ensure all required fields are present with fallbacks
        if "insights" not in data:
            data["insights"] = {}
        
        insights = data["insights"]
        if "competitive_angle" not in insights or not insights["competitive_angle"]:
            insights["competitive_angle"] = "This product offers unique value through its distinctive features and benefits."
        if "key_selling_points" not in insights or not insights["key_selling_points"]:
            insights["key_selling_points"] = ["Core benefit 1", "Core benefit 2", "Core benefit 3"]
        if "recommended_keywords" not in insights or not insights["recommended_keywords"]:
            insights["recommended_keywords"] = ["keyword1", "keyword2", "keyword3"]
        if "demographics" not in insights or not insights.get("demographics"):
            insights["demographics"] = "25-45, All genders"
        if "targeting_interests" not in insights or not insights.get("targeting_interests") or len(insights.get("targeting_interests", [])) == 0:
            insights["targeting_interests"] = ["Online shopping", "Fashion", "Lifestyle"]
        if "behaviors" not in insights or not insights.get("behaviors") or len(insights.get("behaviors", [])) == 0:
            insights["behaviors"] = ["Frequent online shoppers", "Engages with brand content"]
        
        try:
            return AdResponse(**data)
        except Exception as validation_error:
            # Log the validation error for debugging
            error_details = f"Validation error: {str(validation_error)}\nData keys: {list(data.keys())}\nInsights keys: {list(insights.keys()) if 'insights' in data else 'No insights'}"
            raise ValueError(f"Failed to validate response: {str(validation_error)}. {error_details}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error generating ad copies: {str(e)}")
