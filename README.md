# Agentic Lead Generation System

An agentic workflow that sources Shopify store leads, qualifies them with an LLM, and generates personalised cold emails.

## Setup

1. Copy `.env.example` to `.env` and fill in your API keys.
2. Install dependencies: `uv sync`
3. Run: `uv run python main.py`

## Required API Keys

| Key | Purpose |
|---|---|
| `SERPER_API_KEY` | Google Serper API — searches for Shopify store leads |
| `GROQ_API_KEY` | Groq LLM API — qualifies leads and writes cold emails |

## Workflow

```
source leads → qualify leads → generate emails → save results
```

Results are saved to `output/results.json`.
