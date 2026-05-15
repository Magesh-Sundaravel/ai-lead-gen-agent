import csv
import os
from datetime import datetime
from langgraph.graph import StateGraph, END
from core.state import LeadGenState
from agents.lead_sourcer import source_leads
from agents.lead_qualifier import qualify_leads
from agents.email_generator import generate_emails

CSV_COLUMNS = [
    "company_name",
    "website_url",
    "niche",
    "lead_score",
    "priority",
    "reasoning",
    "email_subject",
    "email_body",
]


def _route_after_source(state: LeadGenState) -> str:
    return "qualify" if state["raw_leads"] else END


def save_results(state: LeadGenState) -> LeadGenState:
    print("[4/4] 💾 Saving results to CSV...")
    if not state["emails"]:
        return {**state, "status": "no_emails", "csv_path": ""}

    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"output/results_{timestamp}.csv"

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for email in state["emails"]:
            writer.writerow({
                "company_name": email["title"],
                "website_url": email["url"],
                "niche": email["niche"],
                "lead_score": email["score"],
                "priority": email["priority"],
                "reasoning": email["reasoning"],
                "email_subject": email["subject"],
                "email_body": email["body"].replace("\n", "\\n"),
            })

    print(f"    Saved {len(state['emails'])} rows → {path}")
    return {**state, "status": "done", "csv_path": path}


def build_graph() -> StateGraph:
    graph = StateGraph(LeadGenState)

    graph.add_node("source", source_leads)
    graph.add_node("qualify", qualify_leads)
    graph.add_node("generate_emails", generate_emails)
    graph.add_node("save_results", save_results)

    graph.set_entry_point("source")
    graph.add_conditional_edges("source", _route_after_source, {"qualify": "qualify", END: END})
    graph.add_edge("qualify", "generate_emails")
    graph.add_edge("generate_emails", "save_results")
    graph.add_edge("save_results", END)

    return graph


app = build_graph().compile()
