import os
import json
from typing import List, Optional
from dotenv import load_dotenv
from bd_agent.agent import BDAgent
from bd_agent.schemas import (
    WorkflowSpec, WorkflowGoal, ICP, Signal, SignalType,
    Constraints, Deliverable, CompanySize
)
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()


def print_intro():
    """Print welcome message"""
    intro = """
[bold cyan]BD Agent[/bold cyan] - Autonomous Business Development Research
Think Dexter, but for GTM

[bold]What I do:[/bold]
• Find companies matching your ICP with evidence
• Discover buying signals (hiring, funding, launches)
• Identify decision-makers with verified contact info
• Everything cited with source URLs

[bold]Core principle:[/bold] Evidence first. No hallucinations.

[dim]Powered by Claude + Web Search[/dim]
    """
    console.print(Panel(intro.strip(), border_style="cyan"))


def get_example_workflows() -> List[WorkflowSpec]:
    """Predefined example workflows"""
    
    return [
        # Example 1: Fintech lead list
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
                must_have_verified_email=False,  # Start lenient for MVP
                exclude_keywords=["agency", "consulting"]
            ),
            deliverable=Deliverable(format="csv")
        ),
        
        # Example 2: Health tech accounts
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
        
        # Example 3: Competitor tracking
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
            constraints=Constraints(
                max_accounts=15
            ),
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
        table.add_row(
            str(i),
            example.goal.value,
            industries,
            signals
        )
    
    console.print(table)


def run_example_workflow(workflow: WorkflowSpec):
    """Run a workflow"""
    agent = BDAgent(max_steps=30, max_steps_per_task=8)
    
    console.print(f"\n[bold]Running workflow:[/bold] {workflow.goal.value}\n")
    
    try:
        result = agent.run(workflow)
        
        console.print(f"\n[green]✓ Workflow complete![/green]")
        console.print(f"Check scratchpad: [cyan]{result.scratchpad_file}[/cyan]")
        
        return result
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Workflow cancelled[/yellow]")
        return None
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        return None


def custom_workflow_builder():
    """Interactive workflow builder"""
    console.print("\n[bold cyan]Build Custom Workflow[/bold cyan]\n")
    
    # Goal
    goal_map = {
        "1": WorkflowGoal.LEAD_LIST,
        "2": WorkflowGoal.ACCOUNT_BRIEFS,
        "3": WorkflowGoal.COMPETITOR_MOVES,
        "4": WorkflowGoal.OUTREACH
    }
    
    console.print("[bold]Select goal:[/bold]")
    console.print("1. Lead List")
    console.print("2. Account Briefs")
    console.print("3. Competitor Moves")
    console.print("4. Outreach Drafts")
    
    goal_choice = Prompt.ask("Choice", choices=["1", "2", "3", "4"])
    goal = goal_map[goal_choice]
    
    # Industry
    industry = Prompt.ask("\nIndustry/vertical (e.g., fintech, SaaS, health tech)")
    
    # Geography
    geo = Prompt.ask("Geography (e.g., US, NYC, UK)", default="US")
    
    # Max accounts
    max_accounts = int(Prompt.ask("Max accounts to find", default="30"))
    
    # Create workflow
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
    
    console.print("\n[green]✓ Workflow created![/green]")
    
    if Confirm.ask("Run now?"):
        return run_example_workflow(workflow)
    
    return None


def main():
    """Main CLI entry point"""
    load_dotenv()
    
    # Check API keys
    has_llm = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
    has_search = os.getenv("SERPER_API_KEY")
    
    if not has_llm:
        console.print("[red]Error: No LLM API key found![/red]")
        console.print("Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env")
        return
    
    if not has_search:
        console.print("[yellow]Warning: SERPER_API_KEY not found[/yellow]")
        console.print("[dim]Web search will be limited. Get free key at https://serper.dev[/dim]\n")
    
    print_intro()
    
    examples = get_example_workflows()
    
    console.print("\n[bold]Quick Start:[/bold]")
    console.print("1-3: Run example workflow")
    console.print("4: Build custom workflow")
    console.print("5: Load from JSON file")
    console.print("q: Quit\n")
    
    display_examples(examples)
    
    while True:
        choice = Prompt.ask("\n[bold]Choose option[/bold]", default="1")
        
        if choice.lower() in ['q', 'quit', 'exit']:
            console.print("\n[cyan]Thanks for using BD Agent! 👋[/cyan]\n")
            break
        
        if choice in ['1', '2', '3']:
            idx = int(choice) - 1
            run_example_workflow(examples[idx])
            
            if not Confirm.ask("\nRun another workflow?"):
                break
        
        elif choice == '4':
            custom_workflow_builder()
            
            if not Confirm.ask("\nRun another workflow?"):
                break
        
        elif choice == '5':
            filepath = Prompt.ask("Path to JSON workflow file")
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                workflow = WorkflowSpec(**data)
                run_example_workflow(workflow)
                
                if not Confirm.ask("\nRun another workflow?"):
                    break
            except Exception as e:
                console.print(f"[red]Error loading file: {e}[/red]")
        
        else:
            console.print("[yellow]Invalid choice[/yellow]")


if __name__ == "__main__":
    main()
