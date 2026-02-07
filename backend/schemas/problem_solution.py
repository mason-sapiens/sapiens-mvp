"""Problem definition and solution design schemas."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ProblemDefinition(BaseModel):
    """
    User's problem definition, evaluated by Problem-Solution Tutor.
    Uses market/research lens for evaluation.
    """

    problem_id: str
    project_id: str
    user_id: str

    # User-defined problem
    problem_statement: str = Field(
        ...,
        description="Clear statement of the problem to solve"
    )

    target_audience: str = Field(
        ...,
        description="Who experiences this problem"
    )

    problem_context: str = Field(
        ...,
        description="Why this problem matters and current situation"
    )

    success_metrics: List[str] = Field(
        ...,
        description="How to measure if the problem is well-addressed"
    )

    # Tutor evaluation
    evaluation_passed: bool = False

    evaluation_feedback: Optional[str] = Field(
        None,
        description="Tutor's feedback on the problem definition"
    )

    market_relevance_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=10.0,
        description="How relevant this problem is to the market/domain"
    )

    feasibility_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=10.0,
        description="How feasible to address in 2-3 weeks"
    )

    clarity_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=10.0,
        description="How clearly the problem is defined"
    )

    improvement_suggestions: List[str] = Field(
        default_factory=list,
        description="Specific suggestions for improvement"
    )

    # Version control
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)


class SolutionDesign(BaseModel):
    """
    User's solution design, evaluated by Problem-Solution Tutor.
    Uses VC/practitioner lens for evaluation.
    """

    solution_id: str
    problem_id: str
    project_id: str
    user_id: str

    # User-defined solution
    solution_approach: str = Field(
        ...,
        description="High-level approach to solving the problem"
    )

    key_components: List[str] = Field(
        ...,
        description="Main components or elements of the solution"
    )

    methodology: str = Field(
        ...,
        description="Methods, frameworks, or processes to use"
    )

    expected_outcomes: List[str] = Field(
        ...,
        description="What this solution should achieve"
    )

    resource_requirements: Optional[str] = Field(
        None,
        description="Tools, data, or resources needed"
    )

    # Tutor evaluation
    evaluation_passed: bool = False

    evaluation_feedback: Optional[str] = Field(
        None,
        description="Tutor's feedback on the solution design"
    )

    logical_coherence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=10.0,
        description="How logically sound the solution is"
    )

    innovation_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=10.0,
        description="How innovative or differentiated the approach is"
    )

    implementation_feasibility_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=10.0,
        description="How feasible to implement in 2-3 weeks"
    )

    impact_potential_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=10.0,
        description="Potential impact if implemented well"
    )

    improvement_suggestions: List[str] = Field(
        default_factory=list,
        description="Specific suggestions for improvement"
    )

    # Version control
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)
