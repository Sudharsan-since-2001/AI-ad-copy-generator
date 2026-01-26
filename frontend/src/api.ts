export interface AdRequest {
  product_name: string;
  description: string;
  target_audience: string;
  platform: string;
  campaign_goal: string;
  tone: string;
  framework: string;
}

export interface AdVariation {
  headline: string;
  primary_text: string;
  cta: string;
  angle: string;
}

export interface AudienceInsight {
  pain_points: string[];
  emotional_triggers: string[];
  objections: string[];
  competitive_angle: string;
  key_selling_points: string[];
  recommended_keywords: string[];
  demographics: string;
  targeting_interests: string[];
  behaviors: string[];
}

export interface ComplianceCheck {
  risk_level: string;
  issues: string[];
  suggestions: string[];
}

export interface ChannelOptimization {
  whatsapp: string;
  sms: string;
}

export interface AdResponse {
  insights: AudienceInsight;
  variations: AdVariation[];
  compliance: ComplianceCheck;
  channel_opt: ChannelOptimization;
}

const API_URL = import.meta.env.PROD ? '/api' : 'http://localhost:8000';

export async function generateAds(data: AdRequest): Promise<AdResponse> {
  try {
    const response = await fetch(`${API_URL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      let errorMessage = 'Failed to generate ads';
      try {
        const error = await response.json();
        errorMessage = error.detail || error.message || errorMessage;
      } catch {
        errorMessage = `Server error: ${response.status} ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }

    const result = await response.json();
    return result;
  } catch (error: any) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Network error: Please check your connection and try again.');
  }
}
