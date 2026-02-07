from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class WorkflowGoal(str, Enum):
    """Types of BD workflows"""
    LEAD_LIST = "lead_list"
    ACCOUNT_BRIEFS = "account_briefs"
    COMPETITOR_MOVES = "competitor_moves"
    OUTREACH = "outreach"


class SignalType(str, Enum):
    """Types of buying signals"""
    HIRING = "hiring"
    FUNDING = "funding"
    PRODUCT_LAUNCH = "product_launch"
    TECH_STACK = "tech_stack"
    NEWS = "news"
    JOB_CHANGE = "job_change"
    EXPANSION = "expansion"


class CompanySize(BaseModel):
    """Company size constraints"""
    min: Optional[int] = None
    max: Optional[int] = None


class ICP(BaseModel):
    """Ideal Customer Profile definition"""
    industries: List[str] = Field(description="Target industries")
    geo: List[str] = Field(description="Geographic regions (US, UK, etc.)")
    stage: Optional[List[str]] = Field(default=None, description="Funding stages: seed, series_a, etc.")
    company_size: Optional[CompanySize] = None
    tech_stack: Optional[List[str]] = Field(default=None, description="Required technologies")


class Signal(BaseModel):
    """A buying signal with evidence"""
    type: SignalType
    query: Optional[str] = None
    within_days: Optional[int] = None
    snippet: Optional[str] = None
    date: Optional[datetime] = None
    url: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    def has_evidence(self) -> bool:
        """Check if signal has proper evidence"""
        return self.url is not None and self.snippet is not None


class Constraints(BaseModel):
    """Workflow constraints"""
    max_accounts: int = Field(default=50)
    must_have_verified_email: bool = Field(default=True)
    exclude_keywords: List[str] = Field(default_factory=list)
    min_signal_confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class Deliverable(BaseModel):
    """Output format specification"""
    format: Literal["csv", "json", "markdown"] = "csv"
    columns: List[str] = Field(default_factory=lambda: [
        "company", "domain", "signal", "source_url", 
        "contact_name", "title", "email", "confidence"
    ])


class WorkflowSpec(BaseModel):
    """The main workflow contract - users provide this"""
    goal: WorkflowGoal
    icp: ICP
    signals: List[Signal] = Field(default_factory=list)
    constraints: Constraints = Field(default_factory=Constraints)
    deliverable: Deliverable = Field(default_factory=Deliverable)


class Account(BaseModel):
    """Account/Company with evidence"""
    name: str
    domain: str
    icp_fit_score: float = Field(ge=0.0, le=1.0)
    signals: List[Signal] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list, description="URLs proving this account exists/matches")
    
    # Firmographics
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    funding_stage: Optional[str] = None
    location: Optional[str] = None
    
    def has_verified_signals(self) -> bool:
        """Check if account has at least one signal with evidence"""
        return any(s.has_evidence() for s in self.signals)


class Contact(BaseModel):
    """Contact with evidence and verification"""
    name: str
    title: str
    company: str
    linkedin: Optional[str] = None
    email: Optional[str] = None
    verification_status: Literal["unverified", "verified", "bounced", "catch_all"] = "unverified"
    sources: List[str] = Field(default_factory=list, description="URLs proving this person and role")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    def is_verified(self) -> bool:
        """Check if contact has verified email and evidence"""
        return (
            self.verification_status == "verified" 
            and len(self.sources) > 0
            and self.email is not None
        )


class Task(BaseModel):
    """A single research task"""
    id: int
    description: str
    done: bool = False
    outputs: List[str] = Field(default_factory=list)
    step_count: int = 0
    evidence_count: int = 0  # Track evidence quality


class TaskList(BaseModel):
    """Container for multiple tasks"""
    tasks: List[Task]


class TaskValidation(BaseModel):
    """Validation result for a task"""
    done: bool
    has_evidence: bool = False
    reasoning: Optional[str] = None


class OverallValidation(BaseModel):
    """Validation for whether the entire workflow is complete"""
    done: bool
    evidence_quality: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: Optional[str] = None


class ToolCall(BaseModel):
    """Represents a tool call to be executed"""
    tool_name: str
    arguments: Dict[str, Any]


class ScratchpadEntry(BaseModel):
    """Log entry for debugging - similar to Dexter's scratchpad"""
    timestamp: datetime = Field(default_factory=datetime.now)
    type: Literal["init", "tool_call", "tool_result", "validation", "final"]
    tool_name: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    llm_summary: Optional[str] = None
    evidence_urls: List[str] = Field(default_factory=list)


class WorkflowResult(BaseModel):
    """Final output of a BD workflow"""
    goal: WorkflowGoal
    accounts: List[Account] = Field(default_factory=list)
    contacts: List[Contact] = Field(default_factory=list)
    summary: str
    cost: Optional[float] = None
    duration_seconds: Optional[float] = None
    scratchpad_file: Optional[str] = None
    
    def verified_contacts_count(self) -> int:
        """Count contacts with verified emails"""
        return sum(1 for c in self.contacts if c.is_verified())
    
    def accounts_with_signals_count(self) -> int:
        """Count accounts with verified signals"""
        return sum(1 for a in self.accounts if a.has_verified_signals())
