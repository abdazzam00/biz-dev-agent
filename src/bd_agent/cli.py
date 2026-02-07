import os
import json
from typing import List, Optional
from dotenv import load_dotenv
from bd_agent.agent import BDAgent
from bd_agent.schemas import (
    WorkflowSpec, WorkflowGoal, ICP, Signal, SignalType,
    Constraints, Deliverable, CompanySize, BusinessProfile
)
from bd_agent.onboarding import (
    load_profile, run_onboarding, display_profile,
    load_daily_plan, save_daily_plan, generate_daily_plan, display_daily_plan
)
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

BD_AGENT_ASCII = r"""
[bold cyan]
 ____  ____       _                    _
| __ )|  _ \     / \   __ _  ___ _ __ | |_
|  _ \| | | |   / _ \ / _` |/ _ \ '_ \| __|
| |_) | |_| |  / ___ \ (_| |  __/ | | | |_
|____/|____/  /_/   \_\__, |\___|_| |_|\__|
                      |___/
[/bold cyan]"""


def print_intro(profile: Optional[BusinessProfile] = None):
    """Print welcome message with ASCII art"""
    console.print(BD_AGENT_ASCII)

    subtitle = "[bold cyan]Your AI Business Development Agent[/bold cyan]"
    if profile:
        subtitle += f"\n[dim]Working for: {profile.company_name} | {profile.industry}[/dim]"

    intro = f"""{subtitle}
Current model: [cyan]claude-3-5-sonnet[/cyan] + [cyan]perplexity sonar-pro[/cyan]

[bold]What I do every day:[/bold]
  >> Find new prospects matching your ICP
  ** Monitor competitor moves and signals
  ?? Surface product and market insights
  ~~ Track buying triggers (funding, hiring, launches)
  <> Scout partnership opportunities
  !! Prepare personalized outreach

[bold]Core principle:[/bold] Evidence first. Every claim has a source URL.
"""
    console.print(Panel(intro.strip(), border_style="cyan"))


def get_example_workflows() -> List[WorkflowSpec]:
    """Predefined example workflows"""
    return [
        WorkflowSpec(
            goal=WorkflowGoal.LEAD_LIST,
            icp=ICP(
                industries=["fintech", "payments"],
                geo=["NYC", "San Francisco"],
                stage=["seed", "series_a"],
                company_size=CompanySize(min=10, max=200)
            ),
            signals=[
                Signal(type=SignalType.HIRING, query="SDR OR sales development"),
                Signal(type=SignalType.FUNDING, within_days=365)
            ],
            constraints=Constraints(
                max_accounts=40,
                must_have_verified_email=False,
                exclude_keywords=["agency", "consulting"]
            ),
            deliverable=Deliverable(format="csv")
        ),
        WorkflowSpec(
            goal=WorkflowGoal.ACCOUNT_BRIEFS,
            icp=ICP(
                industries=["health tech", "telemedicine"],
                geo=["US"],
                stage=["series_a", "series_b"]
            ),
            signals=[
                Signal(type=SignalType.PRODUCT_LAUNCH, within_days=180),
                Signal(type=SignalType.EXPANSION)
            ],
            constraints=Constraints(
                max_accounts=20,
                exclude_keywords=[]
            ),
            deliverable=Deliverable(format="markdown")
        ),
        WorkflowSpec(
            goal=WorkflowGoal.COMPETITOR_MOVES,
            icp=ICP(
                industries=["SaaS", "developer tools"],
                geo=["US", "UK"]
            ),
            signals=[
                Signal(type=SignalType.FUNDING, within_days=90),
                Signal(type=SignalType.PRODUCT_LAUNCH, within_days=90),
                Signal(type=SignalType.NEWS, within_days=30)
            ],
            constraints=Constraints(max_accounts=15),
            deliverable=Deliverable(format="markdown")
        )
    ]


def display_examples(examples: List[WorkflowSpec]):
    """Display example workflows"""
    table = Table(title="Example Workflows")
    table.add_column("#", style="cyan")
    table.add_column("Goal")
    table.add_column("Industry")
    table.add_column("Signals")

    for i, example in enumerate(examples, 1):
        industries = ", ".join(example.icp.industries[:2])
        signals = ", ".join([s.type.value for s in example.signals[:2]])
        table.add_row(str(i), example.goal.value, industries, signals)

    console.print(table)


def run_workflow(workflow: WorkflowSpec, profile: Optional[BusinessProfile] = None):
    """Run a workflow"""
    agent = BDAgent(max_steps=30, max_steps_per_task=8, profile=profile)

    console.print(f"\n[bold]Running workflow:[/bold] {workflow.goal.value}\n")

    try:
        result = agent.run(workflow)
        console.print(f"\n[green]Workflow complete![/green]")
        console.print(f"Scratchpad: [cyan]{result.scratchpad_file}[/cyan]")
        return result
    except KeyboardInterrupt:
        console.print("\n[yellow]Workflow cancelled[/yellow]")
        return None
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        return None


def run_daily_tasks(profile: BusinessProfile):
    """Run the daily task plan"""
    plan = load_daily_plan()

    if not plan:
        console.print("[yellow]No daily plan found. Generating one...[/yellow]")
        plan = generate_daily_plan(profile)
        save_daily_plan(plan)

    display_daily_plan(plan)

    if not Confirm.ask("\nRun today's tasks now?"):
        return

    agent = BDAgent(max_steps=30, max_steps_per_task=8, profile=profile)

    enabled_tasks = [t for t in plan.tasks if t.enabled]
    console.print(f"\n[bold cyan]Running {len(enabled_tasks)} daily tasks...[/bold cyan]\n")

    results = []
    for i, task in enumerate(enabled_tasks, 1):
        console.print(f"\n{'='*60}")
        console.print(f"[bold]Task {i}/{len(enabled_tasks)}[/bold]")
        result = agent.run_daily_task(task)
        results.append(result)

    console.print(f"\n{'='*60}")
    console.print(f"[bold green]Daily tasks complete! {len(results)} tasks executed.[/bold green]")


def custom_workflow_builder(profile: Optional[BusinessProfile] = None):
    """Interactive workflow builder"""
    console.print("\n[bold cyan]Build Custom Workflow[/bold cyan]\n")

    goal_map = {
        "1": WorkflowGoal.LEAD_LIST,
        "2": WorkflowGoal.ACCOUNT_BRIEFS,
        "3": WorkflowGoal.COMPETITOR_MOVES,
        "4": WorkflowGoal.OUTREACH
    }

    console.print("[bold]Select goal:[/bold]")
    console.print("1. Lead List - Find companies + contacts")
    console.print("2. Account Briefs - Deep research on accounts")
    console.print("3. Competitor Moves - Track competitor signals")
    console.print("4. Outreach Drafts - Prepare outreach materials")

    goal_choice = Prompt.ask("Choice", choices=["1", "2", "3", "4"])
    goal = goal_map[goal_choice]

    # Pre-fill from profile if available
    default_industry = profile.industry if profile else ""
    default_geo = ", ".join(profile.target_regions) if profile else "US"

    industry = Prompt.ask("\nIndustry/vertical", default=default_industry)
    geo = Prompt.ask("Geography", default=default_geo)
    max_accounts = int(Prompt.ask("Max accounts to find", default="30"))

    workflow = WorkflowSpec(
        goal=goal,
        icp=ICP(
            industries=[industry],
            geo=[geo]
        ),
        signals=[
            Signal(type=SignalType.HIRING, query="sales OR growth"),
            Signal(type=SignalType.FUNDING, within_days=365)
        ],
        constraints=Constraints(max_accounts=max_accounts),
        deliverable=Deliverable(format="csv")
    )

    console.print("\n[green]Workflow created![/green]")

    if Confirm.ask("Run now?"):
        return run_workflow(workflow, profile)

    return None


def main():
    """Main CLI entry point"""
    load_dotenv()

    # Check API keys
    has_llm = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
    has_perplexity = os.getenv("PERPLEXITY_API_KEY")

    if not has_llm:
        console.print("[red]Error: No LLM API key found![/red]")
        console.print("Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env")
        return

    if not has_perplexity:
        console.print("[yellow]Warning: PERPLEXITY_API_KEY not set[/yellow]")
        console.print("[dim]Research capabilities will be limited. Get key at https://perplexity.ai/settings/api[/dim]\n")

    # Load or create business profile
    profile = load_profile()

    if not profile:
        console.print(BD_AGENT_ASCII)
        console.print("[bold]Welcome! Let's get you set up.[/bold]\n")

        if Confirm.ask("Run onboarding to teach BD Agent about your business?", default=True):
            profile = run_onboarding()

            # Generate daily plan
            console.print()
            plan = generate_daily_plan(profile)
            save_daily_plan(plan)
            display_daily_plan(plan)
            console.print()
        else:
            console.print("[dim]Skipping onboarding. You can run it later with option 'o'.[/dim]\n")

    print_intro(profile)

    examples = get_example_workflows()

    console.print("\n[bold]Commands:[/bold]")
    console.print("  d   Run daily tasks (autonomous BD work)")
    console.print("  1-3 Run example workflow")
    console.print("  c   Build custom workflow")
    console.print("  f   Load workflow from JSON file")
    console.print("  p   View/edit business profile")
    console.print("  o   Re-run onboarding")
    console.print("  q   Quit\n")

    display_examples(examples)

    while True:
        choice = Prompt.ask("\n[bold cyan]bd-agent[/bold cyan]", default="d")

        if choice.lower() in ['q', 'quit', 'exit']:
            console.print("\n[cyan]BD Agent signing off.[/cyan]\n")
            break

        elif choice.lower() == 'd':
            if not profile:
                console.print("[yellow]Run onboarding first (option 'o') to set up daily tasks.[/yellow]")
                continue
            run_daily_tasks(profile)

        elif choice in ['1', '2', '3']:
            idx = int(choice) - 1
            run_workflow(examples[idx], profile)

        elif choice.lower() == 'c':
            custom_workflow_builder(profile)

        elif choice.lower() == 'f':
            filepath = Prompt.ask("Path to JSON workflow file")
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                workflow = WorkflowSpec(**data)
                run_workflow(workflow, profile)
            except Exception as e:
                console.print(f"[red]Error loading file: {e}[/red]")

        elif choice.lower() == 'p':
            if profile:
                display_profile(profile)
            else:
                console.print("[dim]No profile yet. Run onboarding with 'o'.[/dim]")

        elif choice.lower() == 'o':
            profile = run_onboarding()
            plan = generate_daily_plan(profile)
            save_daily_plan(plan)
            display_daily_plan(plan)

        else:
            console.print("[yellow]Invalid choice. Try d, 1-3, c, f, p, o, or q.[/yellow]")


if __name__ == "__main__":
    main()
