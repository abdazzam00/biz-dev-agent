"""BD Agent - Business Development Agent (Dexter for GTM)"""

from bd_agent.agent import BDAgent
from bd_agent.schemas import (
    WorkflowSpec, WorkflowGoal, ICP, Signal, SignalType,
    Account, Contact, WorkflowResult
)

__version__ = "0.1.0"

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
]
