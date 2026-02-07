"""
Onboarding flow for Pepo.

Collects business context so the agent understands:
- What your company does
- Who you sell to
- Who your competitors are
- What daily tasks to perform
"""
import json
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from bd_agent.schemas import BusinessProfile, DailyTask, DailyPlan, DailyTaskType
from bd_agent.model import call_llm, DEFAULT_MODEL
from bd_agent.prompts import ONBOARDING_SYSTEM_PROMPT

console = Console()

PROFILE_DIR = Path(".bd-agent")
PROFILE_FILE = PROFILE_DIR / "profile.json"
DAILY_PLAN_FILE = PROFILE_DIR / "daily_plan.json"


def load_profile() -> Optional[BusinessProfile]:
    """Load existing business profile"""
    if PROFILE_FILE.exists():
        try:
            data = json.loads(PROFILE_FILE.read_text())
            return BusinessProfile(**data)
        except Exception:
            return None
    return None


def save_profile(profile: BusinessProfile) -> None:
    """Save business profile to disk"""
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_FILE.write_text(profile.model_dump_json(indent=2))


def load_daily_plan() -> Optional[DailyPlan]:
    """Load existing daily plan"""
    if DAILY_PLAN_FILE.exists():
        try:
            data = json.loads(DAILY_PLAN_FILE.read_text())
            return DailyPlan(**data)
        except Exception:
            return None
    return None


def save_daily_plan(plan: DailyPlan) -> None:
    """Save daily plan to disk"""
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_PLAN_FILE.write_text(plan.model_dump_json(indent=2))


def run_onboarding() -> BusinessProfile:
    """Interactive onboarding to collect business context"""

    console.print(Panel(
        "[bold blue]Let's set up Pepo[/bold blue]\n\n"
        "I need to understand your business so I can find the right\n"
        "prospects, track competitors, and surface insights for you.\n\n"
        "[dim]This takes about 2 minutes. Your answers are saved locally.[/dim]",
        border_style="blue"
    ))

    console.print()

    # Company basics
    console.print("[bold]1. Your Company[/bold]")
    company_name = Prompt.ask("   Company name")
    website = Prompt.ask("   Website", default="")
    industry = Prompt.ask("   Your industry (e.g., SaaS, fintech, health tech)")

    console.print()

    # Product
    console.print("[bold]2. Your Product[/bold]")
    product_description = Prompt.ask("   What does your product/service do? (one sentence)")
    value_proposition = Prompt.ask("   Your key value prop (why customers choose you)")

    console.print()

    # Target market
    console.print("[bold]3. Target Market[/bold]")
    target_customer = Prompt.ask("   Who do you sell to? (e.g., 'Series A-C SaaS companies')")
    target_industries_raw = Prompt.ask(
        "   Target industries (comma-separated)",
        default=industry
    )
    target_industries = [i.strip() for i in target_industries_raw.split(",")]

    target_regions_raw = Prompt.ask("   Target regions (comma-separated)", default="US")
    target_regions = [r.strip() for r in target_regions_raw.split(",")]

    target_titles_raw = Prompt.ask(
        "   Decision-maker titles you target (comma-separated)",
        default="VP Sales, Head of Growth, CRO, CEO"
    )
    target_titles = [t.strip() for t in target_titles_raw.split(",")]

    console.print()

    # Competition
    console.print("[bold]4. Competitive Landscape[/bold]")
    competitors_raw = Prompt.ask(
        "   Known competitors (comma-separated, or 'none')",
        default="none"
    )
    competitors = [] if competitors_raw.lower() == "none" else [
        c.strip() for c in competitors_raw.split(",")
    ]

    console.print()

    # Pain points and differentiators
    console.print("[bold]5. Positioning[/bold]")
    pain_points_raw = Prompt.ask(
        "   Problems your product solves (comma-separated)",
        default=""
    )
    pain_points = [p.strip() for p in pain_points_raw.split(",") if p.strip()]

    differentiators_raw = Prompt.ask(
        "   What makes you different? (comma-separated)",
        default=""
    )
    differentiators = [d.strip() for d in differentiators_raw.split(",") if d.strip()]

    console.print()

    # Current clients (for lookalike)
    console.print("[bold]6. Current Clients (optional - helps find lookalikes)[/bold]")
    clients_raw = Prompt.ask(
        "   Example clients (comma-separated, or 'skip')",
        default="skip"
    )
    current_clients = [] if clients_raw.lower() == "skip" else [
        c.strip() for c in clients_raw.split(",")
    ]

    # Build profile
    profile = BusinessProfile(
        company_name=company_name,
        website=website if website else None,
        industry=industry,
        product_description=product_description,
        target_customer=target_customer,
        value_proposition=value_proposition,
        competitors=competitors,
        target_titles=target_titles,
        target_industries=target_industries,
        target_regions=target_regions,
        pain_points=pain_points,
        differentiators=differentiators,
        current_clients=current_clients,
    )

    # Save
    save_profile(profile)

    # Display summary
    display_profile(profile)

    return profile


def display_profile(profile: BusinessProfile):
    """Display the business profile"""
    table = Table(title="Your Business Profile", show_header=False, border_style="blue")
    table.add_column("Field", style="bold")
    table.add_column("Value")

    table.add_row("Company", profile.company_name)
    table.add_row("Website", profile.website or "-")
    table.add_row("Industry", profile.industry)
    table.add_row("Product", profile.product_description)
    table.add_row("Value Prop", profile.value_proposition)
    table.add_row("Target", profile.target_customer)
    table.add_row("Industries", ", ".join(profile.target_industries))
    table.add_row("Regions", ", ".join(profile.target_regions))
    table.add_row("Titles", ", ".join(profile.target_titles))
    table.add_row("Competitors", ", ".join(profile.competitors) if profile.competitors else "-")
    table.add_row("Pain Points", ", ".join(profile.pain_points) if profile.pain_points else "-")
    table.add_row("Differentiators", ", ".join(profile.differentiators) if profile.differentiators else "-")
    table.add_row("Clients", ", ".join(profile.current_clients) if profile.current_clients else "-")

    console.print()
    console.print(table)
    console.print()


def generate_daily_plan(profile: BusinessProfile, model: str = DEFAULT_MODEL) -> DailyPlan:
    """Use LLM to generate a tailored daily plan based on business profile"""

    console.print("[dim]Generating your personalized daily plan...[/dim]")

    system_prompt = ONBOARDING_SYSTEM_PROMPT.format(profile=profile.summary())

    try:
        response = call_llm(
            prompt=f"""Create a daily BD task plan for {profile.company_name}.

Business context:
- Industry: {profile.industry}
- Product: {profile.product_description}
- Target: {profile.target_customer}
- Competitors: {', '.join(profile.competitors) if profile.competitors else 'Unknown'}
- Target industries: {', '.join(profile.target_industries)}
- Target regions: {', '.join(profile.target_regions)}
- Pain points: {', '.join(profile.pain_points) if profile.pain_points else 'Not specified'}

Generate specific, actionable daily tasks.""",
            system_prompt=system_prompt,
            model_name=model,
            response_format=DailyPlan,
        )

        if isinstance(response, DailyPlan):
            return response

    except Exception as e:
        console.print(f"[yellow]Could not generate AI plan ({e}), using defaults[/yellow]")

    # Fallback: generate sensible defaults from profile
    return _default_daily_plan(profile)


def _default_daily_plan(profile: BusinessProfile) -> DailyPlan:
    """Generate default daily plan from profile"""
    tasks = [
        DailyTask(
            type=DailyTaskType.PROSPECT_DISCOVERY,
            name=f"Find new {profile.target_customer} prospects",
            description=(
                f"Search for {', '.join(profile.target_industries)} companies "
                f"in {', '.join(profile.target_regions)} that match the ICP. "
                f"Look for companies showing buying signals like hiring, funding, or expansion."
            ),
        ),
        DailyTask(
            type=DailyTaskType.COMPETITOR_WATCH,
            name=f"Monitor competitor activity",
            description=(
                f"Check for news, funding, product launches, and hiring moves from: "
                f"{', '.join(profile.competitors) if profile.competitors else 'key players in ' + profile.industry}. "
                f"Surface anything that affects our positioning or creates urgency."
            ),
        ),
        DailyTask(
            type=DailyTaskType.PRODUCT_INSIGHTS,
            name=f"Gather {profile.industry} market insights",
            description=(
                f"Find emerging trends, customer pain points, and product opportunities "
                f"in {profile.industry}. Focus on problems that {profile.company_name} "
                f"could address or areas where the product could improve."
            ),
        ),
        DailyTask(
            type=DailyTaskType.MARKET_SIGNALS,
            name="Track market signals and triggers",
            description=(
                f"Monitor funding rounds, M&A activity, leadership changes, and regulatory "
                f"shifts in {', '.join(profile.target_industries)}. These are buying triggers "
                f"for outreach timing."
            ),
        ),
        DailyTask(
            type=DailyTaskType.PARTNERSHIP_SCOUTING,
            name="Scout partnership opportunities",
            description=(
                f"Identify companies with complementary products or shared customers "
                f"that could be integration, reseller, or co-marketing partners for "
                f"{profile.company_name}."
            ),
            schedule="weekly",
        ),
        DailyTask(
            type=DailyTaskType.OUTREACH_PREP,
            name="Prepare outreach for top prospects",
            description=(
                f"For the top 5 prospects found this week, research their specific "
                f"pain points and prepare personalized talking points referencing recent "
                f"signals. Target titles: {', '.join(profile.target_titles)}."
            ),
            schedule="weekdays",
        ),
    ]

    return DailyPlan(
        tasks=tasks,
        reasoning=(
            f"Daily plan tailored for {profile.company_name}'s BD in {profile.industry}. "
            f"Prioritizes prospect discovery and competitor monitoring daily, "
            f"with partnership scouting weekly and outreach prep on weekdays."
        ),
    )


def display_daily_plan(plan: DailyPlan):
    """Display the daily plan"""

    console.print(Panel(
        "[bold blue]Your Daily Pepo Plan[/bold blue]\n\n"
        "Here's what I'll be doing for you on a daily basis:",
        border_style="blue"
    ))

    table = Table(show_header=True, border_style="blue")
    table.add_column("#", style="blue", width=3)
    table.add_column("Task", style="bold")
    table.add_column("Schedule", justify="center")
    table.add_column("Status", justify="center")

    for i, task in enumerate(plan.tasks, 1):
        status = "[green]On[/green]" if task.enabled else "[dim]Off[/dim]"
        table.add_row(str(i), task.name, task.schedule, status)

    console.print(table)

    if plan.reasoning:
        console.print(f"\n[dim]Strategy: {plan.reasoning}[/dim]")

    console.print()

    # Show details
    for i, task in enumerate(plan.tasks, 1):
        emoji_map = {
            DailyTaskType.PROSPECT_DISCOVERY: ">>",
            DailyTaskType.COMPETITOR_WATCH: "**",
            DailyTaskType.PRODUCT_INSIGHTS: "??",
            DailyTaskType.MARKET_SIGNALS: "~~",
            DailyTaskType.PARTNERSHIP_SCOUTING: "<>",
            DailyTaskType.OUTREACH_PREP: "!!",
        }
        prefix = emoji_map.get(task.type, "--")
        console.print(f"  {prefix} [bold]{task.name}[/bold]")
        console.print(f"     [dim]{task.description}[/dim]")
        console.print()
