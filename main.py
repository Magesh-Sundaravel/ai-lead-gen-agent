import sys
from core.config import get_serper_api_key, get_groq_api_key
from core.state import LeadGenState
from core.graph import app


def _print_summary_table(emails: list[dict]) -> None:
    if not emails:
        return
    rows = [
        (
            str(i + 1),
            e["title"][:20],
            e["url"][:30],
            str(e["score"]),
            e["priority"],
            e["subject"][:25],
        )
        for i, e in enumerate(emails)
    ]
    col_w = [max(len(r[c]) for r in rows + [("#", "Company", "URL", "Score", "Priority", "Subject")]) for c in range(6)]
    header = ("# ", "Company", "URL", "Score", "Priority", "Subject")
    sep = "|-" + "-|-".join("-" * w for w in col_w) + "-|"
    fmt = "| " + " | ".join(f"{{:<{w}}}" for w in col_w) + " |"

    print()
    print(fmt.format(*header))
    print(sep)
    for row in rows:
        print(fmt.format(*row))


def main() -> None:
    get_serper_api_key()
    get_groq_api_key()

    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = input("Enter your lead search query [default: negozio ecommerce italia]: ").strip()
        if not query:
            query = "negozio ecommerce italia"

    print(f"\n=== Agentic Lead Gen ===")
    print(f"Query: {query}\n")

    initial_state: LeadGenState = {
        "query": query,
        "raw_leads": [],
        "qualified_leads": [],
        "emails": [],
        "status": "init",
        "csv_path": "",
    }

    final_state: LeadGenState = initial_state
    for chunk in app.stream(initial_state, stream_mode="updates"):
        for node_name in chunk:
            final_state = {**final_state, **chunk[node_name]}

    if final_state["status"] == "no_leads":
        print("\nNo leads found for that query. Try a different search term.")
        return

    csv_path = final_state.get("csv_path", "")
    lead_count = len(final_state["emails"])
    print(f"\n✅ Done! {lead_count} lead{'s' if lead_count != 1 else ''} saved to {csv_path}")

    _print_summary_table(final_state["emails"])


if __name__ == "__main__":
    main()
