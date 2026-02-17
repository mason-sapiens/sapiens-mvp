"""User state definitions."""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class StateType(str, Enum):
    """Valid states in the user journey."""

    ONBOARDING = "onboarding"
    PROJECT_GENERATION = "project_generation"
    PROBLEM_DEFINITION = "problem_definition"
    SOLUTION_DESIGN = "solution_design"
    EXECUTION = "execution"
    REVIEW = "review"
    COMPLETED = "completed"


class UserState(BaseModel):
    """
    Complete state of a user in the system.
    The Orchestrator uses this as the single source of truth.
    """

    user_id: str  # Actual user ID
    room_id: Optional[str] = None  # Room ID for conversation separation
    current_state: StateType
    previous_state: Optional[StateType] = None

    # State timestamps
    state_entered_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)

    # Onboarding data
    target_role: Optional[str] = None
    target_domain: Optional[str] = None
    background: Optional[str] = None
    interests: Optional[str] = None

    # Project data
    project_id: Optional[str] = None
    project_approved: bool = False

    # Problem-solution data
    problem_id: Optional[str] = None
    problem_approved: bool = False
    solution_id: Optional[str] = None
    solution_approved: bool = False

    # Execution data
    execution_started_at: Optional[datetime] = None
    current_milestone_id: Optional[str] = None
    milestones_completed: int = 0
    total_milestones: int = 0

    # Review data
    review_id: Optional[str] = None
    resume_generated: bool = False

    # Context and metadata
    context: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class StateTransition(BaseModel):
    """Represents a state transition decision."""

    from_state: StateType
    to_state: StateType
    reason: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict)
