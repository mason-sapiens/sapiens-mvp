"""
Logging Module for comprehensive state and artifact tracking.
Serves as the source of truth for resume generation.
"""

import json
from typing import List, Optional, Dict, Any, Type, TypeVar
from datetime import datetime
from pathlib import Path
import structlog

from ..schemas.state import UserState, StateTransition
from ..schemas.project import Project
from ..schemas.problem_solution import ProblemDefinition, SolutionDesign
from ..schemas.execution import Milestone, ProgressUpdate, ExecutionPlan
from ..schemas.review import ArtifactReview, ResumePackage

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

T = TypeVar('T')


class LoggingModule:
    """
    Comprehensive logging and state persistence.

    Capabilities:
    - Log all user inputs and agent outputs
    - Track state transitions
    - Store milestones and progress updates
    - Persist final artifacts
    - Provide audit trail for resume generation

    Storage:
    - MVP: JSON files per user
    - Production: Database with proper indexing
    """

    def __init__(self, storage_dir: str = "./data/logs"):
        """Initialize logging module."""

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logger

    def _get_user_dir(self, user_id: str) -> Path:
        """Get storage directory for a user."""

        user_dir = self.storage_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def _save_json(self, file_path: Path, data: Any) -> None:
        """Save data as JSON."""

        with open(file_path, 'w') as f:
            if hasattr(data, 'model_dump'):
                json.dump(data.model_dump(), f, indent=2, default=str)
            else:
                json.dump(data, f, indent=2, default=str)

    def _load_json(self, file_path: Path, model_class: Type[T]) -> Optional[T]:
        """Load JSON data into a Pydantic model."""

        if not file_path.exists():
            return None

        with open(file_path, 'r') as f:
            data = json.load(f)
            return model_class(**data)

    # ========================================================================
    # User State Management
    # ========================================================================

    def save_user_state(self, state: UserState) -> None:
        """Save user state."""

        user_dir = self._get_user_dir(state.user_id)
        state_file = user_dir / "state.json"

        self._save_json(state_file, state)

        self.logger.info(
            "user_state_saved",
            user_id=state.user_id,
            current_state=state.current_state
        )

    def load_user_state(self, user_id: str) -> Optional[UserState]:
        """Load user state."""

        user_dir = self._get_user_dir(user_id)
        state_file = user_dir / "state.json"

        return self._load_json(state_file, UserState)

    def log_state_transition(self, transition: StateTransition, user_id: str) -> None:
        """Log a state transition."""

        user_dir = self._get_user_dir(user_id)
        transitions_file = user_dir / "transitions.jsonl"

        # Append to JSONL file
        with open(transitions_file, 'a') as f:
            f.write(json.dumps(transition.model_dump(), default=str) + '\n')

        self.logger.info(
            "state_transition",
            user_id=user_id,
            from_state=transition.from_state,
            to_state=transition.to_state,
            reason=transition.reason
        )

    # ========================================================================
    # Project Management
    # ========================================================================

    def save_project(self, project: Project) -> None:
        """Save project."""

        user_dir = self._get_user_dir(project.user_id)
        project_file = user_dir / f"project_{project.project_id}.json"

        self._save_json(project_file, project)

        self.logger.info(
            "project_saved",
            user_id=project.user_id,
            project_id=project.project_id,
            project_type=project.proposal.project_type
        )

    def load_project(self, user_id: str, project_id: str) -> Optional[Project]:
        """Load project."""

        user_dir = self._get_user_dir(user_id)
        project_file = user_dir / f"project_{project_id}.json"

        return self._load_json(project_file, Project)

    # ========================================================================
    # Problem and Solution
    # ========================================================================

    def save_problem_definition(self, problem: ProblemDefinition) -> None:
        """Save problem definition."""

        user_dir = self._get_user_dir(problem.user_id)
        problem_file = user_dir / f"problem_{problem.problem_id}.json"

        self._save_json(problem_file, problem)

        self.logger.info(
            "problem_saved",
            user_id=problem.user_id,
            problem_id=problem.problem_id,
            approved=problem.evaluation_passed
        )

    def load_problem_definition(
        self,
        user_id: str,
        problem_id: str
    ) -> Optional[ProblemDefinition]:
        """Load problem definition."""

        user_dir = self._get_user_dir(user_id)
        problem_file = user_dir / f"problem_{problem_id}.json"

        return self._load_json(problem_file, ProblemDefinition)

    def save_solution_design(self, solution: SolutionDesign) -> None:
        """Save solution design."""

        user_dir = self._get_user_dir(solution.user_id)
        solution_file = user_dir / f"solution_{solution.solution_id}.json"

        self._save_json(solution_file, solution)

        self.logger.info(
            "solution_saved",
            user_id=solution.user_id,
            solution_id=solution.solution_id,
            approved=solution.evaluation_passed
        )

    def load_solution_design(
        self,
        user_id: str,
        solution_id: str
    ) -> Optional[SolutionDesign]:
        """Load solution design."""

        user_dir = self._get_user_dir(user_id)
        solution_file = user_dir / f"solution_{solution_id}.json"

        return self._load_json(solution_file, SolutionDesign)

    # ========================================================================
    # Execution Tracking
    # ========================================================================

    def save_execution_plan(self, plan: ExecutionPlan) -> None:
        """Save execution plan."""

        user_dir = self._get_user_dir(plan.user_id)
        plan_file = user_dir / f"execution_plan_{plan.plan_id}.json"

        self._save_json(plan_file, plan)

        self.logger.info(
            "execution_plan_saved",
            user_id=plan.user_id,
            plan_id=plan.plan_id,
            total_milestones=len(plan.milestones)
        )

    def save_milestone(self, milestone: Milestone) -> None:
        """Save milestone."""

        user_dir = self._get_user_dir(milestone.user_id)
        milestone_file = user_dir / f"milestone_{milestone.milestone_id}.json"

        self._save_json(milestone_file, milestone)

    def load_milestone(self, user_id: str, milestone_id: str) -> Optional[Milestone]:
        """Load milestone."""

        user_dir = self._get_user_dir(user_id)
        milestone_file = user_dir / f"milestone_{milestone_id}.json"

        return self._load_json(milestone_file, Milestone)

    def save_progress_update(self, update: ProgressUpdate) -> None:
        """Save progress update."""

        user_dir = self._get_user_dir(update.user_id)
        updates_file = user_dir / f"progress_updates_{update.milestone_id}.jsonl"

        # Append to JSONL file
        with open(updates_file, 'a') as f:
            f.write(json.dumps(update.model_dump(), default=str) + '\n')

        self.logger.info(
            "progress_update_saved",
            user_id=update.user_id,
            milestone_id=update.milestone_id
        )

    # ========================================================================
    # Review and Resume
    # ========================================================================

    def save_artifact_review(self, review: ArtifactReview) -> None:
        """Save artifact review."""

        user_dir = self._get_user_dir(review.user_id)
        review_file = user_dir / f"review_{review.review_id}.json"

        self._save_json(review_file, review)

        self.logger.info(
            "review_saved",
            user_id=review.user_id,
            review_id=review.review_id,
            overall_score=review.overall_score
        )

    def load_artifact_review(
        self,
        user_id: str,
        review_id: str
    ) -> Optional[ArtifactReview]:
        """Load artifact review."""

        user_dir = self._get_user_dir(user_id)
        review_file = user_dir / f"review_{review_id}.json"

        return self._load_json(review_file, ArtifactReview)

    def save_resume_package(self, resume: ResumePackage) -> None:
        """Save resume package."""

        user_dir = self._get_user_dir(resume.user_id)
        resume_file = user_dir / f"resume_{resume.resume_id}.json"

        self._save_json(resume_file, resume)

        self.logger.info(
            "resume_saved",
            user_id=resume.user_id,
            resume_id=resume.resume_id,
            num_bullets=len(resume.resume_bullets)
        )

    # ========================================================================
    # Conversation Logging
    # ========================================================================

    def log_user_message(self, user_id: str, message: str, metadata: Dict[str, Any] = None) -> None:
        """Log user message."""

        user_dir = self._get_user_dir(user_id)
        conversation_file = user_dir / "conversation.jsonl"

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "user_message",
            "message": message,
            "metadata": metadata or {}
        }

        with open(conversation_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def log_agent_response(
        self,
        user_id: str,
        agent_name: str,
        response: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Log agent response."""

        user_dir = self._get_user_dir(user_id)
        conversation_file = user_dir / "conversation.jsonl"

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "agent_response",
            "agent": agent_name,
            "response": response,
            "metadata": metadata or {}
        }

        with open(conversation_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def get_conversation_history(self, user_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history."""

        user_dir = self._get_user_dir(user_id)
        conversation_file = user_dir / "conversation.jsonl"

        if not conversation_file.exists():
            return []

        history = []
        with open(conversation_file, 'r') as f:
            for line in f:
                history.append(json.loads(line))

        if limit:
            history = history[-limit:]

        return history
