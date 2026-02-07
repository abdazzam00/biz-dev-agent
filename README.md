```
 ____  ____       _                    _
| __ )|  _ \     / \   __ _  ___ _ __ | |_
|  _ \| | | |   / _ \ / _` |/ _ \ '_ \| __|
| |_) | |_| |  / ___ \ (_| |  __/ | | | |_
|____/|____/  /_/   \_\__, |\___|_| |_|\__|
                      |___/
```

**Your AI Business Development Agent.**
Current model: `claude-3-5-sonnet` + `perplexity sonar-pro`

BD Agent learns your business during onboarding, then autonomously finds prospects, tracks competitors, surfaces insights, and prepares outreach — all backed by evidence with source URLs. No hallucinations.

## What It Does

**On Day 1:** Onboarding — learns your business, ICP, competitors, and positioning.

**Every Day After:**
| Task | What It Does |
|------|-------------|
| **Prospect Discovery** | Finds companies matching your ICP with buying signals |
| **Competitor Watch** | Monitors competitor funding, hiring, product launches |
| **Product Insights** | Surfaces market trends and customer pain points |
| **Market Signals** | Tracks buying triggers (M&A, regulation, leadership changes) |
| **Partnership Scouting** | Identifies integration and co-marketing opportunities |
| **Outreach Prep** | Prepares personalized talking points for top prospects |

**Core principle:** Evidence first. Every claim has a source URL.

---

## Prerequisites

- **Python** 3.10 or higher
- **Anthropic API key** ([get here](https://console.anthropic.com/)) — or OpenAI API key
- **Perplexity API key** ([get here](https://www.perplexity.ai/settings/api)) — for deep research with citations

### Installing Python

If you don't have Python 3.10+ installed:

**macOS** (using Homebrew):

```bash
brew install python@3.11
```

**Ubuntu/Debian:**

```bash
sudo apt update && sudo apt install python3.11 python3.11-venv python3-pip
```

**Windows:**

Download from [python.org](https://www.python.org/downloads/) and run the installer. Make sure to check "Add Python to PATH".

After installation, verify Python is installed:

```bash
python3 --version
```

---

## Quick Install (one command)

**macOS/Linux:**

```bash
curl -fsSL https://raw.githubusercontent.com/abdazzam00/biz-dev-agent/main/install.sh | bash
```

This will clone the repo, create a virtual environment, install all dependencies, and set up your `.env` file. After it finishes, just add your API keys and run `bd-agent`.

---

## Manual Install

**1. Clone the repository:**

```bash
git clone https://github.com/abdazzam00/biz-dev-agent.git
cd biz-dev-agent
```

**2. Create a virtual environment (recommended):**

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows
```

**3. Install dependencies:**

```bash
pip install -e .
```

**4. Set up your environment variables:**

```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your API keys
# ANTHROPIC_API_KEY=your-anthropic-api-key
# OPENAI_API_KEY=your-openai-api-key (optional, alternative to Anthropic)

# Required for research
# PERPLEXITY_API_KEY=your-perplexity-api-key

# Optional: For enhanced enrichment (can add later)
# APOLLO_API_KEY=your-apollo-api-key
# CLEARBIT_API_KEY=your-clearbit-api-key
# HUNTER_API_KEY=your-hunter-api-key
```

---

## How to Run

Run BD Agent in interactive mode:

```bash
bd-agent
```

On first run, BD Agent walks you through onboarding to learn your business. Then it proposes a daily task plan tailored to your needs.

```
 ____  ____       _                    _
| __ )|  _ \     / \   __ _  ___ _ __ | |_
|  _ \| | | |   / _ \ / _` |/ _ \ '_ \| __|
| |_) | |_| |  / ___ \ (_| |  __/ | | | |_
|____/|____/  /_/   \_\__, |\___|_| |_|\__|
                      |___/

Your AI Business Development Agent
Working for: YourCompany | SaaS
Current model: claude-3-5-sonnet + perplexity sonar-pro

Commands:
  d   Run daily tasks (autonomous BD work)
  1-3 Run example workflow
  c   Build custom workflow
  f   Load workflow from JSON file
  p   View/edit business profile
  o   Re-run onboarding
  q   Quit
```

---

## Architecture

BD Agent uses a **dual-AI engine**:

- **Claude** (Anthropic) — Orchestration, planning, validation, and synthesis
- **Perplexity sonar-pro** — Deep research with real-time web citations

```
1. ONBOARDING    →  Learns your business context (saved locally)
2. PLANNING      →  Breaks tasks into evidence-gathering steps
3. EXECUTION     →  Runs tools (Perplexity research, company search, signals)
4. VALIDATION    →  Checks evidence quality (URL required for every claim)
5. SYNTHESIS     →  Produces actionable results
```

### Evidence-First Data Model

Every object requires proof:

```python
Account {
    name, domain, icp_fit_score,
    signals[],  # Each signal has url + snippet + confidence
    sources[]   # URLs proving this account exists/matches
}

Contact {
    name, title, email,
    verification_status,
    sources[]   # URLs proving this person and role
}

Signal {
    type, snippet, date,
    url,        # REQUIRED — no URL = no signal
    confidence
}
```

---

## Tools (11 total)

| Tool | What It Does |
|------|-------------|
| `deep_research` | General research via Perplexity sonar-pro |
| `search_companies_by_criteria` | Find ICP-matching companies |
| `find_hiring_signals` | Discover job postings as buying signals |
| `find_funding_signals` | Track funding announcements |
| `find_company_contacts` | Identify decision-makers |
| `verify_email` | Email format validation |
| `enrich_company` | Company firmographics |
| `search_news` | Recent company news |
| `find_competitors` | Competitor analysis |
| `find_product_insights` | Market trends and insights |
| `find_partnership_opportunities` | Partnership scouting |

---

## Programmatic Usage

```python
from bd_agent import BDAgent, WorkflowSpec, WorkflowGoal, ICP, Signal, SignalType

workflow = WorkflowSpec(
    goal=WorkflowGoal.LEAD_LIST,
    icp=ICP(
        industries=["fintech"],
        geo=["NYC"],
        stage=["seed", "series_a"]
    ),
    signals=[
        Signal(type=SignalType.HIRING, query="SDR OR sales"),
        Signal(type=SignalType.FUNDING, within_days=365)
    ]
)

agent = BDAgent()
result = agent.run(workflow)
```

---

## Project Structure

```
biz-dev-agent/
├── src/bd_agent/
│   ├── agent.py          # Core agentic loop
│   ├── onboarding.py     # Business context onboarding
│   ├── model.py          # Claude/OpenAI LLM interface
│   ├── tools.py          # 11 Perplexity-powered research tools
│   ├── prompts.py        # System prompts
│   ├── schemas.py        # Data models (Account, Contact, Signal, etc.)
│   └── cli.py            # Interactive CLI
├── .bd-agent/            # Local data (auto-created)
│   ├── profile.json      # Your business profile
│   ├── daily_plan.json   # Daily task plan
│   └── scratchpad/       # JSONL run logs
├── examples/             # Example workflows
├── pyproject.toml
└── env.example
```

---

## Cost Estimate

Typical daily run:
- Claude calls: ~$0.50–1.50
- Perplexity sonar-pro: ~$0.50–2.00
- **Total: ~$1–3.50/day for full BD coverage**

## License

MIT
