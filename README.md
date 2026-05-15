# AI Lead Gen Agent

An **agentic AI pipeline** that autonomously sources, qualifies, and converts Shopify store leads into personalised cold outreach emails — with zero human input between steps.

Built with **LangGraph**, **Groq (Llama 3.3-70b)**, and **Serper API**.

---

## How It Works

```
Search (Serper API) → Score & Qualify (Groq LLM) → Generate Email (Groq LLM) → Save Results
```

Each step is an independent agent node in a **LangGraph StateGraph**. State flows through the graph automatically — no manual handoffs.

| Agent | What it does |
|---|---|
| `lead_sourcer` | Queries Serper (Google Search API) and extracts up to 10 Shopify store leads |
| `lead_qualifier` | Asks Groq LLM to score each lead 1–10 and filters out scores below 6 |
| `email_generator` | Writes a personalised cold email per qualified lead referencing their niche |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent orchestration | [LangGraph](https://github.com/langchain-ai/langgraph) |
| LLM inference | [Groq](https://groq.com) — `llama-3.3-70b-versatile` |
| Lead sourcing | [Serper API](https://serper.dev) (Google Search) |
| Structured LLM output | [Pydantic](https://docs.pydantic.dev) |
| Package management | [uv](https://github.com/astral-sh/uv) |
| Language | Python 3.11 |

---

## Project Structure

```
agentic-lead-gen/
├── agents/
│   ├── lead_sourcer.py       # Serper API search → raw leads
│   ├── lead_qualifier.py     # Groq LLM scoring + filtering
│   └── email_generator.py    # Personalised cold email generation
├── core/
│   ├── state.py              # Shared TypedDict state schema
│   ├── graph.py              # LangGraph StateGraph definition
│   └── config.py             # .env loader
├── output/                   # JSON results (gitignored)
├── main.py                   # Entry point
└── .env.example
```

---

## Setup

**1. Clone and install dependencies**
```bash
git clone https://github.com/Magesh-Sundaravel/ai-lead-gen-agent.git
cd ai-lead-gen-agent
uv sync
```

**2. Add your API keys**
```bash
cp .env.example .env
# Fill in SERPER_API_KEY and GROQ_API_KEY
```

> Get your keys: [serper.dev](https://serper.dev) (2,500 free searches) · [console.groq.com](https://console.groq.com) (free)

**3. Run**
```bash
# Default query
.venv/bin/python main.py

# Custom query
.venv/bin/python main.py "shopify store selling yoga mats"
```

---

## Sample Output

```
=== Agentic Lead Gen ===
Query: shopify store selling fitness equipment

[lead_sourcer] Found 10 leads
[lead_qualifier] The Fitness Outlet → score=8 (high)
[lead_qualifier] 1/10 leads qualified
[email_generator] Generated email for: The Fitness Outlet
[save_results] Results saved to output/results.json

=== Summary ===
  Leads sourced   : 10
  Leads qualified : 1
  Emails generated: 1
  Status          : done

Subject: Boost Conversions for Your Fitness Equipment Store
Body:
Hi, I came across The Fitness Outlet and was impressed by the wide range of
home and commercial gym equipment you offer. Our AI-powered product
recommendation tool has helped similar Shopify stores drive significant
revenue growth. Worth a quick 15-min chat?

Alex from ConvertAI
```

---

## Key Engineering Decisions

- **LangGraph StateGraph** — chose graph-based orchestration over simple function chaining to make the pipeline extensible (new agent nodes can be inserted without touching existing ones)
- **Pydantic for LLM output** — structured JSON responses validated at runtime, preventing silent failures from malformed LLM output
- **Groq for inference** — sub-second LLM responses vs. 5–10s on other providers, critical for processing batches of leads
- **Single shared state** — all agents read/write one `LeadGenState` TypedDict, making data flow explicit and debuggable

---

## Roadmap

- [ ] AWS Lambda deployment for scheduled daily runs
- [ ] Multi-niche parallel search (async)
- [ ] Email delivery via SendGrid
- [ ] Lead deduplication across runs

---

## Author

**Magesh Sundaravel** · [GitHub](https://github.com/Magesh-Sundaravel)
