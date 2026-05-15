# AI Lead Gen Agent

An **agentic AI pipeline** that autonomously sources Italian e-commerce leads, validates each URL, scores them with an LLM, and writes personalised cold outreach emails — all in one CLI command.

Built with **LangGraph**, **Groq (Llama 3.3-70b)**, and **Serper API**.

---

## How It Works

```
Search (Serper) → Validate Links (HTTP) → Score & Qualify (Groq LLM) → Generate Email (Groq LLM) → Save CSV
```

Each step is an independent agent node in a **LangGraph StateGraph**. State flows through the graph automatically — no manual handoffs.

| Agent | What it does |
|---|---|
| `lead_sourcer` | Queries Serper (Google Search API) scoped to `site:.it`, returns up to 10 Italian e-commerce leads |
| `link_validator` | Makes parallel HTTP HEAD/GET requests to each URL — drops any that are broken or unreachable |
| `lead_qualifier` | Asks Groq LLM to score each live lead 1–5 and filters out scores below 2 |
| `email_generator` | Writes a personalised cold email per qualified lead referencing their niche and the Italian market |
| `save_results` | Writes a timestamped CSV to `output/` — never overwrites previous runs |

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
│   ├── lead_sourcer.py       # Serper API search → raw leads (site:.it)
│   ├── link_validator.py     # Parallel HTTP validation — drops broken URLs
│   ├── lead_qualifier.py     # Groq LLM scoring 1–5, filters score < 2
│   └── email_generator.py    # Personalised cold email per qualified lead
├── core/
│   ├── state.py              # Shared TypedDict state schema
│   ├── graph.py              # LangGraph StateGraph — 5 nodes + conditional edge
│   └── config.py             # .env loader
├── output/                   # Timestamped CSVs saved here (gitignored)
├── main.py                   # CLI entry point
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
# Default query (Italian fashion stores)
uv run python main.py

# Custom query
uv run python main.py "negozio online scarpe italia"
uv run python main.py "ecommerce food italy"
```

---

## Sample Output

```
=== Agentic Lead Gen ===
Query: negozio online abbigliamento

[1/5] 🔍 Searching for leads...
[lead_sourcer] Found 10 leads for query: 'negozio online abbigliamento site:.it'
[2/5] 🔗 Validating links...
  ✓ http://www.lovemoschino.it/
  ✓ https://www.aboutyou.it/
  ✓ https://www.antonia.it/
  ✗ http://www.asos.it/
  ✗ http://uniqlo.it/
  7/10 links are live
[3/5] 🧠 Qualifying leads with AI...
[lead_qualifier] Moschino | Boutique Online → score=5 (high) [fashion]
[lead_qualifier] Antonia Milano | Capi Esclusivi → score=5 (high) [fashion]
[lead_qualifier] 7/7 leads qualified → keeping top 7
[4/5] ✉️  Generating personalised emails...
[email_generator] Generated email for: Moschino | Boutique Online
[5/5] 💾 Saving results to CSV...
    Saved 7 rows → output/results_20260515_201459.csv

✅ Done! 7 leads saved to output/results_20260515_201459.csv

| #  | Company              | URL                        | Score | Priority | Subject                    |
|----|----------------------|----------------------------|-------|----------|----------------------------|
| 1  | Moschino | Boutique  | http://www.lovemoschino.it | 5     | high     | Boosting Revenue for Ital  |
| 2  | Antonia Milano       | https://www.antonia.it/    | 5     | high     | Boost Sales for Antonia M  |
```

**CSV columns:** `company_name`, `website_url`, `niche`, `lead_score`, `priority`, `reasoning`, `email_subject`, `email_body`

---

## Key Engineering Decisions

- **Link validation before LLM** — HTTP check runs in parallel before any API calls, so Groq never wastes tokens on dead URLs
- **LangGraph StateGraph** — graph-based orchestration makes the pipeline extensible; new agent nodes can be added without touching existing ones
- **Conditional edge** — if Serper returns zero results the graph short-circuits to `END` with `status = "no_leads"`, skipping all LLM calls
- **Pydantic for LLM output** — structured JSON responses validated at runtime, preventing silent failures from malformed output
- **Groq for inference** — sub-second LLM responses vs. 5–10s on other providers, critical for scoring batches of leads
- **Timestamped CSV output** — each run writes a new file, never overwrites previous results

---

## Roadmap

- [ ] AWS Lambda deployment for scheduled daily runs
- [ ] Multi-niche parallel search (async)
- [ ] Email delivery via SendGrid
- [ ] Lead deduplication across runs

---

## Author

**Magesh Sundaravel** · [GitHub](https://github.com/Magesh-Sundaravel)
