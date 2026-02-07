import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from contextlib import contextmanager

from bd_agent.schemas import (
    Task, TaskList, TaskValidation, OverallValidation, ToolCall,
    WorkflowSpec, WorkflowResult, Account, Contact, Signal,
    ScratchpadEntry, BusinessProfile, DailyPlan, DailyTask
)
from bd_agent.tools import TOOLS, get_tool_by_name
from bd_agent.model import call_llm, DEFAULT_MODEL
from bd_agent.prompts import (
    PLANNING_SYSTEM_PROMPT,
    ACTION_SYSTEM_PROMPT,
    VALIDATION_SYSTEM_PROMPT,
    META_VALIDATION_SYSTEM_PROMPT,
    ANSWER_SYSTEM_PROMPT,
    CONTEXT_SELECTION_SYSTEM_PROMPT,
)

console = Console()


@contextmanager
def show_progress(description: str, completion_message: str):
    """Context manager to show progress spinner"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(description, total=None)
        try:
            yield progress
        finally:
            progress.update(task, description=completion_message)


class BDAgent:
    """
    BD Agent - Autonomous Business Development Agent

    Autonomous agent that:
    1. Plans BD research tasks
    2. Executes with evidence collection via Perplexity + Claude
    3. Validates data quality
    4. Produces verified, cited results
    """

    def __init__(
        self,
        max_steps: int = 30,
        max_steps_per_task: int = 8,
        model: str = DEFAULT_MODEL,
        profile: Optional[BusinessProfile] = None,
    ):
        self.max_steps = max_steps
        self.max_steps_per_task = max_steps_per_task
        self.model = model
        self.profile = profile
        self.step_count = 0
        self.all_outputs: Dict[int, List[str]] = {}
        self.scratchpad: List[ScratchpadEntry] = []
        self.scratchpad_file: Optional[Path] = None
        self.start_time: Optional[datetime] = None

        # Create scratchpad directory
        self.scratchpad_dir = Path(".bd-agent/scratchpad")
        self.scratchpad_dir.mkdir(parents=True, exist_ok=True)

    def run(self, workflow_spec: WorkflowSpec) -> WorkflowResult:
        """
        Main entry point - execute a BD workflow

        Returns:
            WorkflowResult with accounts, contacts, and evidence
        """
        self.start_time = datetime.now()

        # Initialize scratchpad file
        timestamp = self.start_time.strftime("%Y-%m-%d-%H%M%S")
        run_id = hex(hash(str(workflow_spec)))[2:10]
        self.scratchpad_file = self.scratchpad_dir / f"{timestamp}_{run_id}.jsonl"

        # Log workflow start
        self._log_scratchpad(ScratchpadEntry(
            type="init",
            llm_summary=f"Starting {workflow_spec.goal.value} workflow"
        ))

        console.print(f"\n[bold cyan]BD Agent Workflow:[/bold cyan] {workflow_spec.goal.value}")
        console.print(f"[dim]ICP: {workflow_spec.icp.industries}, {workflow_spec.icp.geo}[/dim]")

        if self.profile:
            console.print(f"[dim]Context: {self.profile.company_name} ({self.profile.industry})[/dim]")

        console.print()

        # Step 1: Plan tasks
        tasks = self.plan_tasks(workflow_spec)
        self.display_tasks(tasks)

        # Step 2: Execute tasks
        self.execute_tasks(tasks, workflow_spec)

        # Step 3: Extract structured results
        accounts, contacts = self.extract_results(tasks, workflow_spec)

        # Step 4: Generate summary
        summary = self.generate_summary(workflow_spec, accounts, contacts)

        # Calculate metrics
        duration = (datetime.now() - self.start_time).total_seconds()

        result = WorkflowResult(
            goal=workflow_spec.goal,
            accounts=accounts,
            contacts=contacts,
            summary=summary,
            duration_seconds=duration,
            scratchpad_file=str(self.scratchpad_file)
        )

        # Log completion
        self._log_scratchpad(ScratchpadEntry(
            type="final",
            llm_summary=f"Completed: {len(accounts)} accounts, {result.verified_contacts_count()} verified contacts"
        ))

        self.display_results(result)

        return result

    def run_daily_task(self, task: DailyTask) -> str:
        """
        Run a single daily task and return results.
        This is for the daily autonomous loop.
        """
        console.print(f"\n[bold cyan]Running:[/bold cyan] {task.name}")
        console.print(f"[dim]{task.description}[/dim]\n")

        # Use the appropriate tool based on task type
        from bd_agent.tools import (
            deep_research, find_competitors, find_product_insights,
            search_companies_by_criteria, search_news, find_partnership_opportunities
        )

        tool_map = {
            "prospect_discovery": deep_research,
            "competitor_watch": find_competitors if self.profile and self.profile.competitors else search_news,
            "product_insights": find_product_insights,
            "market_signals": search_news,
            "partnership_scouting": find_partnership_opportunities,
            "outreach_prep": deep_research,
        }

        tool_fn = tool_map.get(task.type.value, deep_research)

        try:
            # Build query from task description + business context
            context = ""
            if self.profile:
                context = f" (Context: {self.profile.summary()})"

            result = tool_fn.invoke({"query": task.description + context})
            output = str(result)

            # Display result
            preview = output[:500] + "..." if len(output) > 500 else output
            console.print(Panel(
                preview,
                title=f"[cyan]{task.name}[/cyan]",
                border_style="cyan"
            ))

            # Log to scratchpad
            self._log_scratchpad(ScratchpadEntry(
                type="tool_result",
                tool_name=task.type.value,
                result=output[:500],
                llm_summary=f"Daily task: {task.name}",
                evidence_urls=self._extract_urls_from_output(output)
            ))

            return output

        except Exception as e:
            error_msg = f"Error running {task.name}: {e}"
            console.print(f"[red]{error_msg}[/red]")
            return error_msg

    def _log_scratchpad(self, entry: ScratchpadEntry):
        """Log an entry to the scratchpad file"""
        self.scratchpad.append(entry)

        if self.scratchpad_file:
            with open(self.scratchpad_file, 'a') as f:
                f.write(entry.model_dump_json() + '\n')

    def plan_tasks(self, workflow_spec: WorkflowSpec) -> List[Task]:
        """Break down the workflow into actionable tasks"""
        with show_progress("Planning tasks...", "Tasks planned"):
            tool_descriptions = "\n".join([
                f"- {t.name}: {t.description}" for t in TOOLS
            ])

            # Add business context if available
            context_str = ""
            if self.profile:
                context_str = f"\n\nBusiness Context:\n{self.profile.summary()}"

            prompt = f"""Workflow Goal: {workflow_spec.goal.value}

ICP:
- Industries: {', '.join(workflow_spec.icp.industries)}
- Locations: {', '.join(workflow_spec.icp.geo)}
- Stage: {workflow_spec.icp.stage if workflow_spec.icp.stage else 'Any'}
- Size: {workflow_spec.icp.company_size.model_dump() if workflow_spec.icp.company_size else 'Any'}

Signals Required:
{json.dumps([s.model_dump() for s in workflow_spec.signals], indent=2)}

Constraints:
- Max accounts: {workflow_spec.constraints.max_accounts}
- Must have verified email: {workflow_spec.constraints.must_have_verified_email}
- Exclude keywords: {workflow_spec.constraints.exclude_keywords}
{context_str}

Create a task plan that will collect EVIDENCE-BACKED data.
Every task must produce data with SOURCE URLS."""

            system_prompt = PLANNING_SYSTEM_PROMPT.format(tools=tool_descriptions)

            try:
                response = call_llm(
                    prompt,
                    system_prompt=system_prompt,
                    model_name=self.model,
                    response_format=TaskList
                )

                return response.tasks
            except Exception as e:
                console.print(f"[red]Error planning tasks: {e}[/red]")
                return [
                    Task(id=1, description="Search for companies matching ICP", done=False),
                    Task(id=2, description="Find signals for discovered companies", done=False),
                    Task(id=3, description="Identify contacts at companies", done=False),
                ]

    def execute_tasks(self, tasks: List[Task], workflow_spec: WorkflowSpec) -> None:
        """Execute all tasks with validation"""
        incomplete_tasks = [t for t in tasks if not t.done]

        while incomplete_tasks and self.step_count < self.max_steps:
            task = incomplete_tasks[0]

            if task.step_count >= self.max_steps_per_task:
                console.print(f"[yellow]Task {task.id} reached max steps[/yellow]")
                task.done = True
                incomplete_tasks = [t for t in tasks if not t.done]
                continue

            self.execute_task_step(task, tasks)

            if self.validate_task(task):
                task.done = True
                console.print(f"[green]Task {task.id} completed with evidence[/green]")

            incomplete_tasks = [t for t in tasks if not t.done]

            if self.validate_overall(tasks, workflow_spec):
                console.print("[green]Sufficient data collected[/green]")
                break

    def execute_task_step(self, task: Task, all_tasks: List[Task]) -> None:
        """Execute a single step for a task"""
        self.step_count += 1
        task.step_count += 1

        console.print(f"\n[bold]Step {self.step_count}:[/bold] Task {task.id}")
        console.print(f"[dim]{task.description}[/dim]")

        context = self.select_context(task, all_tasks)
        tool_call = self.select_tool(task, context)

        if not tool_call:
            console.print("[yellow]No tool selected[/yellow]")
            return

        output = self.execute_tool(tool_call)

        self._log_scratchpad(ScratchpadEntry(
            type="tool_result",
            tool_name=tool_call.tool_name,
            args=tool_call.arguments,
            result=output[:500],
            llm_summary=f"Executed {tool_call.tool_name} for task {task.id}",
            evidence_urls=self._extract_urls_from_output(output)
        ))

        if task.id not in self.all_outputs:
            self.all_outputs[task.id] = []
        self.all_outputs[task.id].append(output)
        task.outputs.append(output)

        task.evidence_count = len(self._extract_urls_from_output(output))

        preview = output[:300] + "..." if len(output) > 300 else output
        console.print(Panel(
            preview,
            title=f"[cyan]{tool_call.tool_name}[/cyan] ({task.evidence_count} URLs)",
            border_style="cyan"
        ))

    def _extract_urls_from_output(self, output: str) -> List[str]:
        """Extract URLs from tool output for evidence tracking"""
        import re
        url_pattern = r'https?://[^\s\"\',\]\)]+'
        return list(set(re.findall(url_pattern, output)))

    def select_context(self, task: Task, all_tasks: List[Task]) -> str:
        """Select relevant context from previous tasks"""
        completed_tasks = [t for t in all_tasks if t.done and t.id != task.id]

        if not completed_tasks:
            return "No previous context."

        recent_tasks = completed_tasks[-2:]
        context_parts = []

        for t in recent_tasks:
            preview = t.outputs[0][:200] if t.outputs else "No output"
            context_parts.append(f"Task {t.id}: {preview}")

        return "\n\n".join(context_parts)

    def select_tool(self, task: Task, context: str) -> Optional[ToolCall]:
        """Select the best tool for the task"""
        tool_descriptions = "\n".join([
            f"- {t.name}: {t.description}" for t in TOOLS
        ])

        prompt = f"""Task: {task.description}

Context: {context}

Select the best tool and provide arguments."""

        system_prompt = ACTION_SYSTEM_PROMPT.format(
            tools=tool_descriptions,
            context=context,
            task=task.description
        )

        try:
            response = call_llm(prompt, system_prompt=system_prompt, model_name=self.model)

            if hasattr(response, 'content'):
                data = json.loads(response.content)
                return ToolCall(
                    tool_name=data['tool_name'],
                    arguments=data['arguments']
                )

            return None
        except Exception as e:
            console.print(f"[red]Error selecting tool: {e}[/red]")
            return None

    def execute_tool(self, tool_call: ToolCall) -> str:
        """Execute a tool"""
        try:
            tool = get_tool_by_name(tool_call.tool_name)
            result = tool.invoke(tool_call.arguments)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"

    def validate_task(self, task: Task) -> bool:
        """Validate if task has sufficient evidence"""
        if not task.outputs:
            return False

        if task.evidence_count == 0:
            return False

        prompt = f"""Task: {task.description}

Outputs (with {task.evidence_count} evidence URLs):
{json.dumps(task.outputs[:2], indent=2)}

Is this complete with evidence?"""

        try:
            response = call_llm(
                prompt,
                system_prompt=VALIDATION_SYSTEM_PROMPT,
                model_name=self.model,
                response_format=TaskValidation
            )
            return response.done and response.has_evidence
        except:
            return False

    def validate_overall(self, tasks: List[Task], workflow_spec: WorkflowSpec) -> bool:
        """Check if workflow has sufficient data"""
        completed_tasks = [t for t in tasks if t.done]

        if len(completed_tasks) < 2:
            return False

        total_evidence = sum(t.evidence_count for t in completed_tasks)
        if total_evidence < 5:
            return False

        return True

    def extract_results(
        self,
        tasks: List[Task],
        workflow_spec: WorkflowSpec
    ) -> tuple[List[Account], List[Contact]]:
        """Extract structured accounts and contacts from task outputs"""
        accounts = []
        contacts = []

        console.print(f"\n[dim]Extracting structured data from {len(tasks)} tasks...[/dim]")

        return accounts, contacts

    def generate_summary(
        self,
        workflow_spec: WorkflowSpec,
        accounts: List[Account],
        contacts: List[Contact]
    ) -> str:
        """Generate workflow summary"""
        with show_progress("Generating summary...", "Summary complete"):
            all_data = {}
            for task_id, outputs in self.all_outputs.items():
                all_data[f"task_{task_id}"] = {
                    "outputs": outputs[:1],
                }

            prompt = ANSWER_SYSTEM_PROMPT.format(
                workflow_spec=workflow_spec.model_dump_json(indent=2),
                data=json.dumps(all_data, indent=2)
            )

            try:
                response = call_llm(prompt, model_name=self.model)
                return response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                return f"Error generating summary: {e}"

    def display_tasks(self, tasks: List[Task]):
        """Display planned tasks"""
        table = Table(title="Planned Tasks", show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Description")
        table.add_column("Status", justify="center")

        for task in tasks:
            status = "[green]Done[/green]" if task.done else "[dim]Pending[/dim]"
            table.add_row(str(task.id), task.description, status)

        console.print(table)
        console.print()

    def display_results(self, result: WorkflowResult):
        """Display final results"""
        console.print("\n" + "=" * 80)

        metrics = f"""
[bold]Workflow Complete[/bold]

Goal: {result.goal.value}
Duration: {result.duration_seconds:.1f}s
Accounts: {len(result.accounts)}
Contacts: {len(result.contacts)} ({result.verified_contacts_count()} verified)
Accounts with Signals: {result.accounts_with_signals_count()}

Scratchpad: {result.scratchpad_file}
        """

        console.print(Panel(metrics.strip(), border_style="green"))
        console.print(Panel(result.summary, title="[bold green]Summary[/bold green]", border_style="green"))
        console.print("=" * 80 + "\n")
