# Quick Start Guide (For Non-Technical Users)

This guide will get you from zero to running BD Agent in **10 minutes**, even if you've never used the command line.

## Step 1: Install Prerequisites (5 minutes)

### 1.1 Install Python

**Mac:**
```bash
# Open Terminal (press Cmd+Space, type "Terminal")
brew install python@3.10
```

If you don't have Homebrew, install it first:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Windows:**
1. Go to https://python.org/downloads
2. Download Python 3.10 or higher
3. Run installer, **check "Add Python to PATH"**

### 1.2 Install uv (Python package manager)

**Mac/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Step 2: Get API Keys (3 minutes)

You need 2 API keys (both have free tiers):

### 2.1 Claude API Key (or OpenAI)

**Option A: Claude (Recommended)**
1. Go to https://console.anthropic.com
2. Sign up / Log in
3. Go to "API Keys"
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-...`)

**Option B: OpenAI**
1. Go to https://platform.openai.com
2. Sign up / Log in  
3. Go to "API Keys"
4. Click "Create new secret key"
5. Copy the key (starts with `sk-...`)

### 2.2 Serper API Key (for web search)

1. Go to https://serper.dev
2. Sign up with Google
3. You get **2,500 free searches/month**
4. Copy your API key

## Step 3: Setup BD Agent (2 minutes)

```bash
# Download BD Agent
git clone https://github.com/yourusername/bd-agent.git
cd bd-agent

# Install dependencies (takes ~30 seconds)
uv sync

# Create your .env file
cp env.example .env

# Open .env in a text editor
# On Mac:
open .env

# On Windows:
notepad .env
```

Paste your API keys into `.env`:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
SERPER_API_KEY=your-serper-key-here
```

Save and close.

## Step 4: Run Your First Workflow! (30 seconds)

```bash
uv run bd-agent
```

You'll see:

```
BD Agent - Autonomous Business Development Research
Think Dexter, but for GTM

Quick Start:
1-3: Run example workflow
4: Build custom workflow
5: Load from JSON file
q: Quit

Example Workflows
┏━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ # ┃ Goal            ┃ Industry        ┃ Signals       ┃
┡━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ 1 │ lead_list       │ fintech         │ hiring, ...   │
│ 2 │ account_briefs  │ health tech     │ product_la... │
│ 3 │ competitor_moves│ SaaS            │ funding, news │
└───┴─────────────────┴─────────────────┴───────────────┘

Choose option [1]:
```

**Type `1` and press Enter** to run the fintech example.

Watch BD Agent:
1. ✓ Plan tasks
2. 🔄 Search for companies
3. 🔄 Find signals
4. 🔄 Identify contacts  
5. ✓ Generate report

## Understanding the Output

After the workflow completes, you'll see:

```
Workflow Complete

Goal: lead_list
Duration: 45.2s
Accounts: 38
Contacts: 32 (28 verified)
Accounts with Signals: 36

Scratchpad: .bd-agent/scratchpad/2024-02-07-143022_a1b2c3d4.jsonl
```

### Where's the data?

The **summary** is printed directly in the terminal.

The **scratchpad file** has the full trace (every search, every URL).

To view it:
```bash
cat .bd-agent/scratchpad/2024-02-07-143022_a1b2c3d4.jsonl
```

## Common Issues

### "ANTHROPIC_API_KEY not found"
→ Check your `.env` file has the key on the right line with no spaces

### "SERPER_API_KEY not found"  
→ The agent will still work, but searches will be limited

### "No module named 'bd_agent'"
→ Make sure you're in the `bd-agent` directory and ran `uv sync`

### "Rate limit exceeded"
→ You hit your API limit. Wait or upgrade your plan.

## What To Try Next

### Run Another Example

```bash
uv run bd-agent
# Choose 2 for health tech
# Choose 3 for competitor tracking
```

### Build Your Own Workflow

```bash
uv run bd-agent
# Choose 4 for custom workflow
# Answer the prompts
```

### Use a JSON File

Create `my-workflow.json`:
```json
{
  "goal": "lead_list",
  "icp": {
    "industries": ["YOUR INDUSTRY HERE"],
    "geo": ["US"],
    "stage": ["seed", "series_a"]
  },
  "signals": [
    {"type": "hiring", "query": "sales OR growth"},
    {"type": "funding", "within_days": 365}
  ],
  "constraints": {
    "max_accounts": 30
  },
  "deliverable": {
    "format": "csv"
  }
}
```

Run it:
```bash
uv run bd-agent
# Choose 5
# Enter: my-workflow.json
```

## Using with Claude Code

If you have Claude Code installed:

```bash
cd bd-agent
claude-code
```

Then chat with Claude:
- "Run the fintech example workflow"
- "Add a tool to find company tech stacks"
- "Export results to CSV"
- "Debug why task 3 failed"

## Getting Help

1. **Check the scratchpad** - it shows every step the agent took
2. **Open an issue** on GitHub with your scratchpad file
3. **Read the main README** for more details

## Cost Per Run

- Free tier: ~$1-2 per workflow (LLM + search)
- You get **plenty of free searches** with Serper
- Claude free tier is generous for testing

## Next Steps

Once you're comfortable:
1. Read `README.md` for advanced usage
2. Integrate email verification (Hunter.io)
3. Add your own tools
4. Set up automated daily runs

---

**You're ready to go!** Type `uv run bd-agent` and start finding leads. 🎯
