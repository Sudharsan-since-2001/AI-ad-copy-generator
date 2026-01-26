import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Ad Copy Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class AdRequest(BaseModel):
    product_name: str
    description: str
    target_audience: str
    platform: str
    campaign_goal: str
    tone: str
    framework: str

class AdVariation(BaseModel):
    headline: str
    primary_text: str
    cta: str
    angle: str
    strength_score: float = Field(ge=0, le=10)
    score_explanation: str

class AudienceInsight(BaseModel):
    pain_points: List[str]
    emotional_triggers: List[str]
    objections: List[str]
    targeting_interests: List[str] = Field(description="Pages, Topics, Influencers, Skills")
    audience_match_score: int = Field(description="Estimated % match with target audience, 0-100")
    match_score_explanation: str = Field(description="Short reason for the score")
    demographics: str = Field(description="Age range and Career stage")
    behaviors: List[str] = Field(description="Key online behaviors or habits")

class ComplianceCheck(BaseModel):
    risk_level: str
    risk_score: int = Field(description="Risk probability percentage, 0-100")
    risk_score_explanation: str = Field(description="Short reason for the score")
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

# --- LOGIC ---
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPT_TEMPLATE = """
You are an expert digital marketing strategist with 10+ years of experience in audience targeting and ad copywriting. Analyze the following product and create comprehensive marketing intelligence.

**PRODUCT DESCRIPTION:**
Product: {product_name}
Description: {description}
Target Audience: {target_audience}

**CAMPAIGN PARAMETERS:**
- Goal: {campaign_goal}
- Framework: {framework}
- Platform: {platform}
- Tone: {tone}

---

## PART 1: DEEP AUDIENCE ANALYSIS

First, think deeply about who would genuinely benefit from this product. Then provide:

**Demographics:**
- Age Range: Be specific (e.g., "23-34" not just "18-35")
- Career Stage: What point are they at professionally?

**Psychographic Profile:**
- Pain Points (3): What keeps them up at night? What frustrates them daily? Be specific and visceral.
- Emotional Triggers (3): What emotions drive their purchase decisions? (Fear of missing out, desire for status, need for security, etc.)
- Common Objections (3): What makes them hesitate before buying? What doubts do they have?

**Behavioral Patterns (3):**
Consider their actual daily habits:
- What platforms do they use and when?
- How do they consume content? (scrolling, searching, binge-watching)
- What device do they primarily use?

**Targeting Interests (5):**
Be specific and actionable. Instead of "fitness," say "CrossFit, Joe Rogan podcast, Whoop fitness tracker, intermittent fasting, David Goggins."

**Audience Match Score:**
Analyze how well this product aligns with the audience's needs. Consider:
- How urgent is their pain point?
- How aware are they of solutions like this?
- How competitive is the market?
- How unique is this product's value proposition?

Based on this analysis, assign a precise match score (e.g., 67, 73, 91). Avoid round numbers like 80, 85, 90. Then explain in 2-3 sentences why you gave this specific score.

---

## PART 2: CAMPAIGN STRATEGY

Based on the goal "{campaign_goal}", adjust your approach:
- If Awareness: Use curiosity-driven hooks that make them want to learn more
- If Traffic: Lead with value and information, make clicking feel like a smart decision
- If Sales: Use urgency, social proof, and direct CTAs that demand action NOW

Apply the {framework} framework, but make it feel natural - don't just fill in a template.
Use a {tone} tone throughout.

---

## PART 3: AD VARIATIONS

Create 3 distinct ad copy variations. Each should feel genuinely different in approach:

**Variation 1: Emotional Appeal**
Lead with feelings, aspirations, or fears. Make them *feel* something before they think.

**Variation 2: Logical Appeal**  
Lead with facts, benefits, and rational reasons. Appeal to their smart, analytical side.

**Variation 3: Scarcity/Urgency**
Create FOMO. Make them feel they'll miss out if they don't act now.

For each variation:
- Headline (attention-grabbing, max 40 chars)
- Body copy (2-3 sentences, compelling and specific)
- Call-to-action (specific and action-oriented)

**SELF-CRITIQUE EACH VARIATION:**
Rate each ad honestly (0-10 scale). Calculate an overall strength_score as the average of these 4 dimensions:
- Clarity: Is the message instantly understandable?
- Emotional Pull: Does it make you *feel* something?
- Urgency: Does it create a reason to act now?
- CTA Strength: Is the call-to-action specific and compelling?

For the overall score, briefly explain your reasoning (1-2 sentences).

---

## PART 4: CHANNEL-SPECIFIC OPTIMIZATION

**WhatsApp Broadcast Message:**
Create a personal, conversational message (max 300 chars including emoji). Should feel like a message from a friend, not a brand.

**SMS Version:**
Ultra-concise version (max 160 chars). Every word counts.

---

## PART 5: COMPLIANCE & RISK ANALYSIS

Review your ad copy against {platform} policies. Look for:
- Exaggerated claims or misleading statements
- Prohibited content
- Missing disclosures
- Targeting violations
- Trademark or copyright concerns

**Risk Score:**
Calculate a specific risk percentage (e.g., 8, 23, 47). Avoid round numbers like 20, 25, 30. Consider:
- How aggressive is the language?
- Are there any gray-area claims?
- Could any targeting be seen as discriminatory?
- Does it comply with advertising standards?

Assign a precise risk score and explain in 2-3 sentences what specific elements contribute to this score.

**Risk Level:** Based on your risk_score, assign: "Low" (0-30), "Medium" (31-60), or "High" (61-100).

---

**OUTPUT FORMAT (STRICT JSON ONLY):**

{{
  "insights": {{
    "demographics": "Age XX-XX, [Career Stage]",
    "pain_points": ["...", "...", "..."],
    "emotional_triggers": ["...", "...", "..."],
    "objections": ["...", "...", "..."],
    "behaviors": ["...", "...", "..."],
    "targeting_interests": ["...", "...", "...", "...", "..."],
    "audience_match_score": 67,
    "match_score_explanation": "..."
  }},
  "variations": [
    {{
      "headline": "...",
      "primary_text": "...",
      "cta": "...",
      "angle": "Emotional",
      "strength_score": 7.5,
      "score_explanation": "..."
    }},
    {{
      "headline": "...",
      "primary_text": "...",
      "cta": "...",
      "angle": "Logical",
      "strength_score": 8.2,
      "score_explanation": "..."
    }},
    {{
      "headline": "...",
      "primary_text": "...",
      "cta": "...",
      "angle": "Scarcity",
      "strength_score": 9.1,
      "score_explanation": "..."
    }}
  ],
  "compliance": {{
    "risk_level": "Low",
    "risk_score": 23,
    "risk_score_explanation": "...",
    "issues": ["...", "..."],
    "suggestions": ["...", "..."]
  }},
  "channel_opt": {{
    "whatsapp": "...",
    "sms": "..."
  }}
}}

CRITICAL: Respond ONLY with valid JSON. No markdown, no backticks, no preamble. Just pure JSON.
"""

@app.post("/api/generate", response_model=AdResponse)
async def generate_ad(request: AdRequest):
    try:
        prompt = PROMPT_TEMPLATE.format(
            product_name=request.product_name,
            description=request.description,
            target_audience=request.target_audience,
            platform=request.platform,
            campaign_goal=request.campaign_goal,
            tone=request.tone,
            framework=request.framework
        )
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a world-class marketing engine. Return ONLY JSON. For all numeric scores, use precise specific numbers based on your analysis - never use common round numbers like 80, 85, 90, 20, 25."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.8
        )
        
        data = json.loads(completion.choices[0].message.content)
        return AdResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- UI TEMPLATE ---
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Copy Ad Generator</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;500;600;800&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #0a0a0c;
            --bg-card: #121216;
            --bg-inner: rgba(255, 255, 255, 0.03);
            --accent-purple: #9d4edd;
            --deep-purple: #7b2cbf;
            --glow-purple: #c77dff;
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
            --cyber-pink: #ff006e;
            --border-glow: rgba(157, 78, 221, 0.2);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-base);
            background-image: 
                radial-gradient(circle at 20% 30%, rgba(123, 44, 191, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 80% 70%, rgba(255, 0, 110, 0.03) 0%, transparent 40%);
            color: var(--text-main);
            min-height: 100vh; overflow-x: hidden;
            background-attachment: fixed;
        }
        
        .app-wrapper { display: flex; min-height: 100vh; padding: 1.2rem; gap: 1.2rem; }
        
        .sidebar {
            width: 380px; background: var(--bg-card); border: 1px solid rgba(255,255,255,0.05);
            border-radius: 28px; padding: 2.5rem 2rem;
            display: flex; flex-direction: column; overflow-y: auto;
            position: relative; box-shadow: 10px 0 40px rgba(0,0,0,0.5);
        }
        .sidebar::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(to right, transparent, var(--accent-purple), transparent);
        }

        .brand-cloud { margin-bottom: 3rem; text-align: center; }
        .brand-cloud h1 {
            font-family: 'Orbitron', sans-serif; font-size: 1.4rem; letter-spacing: 0.1em;
            background: linear-gradient(to right, #fff, var(--accent-purple));
            -webkit-background-clip: text; background-clip: text; color: transparent;
        }

        .section-lbl {
            font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.2em;
            color: var(--accent-purple); font-weight: 800; display: block; margin-bottom: 1.2rem;
        }

        .field-group { margin-bottom: 1.5rem; }
        .field-label { display: block; font-size: 0.7rem; color: var(--text-dim); margin-bottom: 0.5rem; font-weight: 600; text-transform: uppercase; }
        
        input, select, textarea {
            width: 100%; background: #16161c; border: 1px solid rgba(157, 78, 221, 0.1);
            border-radius: 12px; padding: 0.9rem 1.1rem; color: white; outline: none; transition: 0.3s;
            font-size: 0.9rem;
        }
        input:focus, select:focus, textarea:focus { 
            border-color: var(--accent-purple); 
            box-shadow: 0 0 15px rgba(157, 78, 221, 0.2);
            background: #1c1c24;
        }
        
        select { 
            appearance: none; 
            background-image: url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L6 6L11 1' stroke='%239d4edd' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E"); 
            background-repeat: no-repeat; 
            background-position: right 1.2rem center; 
        }

        /* Options Visibility Fix */
        select option {
            background-color: #121216;
            color: white;
            padding: 10px;
        }

        .btn-dream {
            margin-top: 1.5rem; background: linear-gradient(135deg, var(--deep-purple), var(--accent-purple));
            color: white; border: none; padding: 1.1rem; border-radius: 14px;
            font-weight: 800; text-transform: uppercase; letter-spacing: 0.15em;
            cursor: pointer; transition: 0.4s; box-shadow: 0 10px 20px rgba(123, 44, 191, 0.2);
            font-family: 'Orbitron', sans-serif;
            font-size: 0.8rem;
        }
        .btn-dream:hover { 
            transform: translateY(-3px); 
            filter: brightness(1.2);
            box-shadow: 0 15px 30px rgba(123, 44, 191, 0.4); 
        }
        .btn-dream:active { transform: translateY(-1px); }
        .btn-dream:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: none; }

        .canvas { flex: 1; overflow-y: auto; padding: 0.5rem; display: grid; grid-template-columns: repeat(12, 1fr); gap: 1.2rem; }
        .canvas::-webkit-scrollbar { width: 5px; }
        .canvas::-webkit-scrollbar-thumb { background: var(--bg-card); border-radius: 10px; }

        .main-header-card { 
            grid-column: span 12; display: flex; align-items: center; gap: 1.5rem; 
            padding: 1.5rem 2rem; background: var(--bg-card); border-radius: 20px;
            border-left: 4px solid var(--accent-purple);
        }
        .main-header-card .icon-box { background: var(--deep-purple); width: 45px; height: 45px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }

        .cyber-card {
            background: var(--bg-card); border-radius: 24px; padding: 2rem;
            border: 1px solid rgba(255,255,255,0.03); position: relative;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .blob-persona { grid-column: span 8; }
        .blob-audit { grid-column: span 4; }
        .blob-full { grid-column: span 12; }

        .card-header-lbl { font-size: 0.65rem; text-transform: uppercase; color: var(--text-dim); letter-spacing: 0.1em; margin-bottom: 0.5rem; display: block; }
        .card-title-lg { font-size: 1.5rem; font-weight: 800; margin-bottom: 2rem; color: #fff; }

        /* CIRCULAR CHART */
        .chart-container { position: relative; width: 140px; height: 140px; }
        .circular-chart { display: block; margin: 10px auto; max-width: 100%; max-height: 250px; }
        .circle-bg { fill: none; stroke: rgba(255,255,255,0.05); stroke-width: 3.8; }
        .circle { fill: none; stroke-width: 3.8; stroke-linecap: round; animation: progress 1s ease-out forwards; }
        @keyframes progress { 0% { stroke-dasharray: 0 100; } }

        .persona-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 2rem; }
        .persona-section { margin-bottom: 1.5rem; }
        
        .tag-pill {
            display: inline-block; padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.75rem; 
            background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
            margin: 0.3rem; color: var(--text-dim);
        }
        .tag-pill.purple { background: rgba(157, 78, 221, 0.1); border-color: rgba(157, 78, 221, 0.2); color: var(--accent-purple); }

        .ad-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2rem; }
        .ad-variation {
            background: #16161c; border-radius: 20px; padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.05); position: relative;
            display: flex; flex-direction: column;
        }
        .score-box {
            position: absolute; top: 1.2rem; right: 1.2rem;
            padding: 0.4rem 0.6rem; border-radius: 8px; font-size: 0.7rem; font-weight: 900;
            background: rgba(157, 78, 221, 0.2); color: var(--accent-purple); border: 1px solid var(--accent-purple);
        }

        .cta-btn-alt {
            margin-top: auto; padding: 1rem; border-radius: 12px; text-align: center;
            font-weight: 800; font-size: 0.8rem; background: rgba(157, 78, 221, 0.1);
            color: var(--accent-purple); border: 1px solid var(--border-glow);
        }


        .empty-state { grid-column: span 12; text-align: center; padding: 20vh 0; }
        .empty-state h2 { font-family: 'Orbitron'; font-size: 3rem; margin-bottom: 1rem; color: var(--text-dim); opacity: 0.5; }

        @media (max-width: 1250px) {
            .app-wrapper { flex-direction: column; min-height: auto; padding: 0.8rem; }
            .sidebar { width: 100% !important; border-radius: 20px; padding: 1.5rem 1.2rem; }
            .canvas { display: none; grid-template-columns: 1fr; padding: 0.5rem 0; gap: 1rem; align-items: start; }
            .blob-persona, .blob-audit, .blob-full { grid-column: span 1; }
            .persona-grid { grid-template-columns: 1fr; text-align: left; gap: 1rem; align-items: start; }
            .ad-grid { grid-template-columns: 1fr; align-items: start; }
            .chart-container { margin: 0; width: 120px; height: 120px; }
            .empty-state h2 { font-size: 1.8rem; padding: 10vh 0; }
            .cyber-card { padding: 1.2rem; border-radius: 18px; margin-bottom: 0.5rem; }
            .card-title-lg { font-size: 1.2rem; margin-bottom: 1.2rem; }
            .main-header-card { padding: 1rem 1.2rem; margin-bottom: 0.5rem; }
            .persona-section { margin-bottom: 1rem; }
        }

        @media (max-width: 600px) {
            .brand-cloud h1 { font-size: 1.1rem; }
            .sidebar { padding: 1.2rem 1rem; }
            .cyber-card { padding: 1.2rem 1rem; border-radius: 16px; }
            .tag-pill { padding: 0.4rem 0.8rem; font-size: 0.7rem; }
            .main-header-card { padding: 1rem; gap: 1rem; }
        }
    </style>
</head>
<body>
    <div class="app-wrapper">
        <aside class="sidebar">
            <div class="brand-cloud">
                <h1>AD COPY ENGINE</h1>
                <p style="font-size: 0.6rem; color: var(--accent-purple); letter-spacing: 0.3em; margin-top: 0.5rem;">AI-POWERED MARKETING</p>
            </div>
            
            <form id="adForm">
                <span class="section-lbl">Configuration</span>
                <div class="field-group">
                    <label class="field-label">Product Name</label>
                    <input type="text" id="product_name" placeholder="e.g. Zen Sleep Mask" required>
                </div>
                <div class="field-group">
                    <label class="field-label">Brief Description</label>
                    <textarea id="description" rows="3" placeholder="Core benefit..." required></textarea>
                </div>
                
                <span class="section-lbl">Strategy</span>
                <div class="field-group">
                    <label class="field-label">Target Audience</label>
                    <input type="text" id="target_audience" placeholder="e.g. Founders" required>
                </div>
                <div class="field-group">
                    <label class="field-label">Campaign Goal</label>
                    <select id="campaign_goal">
                        <option value="Awareness">Awareness</option>
                        <option value="Traffic" selected>Traffic</option>
                        <option value="Sales">Sales</option>
                    </select>
                </div>
                <div class="field-group">
                    <label class="field-label">Framework</label>
                    <select id="framework">
                        <option>AIDA</option><option>PAS</option><option>Problem-Solution</option><option>Urgency-Scarcity</option>
                    </select>
                </div>
                <div class="field-group">
                    <label class="field-label">Tone</label>
                    <select id="tone">
                        <option>Professional</option><option>Emotional</option><option>Urgent</option><option>Casual</option>
                    </select>
                </div>
                <button type="submit" class="btn-dream" id="submitBtn">Generate Assets</button>
            </form>
            <div id="errorMessage" style="color: var(--cyber-pink); margin-top: 1rem; font-size: 0.75rem; text-align: center;"></div>
        </aside>

        <main class="canvas" id="canvas">
            <div class="empty-state">
                <h2>READY FOR DEPLOYMENT</h2>
                <p style="color: var(--text-dim); font-size: 0.9rem;">Input variables to synthesize your ad campaign.</p>
            </div>
        </main>
    </div>

    <script>
        const form = document.getElementById('adForm');
        const canvas = document.getElementById('canvas');
        const submitBtn = document.getElementById('submitBtn');
        const errorMsg = document.getElementById('errorMessage');

        form.onsubmit = async (e) => {
            e.preventDefault();
            submitBtn.disabled = true;
            submitBtn.innerText = 'Synthesizing...';
            errorMsg.innerText = '';
            
            // Show and scroll to results area on mobile
            if (window.innerWidth <= 1100) {
                canvas.style.display = 'grid';
                canvas.scrollIntoView({ behavior: 'smooth' });
            }
            
            canvas.innerHTML = '<div class="empty-state"><h2>CORE SYNTHESIS IN PROGRESS...</h2></div>';

            const payload = {
                product_name: document.getElementById('product_name').value,
                description: document.getElementById('description').value,
                target_audience: document.getElementById('target_audience').value,
                platform: 'Meta (IG/FB)',
                campaign_goal: document.getElementById('campaign_goal').value,
                tone: document.getElementById('tone').value,
                framework: document.getElementById('framework').value
            };

            try {
                const res = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (!res.ok) throw new Error('Synthesis failure. Engine offline.');
                const data = await res.json();
                renderDashboard(data);
                scrollToResults();
            } catch (err) {
                errorMsg.innerText = err.message;
                canvas.innerHTML = '<div class="empty-state"><h2>Error</h2><p>' + err.message + '</p></div>';
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerText = 'Generate Assets';
            }
        };

        function renderDashboard(data) {
            console.log("Received Data:", data);
            console.log("Scores - Match:", data.insights.audience_match_score, "Risk:", data.compliance.risk_score);
            
            canvas.innerHTML = `
                <div class="main-header-card">
                    <div class="icon-box">📊</div>
                    <div>
                        <h2 style="font-family: 'Orbitron'; font-size: 1.1rem; letter-spacing: 0.1em;">MARKET INTELLIGENCE</h2>
                        <p style="font-size: 0.6rem; color: var(--accent-purple); letter-spacing: 0.15em;">DATA ANALYTICS</p>
                    </div>
                </div>

                <div class="cyber-card blob-persona">
                    <span class="card-header-lbl">Meta Visualization</span>
                    <h3 class="card-title-lg">Customer Persona Analysis</h3>
                    
                    <div class="persona-grid">
                        <div class="persona-details">
                            <div class="persona-section">
                                <span class="card-header-lbl">Demographics</span>
                                <div style="font-size: 1rem; font-weight: 800; color: var(--accent-purple);">${data.insights.demographics}</div>
                            </div>

                            <div class="persona-section">
                                <span class="card-header-lbl">Pain Points</span>
                                <div>${data.insights.pain_points.map(p => `<span class="tag-pill">${p}</span>`).join('')}</div>
                            </div>

                            <div class="persona-section">
                                <span class="card-header-lbl">Triggers</span>
                                <div>${data.insights.emotional_triggers.map(t => `<span class="tag-pill purple">${t}</span>`).join('')}</div>
                            </div>
                        </div>

                        <div class="persona-extra" style="text-align: center; background: rgba(0,0,0,0.2); border-radius: 20px; padding: 1.5rem;">
                            <span class="card-header-lbl">Interest Distribution</span>
                            <div style="display: flex; justify-content: center; margin: 1.5rem 0;">
                                <div class="chart-container">
                                    <svg viewBox="0 0 36 36" class="circular-chart">
                                        <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                                        <path class="circle" stroke="#9d4edd" stroke-dasharray="${data.insights.audience_match_score}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                                    </svg>
                                    <div style="position: absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-weight: 900; font-size: 1.2rem;">${data.insights.audience_match_score}%</div>
                                </div>
                                <div style="font-size: 0.7rem; color: var(--accent-purple); opacity:0.8; margin-top: 0.5rem; max-width: 150px; line-height: 1.4;">${data.insights.match_score_explanation}</div>
                            </div>
                            <div style="font-size: 0.65rem; color: var(--text-dim); line-height: 1.5;">Targeting Interests:<br>${data.insights.targeting_interests.join(', ')}</div>
                        </div>
                    </div>
                </div>

                <div class="cyber-card blob-audit">
                    <span class="card-header-lbl">Compliance Audit</span>
                    <h3 class="card-title-lg">Risk Assessment</h3>
                    
                    <div class="chart-container" style="margin: 0 auto 1.5rem;">
                        <svg viewBox="0 0 36 36" class="circular-chart">
                            <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                            <path class="circle" 
                                  stroke="${data.compliance.risk_score > 50 ? '#ff006e' : data.compliance.risk_score > 20 ? '#facc15' : '#4ade80'}" 
                                  stroke-dasharray="${data.compliance.risk_score}, 100" 
                                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                        </svg>
                        <div style="position: absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-weight: 900; font-size: 1.4rem; color: ${data.compliance.risk_score > 50 ? '#ff006e' : data.compliance.risk_score > 20 ? '#facc15' : '#4ade80'}">
                            ${data.compliance.risk_score}%
                        </div>
                    </div>
                    <div style="text-align: center; font-size: 0.7rem; color: ${data.compliance.risk_score > 50 ? '#ff006e' : data.compliance.risk_score > 20 ? '#facc15' : '#4ade80'}; opacity:0.9; margin-bottom: 1.5rem; line-height: 1.4; padding: 0 1rem;">
                        ${data.compliance.risk_score_explanation}
                    </div>
                    
                    <div style="background: rgba(0,0,0,0.2); border-radius: 12px; padding: 1rem;">
                        <span class="card-header-lbl">Strategic Notes</span>
                        <ul style="font-size: 0.75rem; color: var(--text-dim); list-style: none; padding: 0;">
                            ${data.compliance.suggestions.slice(0, 2).map(s => `<li style="margin-bottom: 0.5rem;">• ${s}</li>`).join('')}
                        </ul>
                    </div>
                </div>

                <div class="cyber-card blob-full">
                    <span class="card-header-lbl">Generation AI</span>
                    <h3 class="card-title-lg">Ad Copy Variations</h3>
                    
                    <div class="ad-grid">
                        ${data.variations.map(v => `
                            <div class="ad-variation">
                                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem;">
                                    <span class="card-header-lbl" style="color: var(--accent-purple); margin-bottom: 0;">${v.angle} ANGLE</span>
                                    <div style="display: flex; gap: 0.8rem; align-items: center;">
                                        <button class="copy-raw-btn" 
                                            style="background: none; border: none; cursor: pointer; color: var(--text-dim); font-size: 1.1rem; padding: 4px;" 
                                            data-headline="${v.headline.replace(/"/g, '&quot;')}"
                                            data-text="${v.primary_text.replace(/"/g, '&quot;')}"
                                            data-cta="${v.cta.replace(/"/g, '&quot;')}"
                                            onclick="handleCopyAd(this)" 
                                            title="Copy All">📋</button>
                                        <div class="score-box" style="position: static;">${v.strength_score}/10</div>
                                    </div>
                                </div>

                                <div class="ad-part" style="margin-bottom: 1.5rem;">
                                    <span class="card-header-lbl" style="font-size: 0.55rem; opacity: 0.6;">[ HEADLINE ]</span>
                                    <h4 style="font-size: 1.1rem; font-weight: 800; line-height: 1.3;">${v.headline}</h4>
                                </div>

                                <div class="ad-part" style="margin-bottom: 1.5rem; flex-grow: 1;">
                                    <span class="card-header-lbl" style="font-size: 0.55rem; opacity: 0.6;">[ PRIMARY TEXT ]</span>
                                    <p style="font-size: 0.85rem; color: var(--text-dim); line-height: 1.6;">${v.primary_text}</p>
                                </div>
                                
                                <div style="font-size: 0.7rem; color: var(--accent-purple); opacity:0.7; margin-bottom: 1.5rem; font-style: italic; background: rgba(157, 78, 221, 0.05); padding: 0.8rem; border-radius: 10px;">
                                    "${v.score_explanation}"
                                </div>

                                <div class="ad-part">
                                    <span class="card-header-lbl" style="font-size: 0.55rem; opacity: 0.6; margin-bottom: 0.4rem;">[ CALL TO ACTION ]</span>
                                    <div class="cta-btn-alt">${v.cta}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="cyber-card blob-full">
                    <span class="card-header-lbl">Distribution</span>
                    <h4 class="card-title-lg" style="margin-bottom: 1.5rem;">Direct Channel Optimization</h4>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                         <div style="background: rgba(0,0,0,0.2); border-radius: 16px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.03);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                <span class="card-header-lbl" style="margin-bottom: 0;">WhatsApp Broadcast</span>
                                <span style="font-size: 0.7rem; color: var(--accent-purple); cursor: pointer; font-weight: 800;" 
                                    data-content="${data.channel_opt.whatsapp.replace(/"/g, '&quot;')}"
                                    onclick='handleCopyRaw(this)'>COPY CONTENT</span>
                            </div>
                            <div style="font-size: 0.85rem; color: var(--text-dim); line-height: 1.6; font-family: 'Inter', sans-serif; white-space: pre-wrap;">${data.channel_opt.whatsapp}</div>
                         </div>
                         
                         <div style="background: rgba(0,0,0,0.2); border-radius: 16px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.03);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                <span class="card-header-lbl" style="margin-bottom: 0;">SMS Marketing</span>
                                <span style="font-size: 0.7rem; color: var(--accent-purple); cursor: pointer; font-weight: 800;" 
                                    data-content="${data.channel_opt.sms.replace(/"/g, '&quot;')}"
                                    onclick='handleCopyRaw(this)'>COPY CONTENT</span>
                            </div>
                            <div style="font-size: 0.85rem; color: var(--text-dim); line-height: 1.6; font-family: 'Inter', sans-serif; white-space: pre-wrap;">${data.channel_opt.sms}</div>
                         </div>
                    </div>
                </div>
            `;
        }

        window.handleCopyRaw = async (btn) => {
            const text = btn.getAttribute('data-content');
            try {
                await navigator.clipboard.writeText(text);
                const original = btn.innerText;
                btn.innerText = 'COPIED!';
                btn.style.color = '#4ade80';
                setTimeout(() => {
                    btn.innerText = original;
                    btn.style.color = '';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy: ', err);
            }
        };

        window.handleCopyAd = async (btn) => {
            const headline = btn.getAttribute('data-headline');
            const text = btn.getAttribute('data-text');
            const cta = btn.getAttribute('data-cta');
            const fullContent = `${headline}\n\n${text}\n\n${cta}`;
            try {
                await navigator.clipboard.writeText(fullContent);
                const original = btn.innerHTML;
                btn.innerHTML = '<span style="color: #4ade80; font-size: 0.9rem; font-weight: 800;">✅</span>';
                setTimeout(() => btn.innerHTML = original, 2000);
            } catch (err) {
                console.error('Failed to copy: ', err);
            }
        };

        // Scroll helper for mobile
        function scrollToResults() {
            if (window.innerWidth <= 1100) {
                setTimeout(() => {
                    canvas.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return HTML_CONTENT
