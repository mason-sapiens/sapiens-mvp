"""
Agent input/output schemas.
Each agent has explicit input and output contracts.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .project import ProjectType, ProjectProposal
from .problem_solution import ProblemDefinition, SolutionDesign
from .execution import Milestone, MilestoneStatus
from .review import ArtifactReview, ResumeBullet


# ============================================================================
# Base Agent Schemas
# ============================================================================

class AgentInput(BaseModel):
    """Base class for all agent inputs."""

    user_id: str
    request_id: str = Field(
        ...,
        description="Unique ID for this request for tracking"
    )


class AgentOutput(BaseModel):
    """Base class for all agent outputs."""

    request_id: str
    success: bool
    message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Project Generator Agent
# ============================================================================

class ProjectGeneratorInput(AgentInput):
    """
    Input for Project Generator agent.
    Generates a role-aligned, 2-3 week project.
    """

    target_role: str = Field(
        ...,
        description="Target job role"
    )

    target_domain: str = Field(
        ...,
        description="Target industry/domain"
    )

    background: Optional[str] = Field(
        None,
        description="User's background and experience"
    )

    interests: Optional[str] = Field(
        None,
        description="User's specific interests"
    )

    previous_proposals: List[str] = Field(
        default_factory=list,
        description="IDs of previously rejected proposals (to avoid duplicates)"
    )


class ProjectGeneratorOutput(AgentOutput):
    """
    Output from Project Generator agent.
    Contains a complete project proposal.
    """

    proposal: Optional[ProjectProposal] = None
    reasoning: str = Field(
        ...,
        description="Why this project was chosen"
    )

    alternative_options: List[str] = Field(
        default_factory=list,
        description="Brief descriptions of other options considered"
    )


# ============================================================================
# Problem-Solution Tutor Agent
# ============================================================================

class ProblemSolutionTutorInput(AgentInput):
    """
    Input for Problem-Solution Tutor agent.
    Handles both problem evaluation and solution evaluation.
    """

    project_id: str

    mode: str = Field(
        ...,
        description="Either 'problem' or 'solution'"
    )

    # For problem evaluation
    problem_definition: Optional[ProblemDefinition] = None

    # For solution evaluation
    solution_design: Optional[SolutionDesign] = None
    problem_context: Optional[ProblemDefinition] = Field(
        None,
        description="The approved problem definition (for solution evaluation)"
    )


class ProblemSolutionTutorOutput(AgentOutput):
    """
    Output from Problem-Solution Tutor agent.
    Contains evaluation results and feedback.
    """

    mode: str  # 'problem' or 'solution'

    evaluation_passed: bool

    # Scores
    scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Evaluation scores for different criteria"
    )

    # Feedback
    overall_feedback: str

    strengths: List[str] = Field(
        default_factory=list,
        description="What was done well"
    )

    improvement_suggestions: List[str] = Field(
        default_factory=list,
        description="Specific, actionable suggestions"
    )

    # Guidance
    next_steps: str = Field(
        ...,
        description="What the user should do next"
    )

    example_improvements: Optional[str] = Field(
        None,
        description="Concrete examples of how to improve (if not passed)"
    )


# ============================================================================
# Execution Coach Agent
# ============================================================================

class ExecutionCoachInput(AgentInput):
    """
    Input for Execution Coach agent.
    Handles milestone creation, progress tracking, and guidance.
    """

    project_id: str

    action: str = Field(
        ...,
        description="Action type: 'create_plan', 'update_progress', 'get_next_action'"
    )

    # For plan creation
    problem_definition: Optional[ProblemDefinition] = None
    solution_design: Optional[SolutionDesign] = None

    # For progress updates
    current_milestone_id: Optional[str] = None
    progress_update: Optional[str] = None
    blockers: List[str] = Field(default_factory=list)

    # Current state
    completed_milestones: List[str] = Field(default_factory=list)
    all_milestones: List[Milestone] = Field(default_factory=list)


class ExecutionCoachOutput(AgentOutput):
    """
    Output from Execution Coach agent.
    Always includes one clear next action.
    """

    action: str  # Which action was performed

    # For plan creation
    milestones: List[Milestone] = Field(
        default_factory=list,
        description="Generated milestones"
    )

    total_estimated_days: Optional[float] = None

    # For progress updates
    progress_acknowledged: bool = False
    milestone_status_update: Optional[MilestoneStatus] = None

    stagnation_detected: bool = False
    stagnation_reason: Optional[str] = None

    # Always present: the ONE next action
    next_action: str = Field(
        ...,
        description="Clear, specific next action for the user"
    )

    # Guidance and motivation
    feedback: str = Field(
        ...,
        description="Encouraging and specific feedback"
    )

    tips: List[str] = Field(
        default_factory=list,
        description="Practical tips for the current phase"
    )


# ============================================================================
# Reviewer & Resume Agent
# ============================================================================

class ArtifactSubmission(BaseModel):
    """A submitted artifact for review."""

    artifact_type: str
    artifact_url: Optional[str] = None
    artifact_description: str
    file_name: Optional[str] = None


class ReviewerInput(AgentInput):
    """
    Input for Reviewer & Resume agent.
    Evaluates final artifacts and generates resume content.
    """

    project_id: str

    action: str = Field(
        ...,
        description="Action type: 'review_artifacts', 'generate_resume'"
    )

    # For artifact review
    submitted_artifacts: List[ArtifactSubmission] = Field(
        default_factory=list
    )

    project_proposal: Optional[Any] = Field(
        None,
        description="Original project proposal with evaluation criteria"
    )

    # Context for resume generation
    problem_definition: Optional[ProblemDefinition] = None
    solution_design: Optional[SolutionDesign] = None
    completed_milestones: List[Milestone] = Field(default_factory=list)
    artifact_review: Optional[ArtifactReview] = None


class ReviewerOutput(AgentOutput):
    """
    Output from Reviewer & Resume agent.
    Contains objective evaluation and/or resume content.
    """

    action: str  # Which action was performed

    # For artifact review
    review: Optional[ArtifactReview] = None

    # For resume generation
    resume_bullets: List[ResumeBullet] = Field(
        default_factory=list,
        description="Generated resume bullets grounded in actual work"
    )

    project_title: Optional[str] = None
    project_one_liner: Optional[str] = None
    project_description: Optional[str] = None

    suggested_skills: List[str] = Field(
        default_factory=list,
        description="Skills to add to resume"
    )

    interview_talking_points: List[str] = Field(
        default_factory=list,
        description="Key points for interviews"
    )

    # Guidance
    next_steps: str = Field(
        ...,
        description="What the user should do next with this feedback"
    )
