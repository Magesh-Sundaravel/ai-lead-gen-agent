from groq import Groq
from pydantic import BaseModel
from core.config import get_groq_api_key
from core.state import LeadGenState, RawLead, QualifiedLead

MODEL = "llama-3.3-70b-versatile"
SCORE_THRESHOLD = 2


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

Score this lead from 1 to 5 (5 is highest priority):
- 5: Clearly an active e-commerce store selling products in Italy (ideal target)
- 4: Likely a real Italian store but slightly less certain
- 3: Possibly relevant — may be an Italian store or sell to Italian market
- 2: Unclear or only loosely relevant
- 1: Directories, blog posts, agencies, or irrelevant pages

Also assign a priority: "high" (score 5), "medium" (score 3–4), or "low" (score 1–2).

Respond with JSON matching this schema exactly:
{{"score": <int 1-5>, "reasoning": "<one sentence>", "priority": "<high|medium|low>", "niche": "<product category e.g. fashion, food, electronics, home decor>"}}"""

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

    top10 = sorted(qualified, key=lambda x: x["score"], reverse=True)[:10]
    print(f"[lead_qualifier] {len(qualified)}/{len(state['raw_leads'])} leads qualified → keeping top {len(top10)}")
    return {**state, "qualified_leads": top10, "status": "leads_qualified"}
