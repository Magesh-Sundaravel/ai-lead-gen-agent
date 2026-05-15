import requests
from core.config import get_serper_api_key
from core.state import LeadGenState, RawLead

SERPER_URL = "https://google.serper.dev/search"


def source_leads(state: LeadGenState) -> LeadGenState:
    print("[1/4] 🔍 Searching for leads...")
    query = state["query"]
    scoped_query = f"{query} site:myshopify.com"
    headers = {
        "X-API-KEY": get_serper_api_key(),
        "Content-Type": "application/json",
    }
    payload = {"q": scoped_query, "num": 10}

    response = requests.post(SERPER_URL, json=payload, headers=headers, timeout=10)
    response.raise_for_status()

    organic = response.json().get("organic", [])

    raw_leads: list[RawLead] = [
        {
            "title": result.get("title", ""),
            "url": result.get("link", ""),
            "snippet": result.get("snippet", ""),
        }
        for result in organic[:10]
    ]

    print(f"[lead_sourcer] Found {len(raw_leads)} leads for query: '{scoped_query}'")

    return {**state, "raw_leads": raw_leads, "status": "leads_sourced"}
