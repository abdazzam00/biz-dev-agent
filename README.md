```
 ____  _____ ____   ___
|  _ \| ____|  _ \ / _ \
| |_) |  _| | |_) | | | |
|  __/| |___| |__/| |_| |
|_|   |_____|_|    \___/
```

**Pepo is an autonomous Business Development agent that thinks, plans, and learns as it works.** It finds prospects, tracks competitors, surfaces market insights, scouts partnerships, and prepares outreach — all backed by evidence with source URLs. Think Claude Code, but built just for business development work.

## What It Does

**On Day 1:** Onboarding — Pepo learns your business, ICP, competitors, and positioning.

**Every Day After:**
| Task | What It Does |
|------|-------------|
| **Prospect Discovery** | Finds companies matching your ICP with buying signals |
| **Competitor Watch** | Monitors competitor funding, hiring, product launches |
| **Product Insights** | Surfaces market trends and customer pain points |
| **Market Signals** | Tracks buying triggers (M&A, regulation, leadership changes) |
| **Partnership Scouting** | Identifies integration and co-marketing opportunities |
| **Outreach Prep** | Prepares personalized talking points for top prospects |

**Core principle:** Evidence first. Every claim has a source URL. No hallucinations.

---

## Prerequisites

- **Python** 3.10 or higher
- **API keys** (provided during setup)

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

This will clone the repo, create a virtual environment, install all dependencies, and set up your `.env` file. After it finishes, just add your API keys and run `pepo`.

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
cp env.example .env
# Edit .env and add your API keys
```

---

## How to Run

Run Pepo in interactive mode:

```bash
pepo
```

On first run, Pepo walks you through onboarding to learn your business. Then it proposes a daily task plan tailored to your needs.

```
 ____  _____ ____   ___
|  _ \| ____|  _ \ / _ \
| |_) |  _| | |_) | | | |
|  __/| |___| |__/| |_| |
|_|   |_____|_|    \___/

Your AI Business Development Agent
Working for: YourCompany | SaaS

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

Pepo uses a **multi-stage agentic loop** with deep research capabilities:

```
1. ONBOARDING    →  Learns your business context (saved locally)
2. PLANNING      →  Breaks tasks into evidence-gathering steps
3. EXECUTION     →  Runs research tools (company search, signals, contacts)
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
| `deep_research` | Deep research with real-time citations |
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
│   ├── model.py          # LLM interface
│   ├── tools.py          # 11 research tools
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

## License

MIT
