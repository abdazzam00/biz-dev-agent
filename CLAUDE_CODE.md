# Using BD Agent with Claude Code

This guide shows how to use Claude Code to build, modify, and debug BD Agent workflows.

## Quick Start with Claude Code

```bash
# Navigate to the project
cd bd-agent

# Start Claude Code
claude-code
```

## Common Tasks

### 1. Run a Workflow

```
Claude, run the fintech example workflow and show me the results.
```

Claude will:
- Install dependencies if needed
- Load the workflow spec
- Execute the agent
- Display results and scratchpad

### 2. Debug a Failed Task

```
Claude, task 3 in my last run didn't find any emails. Can you:
1. Check the scratchpad to see what happened
2. Look at the tool outputs
3. Suggest a fix
```

Claude will analyze the `.bd-agent/scratchpad/*.jsonl` file and diagnose issues.

### 3. Add a New Tool

```
Claude, add a tool called "find_product_reviews" that:
- Searches G2, Capterra, and TrustRadius
- Finds reviews for a company
- Returns review snippets with URLs as evidence
- Follows the same evidence-first pattern as other tools
```

Claude will:
- Add the tool to `tools.py`
- Update the TOOLS list
- Test it with a sample call

### 4. Modify a Workflow

```
Claude, I want to modify the fintech example to:
- Only search in Austin, TX
- Look for Series B companies instead
- Find "VP of Revenue" instead of "VP Sales"
- Increase max accounts to 60
```

Claude will update `examples/fintech-leads.json` with your changes.

### 5. Create a Custom Workflow

```
Claude, create a new workflow for finding:
- SaaS companies in the developer tools space
- Series A-B stage
- Located in NYC or SF
- Recently launched a new product
- Have 20-100 employees
- Find the Head of Product and Head of Growth
```

Claude will generate the JSON spec and optionally run it.

### 6. Export Results

```
Claude, export the results from the last run to:
- A CSV file with company, contact, signal, and URLs
- A formatted markdown report
- Save to the outputs/ directory
```

### 7. Improve Validation

```
Claude, the validator is marking tasks as done too early. Can you:
1. Make it stricter about requiring evidence URLs
2. Add a check for minimum confidence scores
3. Ensure at least 3 sources per account
```

### 8. Add Perplexity Integration

```
Claude, I have a Perplexity API key. Can you:
1. Update the perplexity_search tool to actually call Perplexity
2. Test it with a sample query
3. Show me how the citations work
```

### 9. Track Costs

```
Claude, add cost tracking to the agent so I can see:
- LLM API costs per workflow
- Search API costs
- Total cost per account found
- Cost per verified contact
```

### 10. Build an Evaluation Suite

```
Claude, create an eval suite like Dexter's that:
- Has 20 test workflows
- Measures: verified emails %, evidence coverage %, ICP match %
- Runs all tests and shows results in a table
- Logs results to a file
```

## Advanced Workflows

### Multi-Stage Research

```
Claude, I want to build a 3-stage workflow:

Stage 1: Find 100 companies matching ICP
Stage 2: For each company, research their tech stack and recent funding
Stage 3: For the top 30 by fit score, find 2-3 contacts per company

Can you modify the agent to support this?
```

### Continuous Monitoring

```
Claude, set up a daily monitoring workflow that:
- Runs every morning at 9am
- Checks for new signals on my saved accounts list
- Emails me if it finds: new funding, new hiring, product launches
- Logs to a dedicated monitoring.jsonl file
```

### CRM Integration

```
Claude, I want to push results to HubSpot. Can you:
1. Add a tool that creates companies in HubSpot
2. Add a tool that creates contacts
3. Link the contact to the company
4. Add the signal as a note
5. Set a task for the assigned sales rep
```

## Debugging with Claude Code

### Check Scratchpad

```
Claude, open my last scratchpad file and tell me:
- Which tools were called
- How many evidence URLs were found
- Where the agent spent the most time
- If there were any errors
```

### Analyze Tool Performance

```
Claude, analyze all my scratchpad files from the past week and tell me:
- Which tools are most reliable
- Which tools return the most evidence
- Which tools fail most often
- Average evidence per tool call
```

### Fix Common Issues

```
Claude, I keep getting "No results found" for hiring signals. Can you:
1. Check the find_hiring_signals tool
2. Test it with a known company that's hiring
3. Debug why it's not finding anything
4. Suggest improvements to the search query
```

## Best Practices with Claude Code

### 1. Describe Intent Clearly

Good:
```
Claude, I want to find Series A dev tools companies in SF that are hiring.
Show me the workflow spec and run it.
```

Bad:
```
Claude, do the thing
```

### 2. Ask for Explanations

```
Claude, before running this, explain:
- What tasks will be created
- Which tools will be used
- What evidence will be collected
- How long it will take
```

### 3. Iterate on Results

```
Claude, that workflow found 40 accounts but only 10 had verified emails.
Can you:
- Re-run with stricter email verification
- Add more sources for email finding
- Show me the accounts that failed verification
```

### 4. Request Testing

```
Claude, before deploying this new tool, can you:
1. Write a test for it
2. Run the test with sample data
3. Show me the evidence it collects
4. Verify the output format
```

## Example Session

Here's a full example of using Claude Code:

```
You: Claude, I want to build a workflow for finding mental health startups 
     hiring therapists in California.

Claude: I'll create a workflow for you. Here's what I'll search for:
        - Industries: mental health, behavioral health, therapy
        - Location: California  
        - Signals: hiring (therapist, counselor, psychologist)
        - Stage: seed to Series B
        
        Should I proceed?

You: Yes, and also look for recent product launches

Claude: [Creates workflow, runs it]
        
        ✓ Workflow complete!
        - Found 32 companies
        - 28 have hiring signals with evidence
        - 24 have product launches in last 6 months
        - 18 contacts identified
        
        Top account: Headway (headway.co)
        Signal: Hiring 5 therapists (source: lever.co/headway/...)
        Recent launch: Launched Medicare coverage (source: techcrunch.com/...)
        
        Would you like me to export this to CSV?

You: Yes, and can you add a column showing when they launched the product?

Claude: [Updates export format, regenerates CSV]
        
        Done! Saved to outputs/mental-health-2024-02-07.csv
        
        Columns:
        - Company, Domain, Hiring Signal, Launch Date, Launch Description, 
          Contact Name, Title, Confidence, Evidence URLs
```

## Tips for Non-Technical Users

### You Don't Need to Code

Just describe what you want:

```
Claude, I need a list of companies that:
- Sell to restaurants
- Just raised money
- Are hiring salespeople
- Based in Texas or Florida

Give me 50 companies with the owner's contact info.
```

### Ask for Explanations

```
Claude, explain what this workflow will do step-by-step in simple terms.
```

### Request Modifications

```
Claude, the results look good but can you:
- Remove any companies with fewer than 20 employees
- Add a column showing their LinkedIn URL
- Sort by most recent funding first
```

### Troubleshoot Together

```
Claude, it says "No results found" - why is that happening and how do I fix it?
```

## Next Steps

After getting comfortable with Claude Code:

1. **Build Custom Workflows** - Define your exact ICP and signals
2. **Add Integration** - Connect to your CRM, email tools, etc.
3. **Automate** - Set up scheduled runs
4. **Scale** - Process larger datasets with Claude Code's help

---

**The key insight:** Claude Code handles all the technical details. You just describe what you want to research, and Claude builds/runs/debugs it for you.
