# BD Agent

**Your AI Business Development Agent** - An autonomous agent that does BD research 24/7 so you don't have to.

BD Agent learns your business during onboarding, then autonomously finds prospects, tracks competitors, surfaces insights, and prepares outreach - all backed by evidence with source URLs.

## What It Does

**On Day 1:** Onboarding - learns your business, ICP, competitors, and positioning.

**Every Day After:**
- **Find New Prospects** - Discovers companies matching your ICP with buying signals
- **Competitor Watch** - Monitors competitor funding, hiring, product launches, and news
- **Product Insights** - Surfaces market trends and customer pain points
- **Market Signals** - Tracks buying triggers (M&A, regulation, leadership changes)
- **Partnership Scouting** - Identifies integration and co-marketing opportunities
- **Outreach Prep** - Prepares personalized talking points for top prospects

**Everything cited with source URLs. No hallucinations.**

## Architecture

BD Agent uses a **dual-AI engine**:

- **Claude** (Anthropic) - Orchestration, planning, validation, and synthesis
- **Perplexity sonar-pro** - Deep research with real-time web citations

### How It Works

```
1. ONBOARDING    -> Learns your business context (saved locally)
2. PLANNING      -> Breaks tasks into evidence-gathering steps
3. EXECUTION     -> Runs tools (Perplexity research, company search, signals)
4. VALIDATION    -> Checks evidence quality (URL required for every claim)
5. SYNTHESIS     -> Produces actionable results
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
    url,        # REQUIRED - no URL = no signal
    confidence
}
```

## Quick Start

```bash
# Clone
git clone https://github.com/abdazzam00/biz-dev-agent.git
cd biz-dev-agent

# Install
pip install -e .

# Configure
cp env.example .env
# Add your API keys to .env:
#   ANTHROPIC_API_KEY or OPENAI_API_KEY
#   PERPLEXITY_API_KEY

# Run
bd-agent
```

On first run, BD Agent walks you through onboarding to learn your business. Then it proposes a daily task plan tailored to your needs.

## Usage

### Interactive CLI

```bash
bd-agent
```

```
 ____  ____       _                    _
| __ )|  _ \     / \   __ _  ___ _ __ | |_
|  _ \| | | |   / _ \ / _` |/ _ \ '_ \| __|
| |_) | |_| |  / ___ \ (_| |  __/ | | | |_
|____/|____/  /_/   \_\__, |\___|_| |_|\__|
                      |___/

Your AI Business Development Agent
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

### Programmatic Usage

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

## API Keys Required

| Key | Required | What For |
|-----|----------|----------|
| `ANTHROPIC_API_KEY` | Yes (or OpenAI) | Claude for orchestration |
| `PERPLEXITY_API_KEY` | Yes | Deep research with citations |
| `OPENAI_API_KEY` | Alternative | Can use instead of Claude |

## Cost Estimate

Typical daily run:
- Claude calls: ~$0.50-1.50
- Perplexity sonar-pro: ~$0.50-2.00
- **Total: ~$1-3.50/day for full BD coverage**

## License

MIT
