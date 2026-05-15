# Agentic AI Lead Generation System

## Package Manager
Use `uv` for all Python package management. Never use pip directly.
- Init project: `uv init`
- Add packages: `uv add <package>`
- Run scripts: `uv run python <script>`
- Python version: 3.11

---

## Git — Already Initialised
- Repo is live, main and dev branches exist
- Branch strategy: feature/* → dev → main
- Always create a feature branch before starting any file
- Commit message format: feat: / fix: / chore: / refactor: / docs:

## Branching Workflow Per Feature
Before starting each file:
  git checkout dev
  git checkout -b feature/<name>

After finishing and testing each file:
  git add .
  git commit -m "feat: <what you built>"
  git checkout dev
  git merge feature/<name>
  git branch -d feature/<name>

---

## Project Goal
Build a simple agentic CLI workflow that:
1. Sources Shopify store leads via Google Serper API
2. Scores and qualifies leads using Groq LLM
3. Generates a personalised cold email per qualified lead
4. Saves results as a timestamped CSV file
5. Shows live progress in terminal at every step

## Phase
PHASE 1 — Local only. No AWS, no Docker, no Lambda. Just working Python scripts.

---

## Folder Structure to Create

agentic-lead-gen/
├── agents/
│   ├── __init__.py
│   ├── lead_sourcer.py       # Step 1: search Shopify leads via Serper API
│   ├── lead_qualifier.py     # Step 2: score each lead with Groq LLM
│   └── email_generator.py    # Step 3: write personalised email per lead
├── core/
│   ├── __init__.py
│   ├── state.py              # Shared state schema (TypedDict)
│   ├── graph.py              # LangGraph workflow wiring all agents together
│   └── config.py             # Load env vars via python-dotenv
├── output/                   # CSV results saved here (gitignored)
├── .env.example              # All required env vars documented
├── .gitignore
├── main.py                   # CLI entry point — runs full workflow
└── README.md

---

## Rules
- Before writing each file, print a one-paragraph plain English explanation of:
  what this file does, why it exists, and how it connects to the others
- Before starting each file, create and switch to its feature branch
- After finishing each file, commit and merge back to dev
- All secrets from .env file, never hardcoded
- Use type hints everywhere
- Keep each agent file focused on ONE job only
- Use uv add to install, never pip
- Never overwrite previous CSV output — always timestamp the filename
- Email body in CSV must be single line (replace actual newlines with \n)
- Terminal must show progress at each step, not just at the end
- Summary table must print even if only 1 lead is found

---

## Agent Details

### agents/lead_sourcer.py
EXPLAIN FIRST: what Serper API is, what we are searching for, and what raw data comes back
- Call Serper API with the user's query e.g. "shopify store selling fitness equipment"
- Extract from each result: title, url, snippet
- Return list of dicts, max 10 leads
- Uses: SERPER_API_KEY

### agents/lead_qualifier.py
EXPLAIN FIRST: what lead scoring means, why we use an LLM for it, what structured output looks like
- For each raw lead, ask Groq to score it 1-10
- Use model: llama-3.3-70b-versatile
- Use Pydantic model for structured output with fields:
    score: int
    reasoning: str
    priority: str   (high / medium / low)
    niche: str      (inferred e.g. fitness, fashion, pet supplies)
- Keep only leads with score >= 6
- Uses: GROQ_API_KEY

### agents/email_generator.py
EXPLAIN FIRST: what personalised outreach means and how the LLM uses lead data to write it
- For each qualified lead, generate a cold outreach email
- Email must reference: store name, niche, specific value prop
- Output per lead:
    subject: str
    body: str
- Uses: GROQ_API_KEY

### core/state.py
EXPLAIN FIRST: what shared state is in an agentic workflow and why LangGraph needs it
- TypedDict with fields:
    query: str
    raw_leads: list[dict]
    qualified_leads: list[dict]
    emails: list[dict]
    status: str

### core/graph.py
EXPLAIN FIRST: what LangGraph is, what a StateGraph does, and how nodes connect
- Build StateGraph with nodes in this order:
    source_leads → qualify_leads → generate_emails → save_results
- Add conditional edge: if raw_leads is empty after sourcing, go to END with status "no_leads"
- Compile and expose as: app = graph.compile()

### main.py
EXPLAIN FIRST: this is the CLI entry point — it drives the whole workflow, shows live
progress to the user in terminal, and saves final output as a timestamped CSV file

- Accept query as CLI argument: `uv run python main.py "shopify fitness stores"`
- If no argument given, prompt user to type query interactively
- Show live progress at each step:
    [1/4] 🔍 Searching for leads...
    [2/4] 🧠 Qualifying leads with AI...
    [3/4] ✉️  Generating personalised emails...
    [4/4] 💾 Saving results to CSV...
    ✅ Done! 7 leads saved to output/results_20250115_143022.csv
- After completion, print a clean summary table in terminal:
    | # | Company       | URL                   | Score | Priority | Subject              |
    |---|---------------|-----------------------|-------|----------|----------------------|
    | 1 | FitGear Shop  | fitgear.myshopify.com | 8     | high     | Quick idea for you.. |
- Save full results to output/results_YYYYMMDD_HHMMSS.csv

---

## Output Format — CSV

File: output/results_YYYYMMDD_HHMMSS.csv

Columns in this exact order:
  company_name     → extracted from Serper result title
  website_url      → full URL
  niche            → inferred by qualifier agent
  lead_score       → integer 1-10
  priority         → high / medium / low
  reasoning        → one line explanation from LLM
  email_subject    → generated subject line
  email_body       → full email body (newlines replaced with \n)

Use Python's built-in csv module with DictWriter.
Each run creates a new timestamped file — never overwrite old results.

---

## .env.example
SERPER_API_KEY=
GROQ_API_KEY=

---

## After Each File
After writing each file, tell me:
- What was built and why
- What to run to confirm it works
- What git commands were run
- What the next file will do
Then wait for my confirmation before moving on.