"""Execution and milestone tracking schemas."""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field


class MilestoneStatus(str, Enum):
    """Status of a milestone."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class Milestone(BaseModel):
    """
    A concrete, time-bound milestone in the execution phase.
    Created by Execution Coach.
    """

    milestone_id: str
    project_id: str
    user_id: str

    title: str = Field(
        ...,
        description="Clear, actionable milestone title"
    )

    description: str = Field(
        ...,
        description="What needs to be accomplished"
    )

    deliverable: str = Field(
        ...,
        description="Concrete output expected from this milestone"
    )

    order: int = Field(
        ...,
        ge=1,
        description="Sequence order of this milestone"
    )

    status: MilestoneStatus = MilestoneStatus.NOT_STARTED

    # Timing
    estimated_days: float = Field(
        ...,
        gt=0,
        description="Estimated days to complete"
    )

    target_date: Optional[date] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Dependencies
    depends_on: List[str] = Field(
        default_factory=list,
        description="IDs of milestones that must be completed first"
    )

    # Next action (always present for active milestones)
    next_action: Optional[str] = Field(
        None,
        description="The ONE clear next action to take"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class ProgressUpdate(BaseModel):
    """
    User's progress update for a milestone.
    Evaluated by Execution Coach.
    """

    update_id: str
    milestone_id: str
    user_id: str

    update_text: str = Field(
        ...,
        description="What the user has accomplished or attempted"
    )

    status_change: Optional[MilestoneStatus] = None

    blockers: List[str] = Field(
        default_factory=list,
        description="Any blockers or challenges encountered"
    )

    artifacts_uploaded: List[str] = Field(
        default_factory=list,
        description="URLs or references to uploaded work"
    )

    # Coach response
    coach_feedback: Optional[str] = None
    coach_next_action: Optional[str] = None
    stagnation_detected: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)

    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class ExecutionPlan(BaseModel):
    """Complete execution plan with all milestones."""

    plan_id: str
    project_id: str
    user_id: str

    milestones: List[Milestone]

    total_estimated_days: float
    target_completion_date: date

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
