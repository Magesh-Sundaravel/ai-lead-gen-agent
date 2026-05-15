from groq import Groq
from pydantic import BaseModel
from core.config import get_groq_api_key
from core.state import LeadGenState, QualifiedLead, Email

MODEL = "llama-3.3-70b-versatile"


class EmailDraft(BaseModel):
    subject: str
    body: str


def _generate_email(client: Groq, lead: QualifiedLead) -> EmailDraft:
    prompt = f"""You are an expert cold email copywriter for a B2B SaaS company targeting Italian e-commerce businesses.

Write a short, personalised cold email to the owner of this Italian e-commerce store.

Store name: {lead['title']}
Store URL: {lead['url']}
Niche: {lead['niche']}
Description: {lead['snippet']}
Lead score: {lead['score']}/5
Priority: {lead['priority']}

Rules:
- Subject line: concise, specific, no clickbait
- Body: 3-4 sentences max
- Reference the store's niche or product type and the Italian market naturally
- Value proposition: we help Italian e-commerce stores grow revenue through AI-powered personalisation and conversion optimisation
- End with a low-friction CTA (e.g. "Worth a quick 15-min chat?")
- Do NOT use placeholders like [Your Name] — sign off as "Alex from ConvertAI"
- Write the email in English
- Tone: friendly, professional, not salesy

Respond with JSON matching this schema exactly:
{{"subject": "<email subject>", "body": "<full email body>"}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    raw = response.choices[0].message.content or "{}"
    return EmailDraft.model_validate_json(raw)


def generate_emails(state: LeadGenState) -> LeadGenState:
    print("[4/5] ✉️  Generating personalised emails...")
    client = Groq(api_key=get_groq_api_key())
    emails: list[Email] = []

    for lead in state["qualified_leads"]:
        draft = _generate_email(client, lead)
        print(f"[email_generator] Generated email for: {lead['title'][:50]}")
        emails.append({
            "title": lead["title"],
            "url": lead["url"],
            "niche": lead["niche"],
            "score": lead["score"],
            "priority": lead["priority"],
            "reasoning": lead["reasoning"],
            "subject": draft.subject,
            "body": draft.body,
        })

    print(f"[email_generator] {len(emails)} email(s) generated")
    return {**state, "emails": emails, "status": "emails_generated"}
