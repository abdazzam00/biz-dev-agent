# BD Agent 🎯

**Business Development Agent** - An autonomous BD research agent built on the Dexter architecture. Think "Dexter for GTM".

BD Agent autonomously finds high-quality leads with **verified information** and **evidence for every claim**. No hallucinations. Every company, contact, and signal is backed by source URLs.

## What It Does (Concretely)

**Input:**
```
"Find 40 seed–Series A fintechs hiring SDRs in NYC, identify the VP Sales / Head of Growth,
find their email, and draft a 3-line opener referencing a recent signal."
```

**Output:**
- ✅ Ranked list of accounts + contacts
- ✅ Evidence links for each signal (funding, hiring, product launch, etc.)
- ✅ Draft outreach + suggested next action
- ✅ Trace file showing exactly how it got there (so you can trust/debug it)

## Core Architecture (from Dexter)

BD Agent mirrors Dexter's proven pattern: **task planning → autonomous execution → self-validation → refinement loop**.

### 1. **Multi-Agent System**

- **Planner Agent**: Turns GTM asks into evidence-gathering checklists
- **Executor Agent**: Calls tools (search, enrichment, verification)
- **Validator Agent**: Enforces "no data without source URL" rule
- **Synthesizer Agent**: Produces final output with recommended actions

### 2. **Evidence-First Data Model**

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

**Rule:** No score without at least 1 source URL.

### 3. **Safety Rails**

- Loop detection (identical to Dexter)
- Step limits (global + per-task)
- Evidence validation gates
- Cost tracking

### 4. **Scratchpad Logging**

Every run logs to `.bd-agent/scratchpad/*.jsonl`:

```jsonl
{"type":"init","timestamp":"...","llm_summary":"Starting lead_list workflow"}
{"type":"tool_result","tool_name":"search_companies_by_criteria","args":{...},"evidence_urls":[...]}
{"type":"validation","done":true,"has_evidence":true}
{"type":"final","llm_summary":"40 accounts, 35 verified contacts"}
```

## Installation

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Claude API key OR OpenAI API key
- Serper API key (free tier: 2,500 searches/month)

### Quick Start

```bash
# Clone
git clone https://github.com/yourusername/bd-agent.git
cd bd-agent

# Install
uv sync

# Configure
cp env.example .env
# Edit .env and add your API keys:
# - ANTHROPIC_API_KEY or OPENAI_API_KEY
# - SERPER_API_KEY (get free at https://serper.dev)

# Run
uv run bd-agent
```

## Usage

### Interactive Mode

```bash
uv run bd-agent
```

Choose from example workflows or build your own.

### Programmatic Usage

```python
from bd_agent import BDAgent, WorkflowSpec, WorkflowGoal, ICP, Signal, SignalType

# Define workflow
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
    ],
    constraints=Constraints(max_accounts=40)
)

# Run
agent = BDAgent()
result = agent.run(workflow)

# Access results
print(f"Found {len(result.accounts)} accounts")
print(f"{result.verified_contacts_count()} verified contacts")
print(f"Scratchpad: {result.scratchpad_file}")
```

### JSON Workflow Files

```bash
# Create workflow.json
{
  "goal": "lead_list",
  "icp": {
    "industries": ["mental health", "women's health"],
    "geo": ["US"],
    "stage": ["seed", "series_a"],
    "company_size": {"min": 10, "max": 200}
  },
  "signals": [
    {"type": "hiring", "query": "nutritionist OR dietitian"},
    {"type": "funding", "within_days": 365}
  ],
  "constraints": {
    "max_accounts": 50,
    "must_have_verified_email": false,
    "exclude_keywords": ["agency", "consulting"]
  },
  "deliverable": {
    "format": "csv"
  }
}

# Run it
uv run bd-agent  # Then select option 5 and provide path
```

## Workflow Types

### 1. Lead List
Find companies + contacts matching ICP with verified signals

**Use for:** Building outbound lists, prospecting, account discovery

### 2. Account Briefs
Deep research on specific accounts with recent signals

**Use for:** Account planning, exec briefings, strategic research

### 3. Competitor Moves
Track competitor signals (funding, launches, hiring)

**Use for:** Competitive intelligence, market monitoring

### 4. Outreach (coming soon)
Draft personalized outreach referencing real signals

**Use for:** Email sequences, LinkedIn messages, call prep

## Tools (The GTM Toolbelt)

BD Agent has 9 core tools:

1. **web_search** - General web search with evidence URLs
2. **search_companies_by_criteria** - Find ICP-matching companies
3. **find_hiring_signals** - Discover hiring postings
4. **find_funding_signals** - Track fundraising announcements
5. **find_company_contacts** - Identify decision-makers
6. **verify_email** - Email validation (integrate Hunter.io for production)
7. **enrich_company** - Company firmographics
8. **search_news** - Recent company news
9. **perplexity_search** - Use Perplexity for cited research (optional)

Each tool **returns URLs** for evidence. No guessing.

## What Makes This Different

### ❌ Traditional Tools
- Return unverified data
- Hallucinate emails
- No source attribution
- Black box operation

### ✅ BD Agent
- Every claim has a source URL
- Email verification required
- Full transparency via scratchpad
- Validates its own work

## Project Structure

```
bd-agent/
├── src/bd_agent/
│   ├── agent.py          # Main orchestration (like Dexter)
│   ├── model.py          # LLM interface
│   ├── tools.py          # 9 GTM research tools
│   ├── prompts.py        # Evidence-focused system prompts
│   ├── schemas.py        # Workflow contract + data models
│   └── cli.py            # Interactive CLI
├── .bd-agent/scratchpad/ # JSONL logs (auto-created)
├── examples/             # Example workflows
├── pyproject.toml
├── env.example
└── README.md
```

## Evaluation (Like Dexter's Eval Suite)

Create eval sets with **hard checks**:

```python
eval_metrics = {
    "% emails verified": 0.85,
    "% contacts have evidence": 1.0,
    "% accounts match ICP": 0.90,
    "duplication rate": 0.05,
    "avg cost per run": "$2.50"
}
```

Not just LLM-as-judge - **quantifiable quality**.

## Roadmap

### MVP (Current)
- [x] Core agent architecture
- [x] Evidence-first data model
- [x] Scratchpad logging
- [x] 9 essential tools
- [x] Interactive CLI
- [x] 3 workflow types

### Next
- [ ] Email verification API integration (Hunter.io)
- [ ] Company enrichment API (Clearbit/Apollo)
- [ ] CSV/Google Sheets export
- [ ] Evaluation harness
- [ ] Continuous monitoring (daily workflows)
- [ ] CRM integration (HubSpot/Salesforce)

### Future
- [ ] Outreach generation
- [ ] Sequence automation
- [ ] Pipeline cleanup
- [ ] Account scoring models

## Integration Recommendations

### For Production

1. **Email Verification**: Hunter.io, NeverBounce, or ZeroBounce
2. **Company Data**: Clearbit, Apollo, or RocketReach
3. **Contact Data**: LinkedIn Sales Navigator API (if compliant)
4. **CRM**: HubSpot or Salesforce write-back

### Claude Code Setup

This project is **Claude Code-ready**. To use with Claude Code:

```bash
# From project root
claude-code

# Then in Claude Code:
"Install dependencies and run the example fintech workflow"
"Add a new tool for finding product launch signals"
"Debug why Task 3 didn't find emails"
```

## Cost Estimate

Typical run (40 accounts):
- LLM calls: ~$0.50-1.50
- Web search: Free (Serper free tier)
- Total: **< $2 per workflow**

With premium APIs (Hunter, Clearbit):
- Add ~$0.10-0.30 per verified contact
- Still **< $15 for 40 high-quality leads**

## Inspired By

- [Dexter](https://github.com/virattt/dexter) by [@virattt](https://twitter.com/virattt) - The financial research agent that proved autonomous agents can be production-grade with the right architecture.

## License

MIT

## Support

- Open an issue on GitHub
- Check the scratchpad logs for debugging
- Review the Dexter project for similar patterns

---

**Built for BD teams who want AI-powered research they can actually trust.** 🎯
