import sys
from core.config import get_serper_api_key, get_groq_api_key
from core.state import LeadGenState
from core.graph import app

DEFAULT_QUERY = "shopify store selling fitness equipment"


def main() -> None:
    # Validate keys up front so failures are obvious before any API calls
    get_serper_api_key()
    get_groq_api_key()

    query = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUERY

    print(f"\n=== Agentic Lead Gen ===")
    print(f"Query: {query}\n")

    initial_state: LeadGenState = {
        "query": query,
        "raw_leads": [],
        "qualified_leads": [],
        "emails": [],
        "status": "init",
    }

    final_state = app.invoke(initial_state)

    print("\n=== Summary ===")
    print(f"  Leads sourced   : {len(final_state['raw_leads'])}")
    print(f"  Leads qualified : {len(final_state['qualified_leads'])}")
    print(f"  Emails generated: {len(final_state['emails'])}")
    print(f"  Status          : {final_state['status']}")

    if final_state["emails"]:
        print("\n--- Emails ---")
        for email in final_state["emails"]:
            print(f"\nTo     : {email['url']}")
            print(f"Subject: {email['subject']}")
            print(f"Body:\n{email['body']}")

    print("\nFull results saved to output/results.json")


if __name__ == "__main__":
    main()
