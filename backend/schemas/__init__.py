"""Schema definitions for the Sapiens MVP system."""

from .state import UserState, StateType
from .user import User, UserProfile
from .project import Project, ProjectType, ProjectProposal
from .problem_solution import ProblemDefinition, SolutionDesign
from .execution import Milestone, MilestoneStatus, ProgressUpdate
from .review import ArtifactReview, ResumeBullet
from .agent_io import (
    AgentInput,
    AgentOutput,
    ProjectGeneratorInput,
    ProjectGeneratorOutput,
    ProblemSolutionTutorInput,
    ProblemSolutionTutorOutput,
    ExecutionCoachInput,
    ExecutionCoachOutput,
    ReviewerInput,
    ReviewerOutput,
)

__all__ = [
    # State
    "UserState",
    "StateType",
    # User
    "User",
    "UserProfile",
    # Project
    "Project",
    "ProjectType",
    "ProjectProposal",
    # Problem and Solution
    "ProblemDefinition",
    "SolutionDesign",
    # Execution
    "Milestone",
    "MilestoneStatus",
    "ProgressUpdate",
    # Review
    "ArtifactReview",
    "ResumeBullet",
    # Agent I/O
    "AgentInput",
    "AgentOutput",
    "ProjectGeneratorInput",
    "ProjectGeneratorOutput",
    "ProblemSolutionTutorInput",
    "ProblemSolutionTutorOutput",
    "ExecutionCoachInput",
    "ExecutionCoachOutput",
    "ReviewerInput",
    "ReviewerOutput",
]
