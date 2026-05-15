import json
import os
from langgraph.graph import StateGraph, END
from core.state import LeadGenState
from agents.lead_sourcer import source_leads
from agents.lead_qualifier import qualify_leads
from agents.email_generator import generate_emails

OUTPUT_PATH = "output/results.json"


def save_results(state: LeadGenState) -> LeadGenState:
    os.makedirs("output", exist_ok=True)
    final = {**state, "status": "done"}
    with open(OUTPUT_PATH, "w") as f:
        json.dump(final, f, indent=2)
    print(f"[save_results] Results saved to {OUTPUT_PATH}")
    return final


def build_graph() -> StateGraph:
    graph = StateGraph(LeadGenState)

    graph.add_node("source", source_leads)
    graph.add_node("qualify", qualify_leads)
    graph.add_node("generate_emails", generate_emails)
    graph.add_node("save_results", save_results)

    graph.set_entry_point("source")
    graph.add_edge("source", "qualify")
    graph.add_edge("qualify", "generate_emails")
    graph.add_edge("generate_emails", "save_results")
    graph.add_edge("save_results", END)

    return graph


app = build_graph().compile()
