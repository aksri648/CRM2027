from openai import OpenAI
from app.core.config import settings
from typing import Optional, List, Dict, Any


class AIService:
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.KIMCHI_BASE_URL,
            api_key=settings.KIMCHI_API_KEY
        )
        self.model = settings.AI_MODEL
    
    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Natural language chat interface"""
        system_prompt = """You are an AI assistant for Xeno Mini CRM, a marketing and engagement platform.
You help marketers:
- Understand their customer data
- Create and optimize campaigns
- Build audience segments
- Analyze campaign performance

Be helpful, concise, and actionable in your responses."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            context_str = f"\n\nContext: {json.dumps(context)}"
            messages.append({"role": "system", "content": context_str})
        
        messages.append({"role": "user", "content": message})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def suggest_segment(self, goal: str, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest a segment based on a marketing goal"""
        prompt = f"""Based on this marketing goal: {goal}

And this customer data summary:
- Total customers: {customer_data.get('total_customers', 0)}
- Average order value: ₹{customer_data.get('avg_order_value', 0)}
- Top cities: {', '.join(customer_data.get('top_cities', [])[:5])}
- Top products: {', '.join(customer_data.get('top_products', [])[:5])}

Suggest a segment definition with:
1. A name for the segment
2. The rules (field, operator, value format)
3. Why this segment would be valuable for the goal

Return as JSON with keys: name, description, rules (array of {{field, operator, value}})."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        import json
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {"error": "Could not parse AI response"}
    
    def generate_message_variants(self, campaign_goal: str, audience: str, count: int = 3) -> List[str]:
        """Generate message variants for a campaign"""
        prompt = f"""Generate {count} message variants for a marketing campaign.

Campaign goal: {campaign_goal}
Target audience: {audience}

Requirements:
- Each message should be concise (under 160 characters for SMS, or a compelling email subject line)
- Use personalisation tokens where appropriate: {{first_name}}, {{city}}
- Vary the tone and approach
- Make them actionable

Return as a JSON array of strings."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=500
        )
        
        import json
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return ["Thank you for being a valued customer!", "Special offer just for you!", "We miss you!"]
    
    def suggest_channel(self, customer_data: Dict[str, Any]) -> str:
        """Suggest the best channel for a customer"""
        prompt = f"""Based on this customer data:
- Email: {customer_data.get('email', 'N/A')}
- Phone: {customer_data.get('phone', 'N/A')}
- Preferred channel: {customer_data.get('preferred_channel', 'unknown')}
- Engagement score: {customer_data.get('engagement_score', 0)}
- Last engaged: {customer_data.get('last_engaged_at', 'unknown')}

Suggest the best channel (email, sms, whatsapp, or rcs) for reaching this customer.
Consider:
- If they have email but no phone, suggest email
- If they have high engagement, they might prefer their preferred channel
- SMS has higher open rates but email is better for detailed content

Return just the channel name as a string."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=50
        )
        
        return response.choices[0].message.content.strip().lower()
    
    def analyze_campaign_performance(self, campaign_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Provide AI-powered insights on campaign performance"""
        prompt = f"""Analyze this campaign performance data:

- Sent: {campaign_stats.get('sent_count', 0)}
- Delivered: {campaign_stats.get('delivered_count', 0)} ({campaign_stats.get('delivered_rate', 0)*100:.1f}%)
- Opened: {campaign_stats.get('opened_count', 0)} ({campaign_stats.get('opened_rate', 0)*100:.1f}%)
- Clicked: {campaign_stats.get('clicked_count', 0)} ({campaign_stats.get('clicked_rate', 0)*100:.1f}%)
- Converted: {campaign_stats.get('converted_count', 0)} ({campaign_stats.get('converted_rate', 0)*100:.1f}%)
- Revenue: ₹{campaign_stats.get('revenue', 0)}

Provide:
1. A brief performance summary (1-2 sentences)
2. Key strengths
3. Areas for improvement
4. Recommendations for next campaign

Return as JSON with keys: summary, strengths (array), improvements (array), recommendations (array)."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        
        import json
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {"summary": "Could not analyze campaign performance"}


import json

ai_service = AIService()