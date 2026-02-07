"""Pepo - Your AI Business Development Agent"""

from bd_agent.agent import BDAgent
from bd_agent.schemas import (
    WorkflowSpec, WorkflowGoal, ICP, Signal, SignalType,
    Account, Contact, WorkflowResult, BusinessProfile, DailyTaskType
)

__version__ = "0.2.0"

__all__ = [
    "BDAgent",
    "WorkflowSpec",
    "WorkflowGoal",
    "ICP",
    "Signal",
    "SignalType",
    "Account",
    "Contact",
    "WorkflowResult",
    "BusinessProfile",
    "DailyTaskType",
]
