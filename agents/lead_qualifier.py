from groq import Groq
from pydantic import BaseModel
from core.config import get_groq_api_key
from core.state import LeadGenState, RawLead, QualifiedLead

MODEL = "llama-3.3-70b-versatile"
SCORE_THRESHOLD = 6


class LeadScore(BaseModel):
    score: int
    reasoning: str
    priority: str
    niche: str


def _score_lead(client: Groq, lead: RawLead) -> LeadScore:
    prompt = f"""You are a B2B lead qualification expert.

Evaluate this search result as a potential Shopify store owner to cold-email.

Title: {lead['title']}
URL: {lead['url']}
Snippet: {lead['snippet']}

Score this lead from 1 to 10:
- 8-10: Clearly an active Shopify store selling products (ideal target)
- 6-7: Likely a real store but less certain
- 4-5: Possibly relevant but unclear
- 1-3: Directories, blog posts, agencies, or irrelevant pages

Also assign a priority: "high", "medium", or "low".

Respond with JSON matching this schema exactly:
{{"score": <int 1-10>, "reasoning": "<one sentence>", "priority": "<high|medium|low>", "niche": "<product category e.g. fitness, fashion, pet supplies>"}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    raw = response.choices[0].message.content or "{}"
    return LeadScore.model_validate_json(raw)


def qualify_leads(state: LeadGenState) -> LeadGenState:
    print("[2/4] 🧠 Qualifying leads with AI...")
    client = Groq(api_key=get_groq_api_key())
    qualified: list[QualifiedLead] = []

    for lead in state["raw_leads"]:
        scored = _score_lead(client, lead)
        print(f"[lead_qualifier] {lead['title'][:50]} → score={scored.score} ({scored.priority}) [{scored.niche}]")
        if scored.score >= SCORE_THRESHOLD:
            qualified.append({
                **lead,
                "score": scored.score,
                "reasoning": scored.reasoning,
                "priority": scored.priority,
                "niche": scored.niche,
            })

    print(f"[lead_qualifier] {len(qualified)}/{len(state['raw_leads'])} leads qualified")
    return {**state, "qualified_leads": qualified, "status": "leads_qualified"}
