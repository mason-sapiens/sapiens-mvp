"""
Orchestrator - the brain of the system.

Manages user state, coordinates agents, and controls state transitions.
NO agent calls another agent directly - all goes through Orchestrator.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import structlog

from .state_machine import StateMachine
from ..schemas.state import UserState, StateType, StateTransition
from ..schemas.user import User, UserProfile
from ..schemas.project import Project
from ..schemas.problem_solution import ProblemDefinition, SolutionDesign
from ..schemas.execution import Milestone, ExecutionPlan
from ..schemas.agent_io import *
from ..modules.rag import RAGModule
from ..modules.logging import LoggingModule
from ..agents import (
    MainChatAgent,
    ProjectGeneratorAgent,
    ProblemSolutionTutorAgent,
    ExecutionCoachAgent,
    ReviewerAgent
)

logger = structlog.get_logger()


class Orchestrator:
    """
    Central controller for the multi-agent system.

    Responsibilities:
    - Maintain user state
    - Decide state transitions
    - Route requests to appropriate agents
    - Coordinate agent interactions
    - Persist all data

    Agents are stateless - Orchestrator holds all state.
    """

    def __init__(
        self,
        rag_module: RAGModule,
        logging_module: LoggingModule,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize orchestrator.

        Args:
            rag_module: RAG module for knowledge retrieval
            logging_module: Logging module for persistence
            openai_api_key: OpenAI API key
        """

        self.rag_module = rag_module
        self.logging_module = logging_module
        self.state_machine = StateMachine()

        # Initialize agents
        self.main_chat = MainChatAgent(
            rag_module=rag_module,
            logging_module=logging_module,
            openai_api_key=openai_api_key
        )

        self.project_generator = ProjectGeneratorAgent(
            rag_module=rag_module,
            logging_module=logging_module,
            openai_api_key=openai_api_key
        )

        self.problem_solution_tutor = ProblemSolutionTutorAgent(
            rag_module=rag_module,
            logging_module=logging_module,
            openai_api_key=openai_api_key
        )

        self.execution_coach = ExecutionCoachAgent(
            rag_module=rag_module,
            logging_module=logging_module,
            openai_api_key=openai_api_key
        )

        self.reviewer = ReviewerAgent(
            rag_module=rag_module,
            logging_module=logging_module,
            openai_api_key=openai_api_key
        )

        logger.info("Orchestrator initialized")

    # ========================================================================
    # Main Entry Point
    # ========================================================================

    def process_user_message(
        self,
        user_id: str,
        message: str
    ) -> str:
        """
        Main entry point for processing user messages.

        Args:
            user_id: User ID
            message: User's message

        Returns:
            Response message for user
        """

        try:
            # Log user message
            self.logging_module.log_user_message(user_id, message)

            # Load or create user state
            user_state = self.logging_module.load_user_state(user_id)
            if not user_state:
                user_state = self._create_new_user_state(user_id)

            # Process based on current state
            response = self._route_by_state(user_state, message)

            # Save updated state
            user_state.last_activity_at = datetime.utcnow()
            self.logging_module.save_user_state(user_state)

            # Log agent response
            self.logging_module.log_agent_response(
                user_id,
                "MainChat",
                response
            )

            return response

        except Exception as e:
            logger.error("Error processing message", user_id=user_id, error=str(e))
            return f"I encountered an error processing your message. Please try again. Error: {str(e)}"

    def _create_new_user_state(self, user_id: str) -> UserState:
        """Create new user state."""

        user_state = UserState(
            user_id=user_id,
            current_state=StateType.ONBOARDING
        )

        self.logging_module.save_user_state(user_state)

        logger.info("Created new user state", user_id=user_id)

        return user_state

    # ========================================================================
    # State Routing
    # ========================================================================

    def _route_by_state(self, user_state: UserState, message: str) -> str:
        """
        Route message based on current state.

        Args:
            user_state: Current user state
            message: User's message

        Returns:
            Response message
        """

        if user_state.current_state == StateType.ONBOARDING:
            return self._handle_onboarding(user_state, message)

        elif user_state.current_state == StateType.PROJECT_GENERATION:
            return self._handle_project_generation(user_state, message)

        elif user_state.current_state == StateType.PROBLEM_DEFINITION:
            return self._handle_problem_definition(user_state, message)

        elif user_state.current_state == StateType.SOLUTION_DESIGN:
            return self._handle_solution_design(user_state, message)

        elif user_state.current_state == StateType.EXECUTION:
            return self._handle_execution(user_state, message)

        elif user_state.current_state == StateType.REVIEW:
            return self._handle_review(user_state, message)

        elif user_state.current_state == StateType.COMPLETED:
            return self._handle_completed(user_state, message)

        else:
            return "I'm not sure how to help with that. Let's start over."

    # ========================================================================
    # State Handlers
    # ========================================================================

    def _handle_onboarding(self, user_state: UserState, message: str) -> str:
        """Handle onboarding state."""

        # First time? Show welcome
        if not user_state.target_role:
            welcome = self.main_chat.generate_message("welcome", {})

            # Check if message contains role info
            if message and len(message) > 10:
                # Try to extract role from initial message
                user_state.target_role = message
                user_state.context["onboarding_step"] = "domain"
                self.logging_module.save_user_state(user_state)

                return welcome + "\n\nGreat! Now, what industry or domain are you targeting? (e.g., FinTech, Healthcare, E-commerce)"

            return welcome

        # Collect target domain
        elif not user_state.target_domain:
            user_state.target_domain = message
            user_state.context["onboarding_step"] = "background"
            self.logging_module.save_user_state(user_state)

            return """Perfect! To design the best project for you, it would help to know:

**What's your background?** (e.g., education, previous experience)

(You can skip this by typing "skip")"""

        # Collect background (optional)
        elif not user_state.background:
            if message.lower() != "skip":
                user_state.background = message
            user_state.context["onboarding_step"] = "interests"
            self.logging_module.save_user_state(user_state)

            return """Great! Last question:

**Any specific interests or focus areas?** (e.g., "AI applications", "growth strategies", "user research")

(You can skip this by typing "skip")"""

        # Collect interests (optional) and transition
        else:
            if message.lower() != "skip":
                user_state.interests = message
            self.logging_module.save_user_state(user_state)

            # Transition to project generation
            return self._transition_to_project_generation(user_state)

    def _handle_project_generation(self, user_state: UserState, message: str) -> str:
        """Handle project generation state."""

        # Check if we need to generate a proposal
        if not user_state.project_id:
            # Generate project
            request_id = f"req_{uuid.uuid4().hex[:8]}"

            project_input = ProjectGeneratorInput(
                user_id=user_state.user_id,
                request_id=request_id,
                target_role=user_state.target_role,
                target_domain=user_state.target_domain,
                background=user_state.background,
                interests=user_state.interests
            )

            output = self.project_generator.process(project_input)

            if not output.success or not output.proposal:
                return "I had trouble generating a project proposal. Let me try again..."

            # Create and save project
            project = Project(
                project_id=f"proj_{uuid.uuid4().hex[:8]}",
                user_id=user_state.user_id,
                proposal=output.proposal,
                status="proposed"
            )

            self.logging_module.save_project(project)

            user_state.project_id = project.project_id
            self.logging_module.save_user_state(user_state)

            # Present proposal
            return self.main_chat.generate_message(
                "project_proposal",
                {"proposal": output.proposal}
            )

        # User is responding to proposal
        else:
            parsed = self.main_chat.parse_user_input(message, "approval")

            if parsed["approved"]:
                # Approve project and transition
                user_state.project_approved = True
                self.logging_module.save_user_state(user_state)

                return self._transition_to_problem_definition(user_state)

            elif parsed["approved"] is False:
                # Generate new proposal
                user_state.project_id = None
                self.logging_module.save_user_state(user_state)

                return "No problem! Let me create a different project for you...\n\n" + \
                       self._handle_project_generation(user_state, "")

            else:
                return "I didn't catch that. Do you approve this project? (Yes/No)"

    def _handle_problem_definition(self, user_state: UserState, message: str) -> str:
        """Handle problem definition state."""

        # First time? Prompt for problem
        if not user_state.context.get("problem_submitted"):
            if user_state.context.get("awaiting_problem"):
                # User is submitting problem definition
                return self._evaluate_problem(user_state, message)
            else:
                # Show problem prompt
                user_state.context["awaiting_problem"] = True
                self.logging_module.save_user_state(user_state)

                return self.main_chat.generate_message("problem_prompt", {})

        # Problem was evaluated but not approved
        elif not user_state.problem_approved:
            # User is resubmitting
            return self._evaluate_problem(user_state, message)

        else:
            return "Your problem definition is already approved! Moving forward..."

    def _evaluate_problem(self, user_state: UserState, message: str) -> str:
        """Evaluate problem definition."""

        # Parse problem from message (simplified - in production, use structured form)
        problem = ProblemDefinition(
            problem_id=user_state.problem_id or f"prob_{uuid.uuid4().hex[:8]}",
            project_id=user_state.project_id,
            user_id=user_state.user_id,
            problem_statement=message[:500],  # First part as statement
            target_audience="To be refined",
            problem_context=message[500:] if len(message) > 500 else message,
            success_metrics=["To be defined"]
        )

        # Evaluate with tutor
        request_id = f"req_{uuid.uuid4().hex[:8]}"

        tutor_input = ProblemSolutionTutorInput(
            user_id=user_state.user_id,
            request_id=request_id,
            project_id=user_state.project_id,
            mode="problem",
            problem_definition=problem
        )

        tutor_output = self.problem_solution_tutor.process(tutor_input)

        # Update problem with evaluation
        problem.evaluation_passed = tutor_output.evaluation_passed
        problem.evaluation_feedback = tutor_output.overall_feedback

        for key, value in tutor_output.scores.items():
            setattr(problem, f"{key}_score", value)

        problem.improvement_suggestions = tutor_output.improvement_suggestions

        # Save problem
        if not user_state.problem_id:
            user_state.problem_id = problem.problem_id

        self.logging_module.save_problem_definition(problem)
        user_state.context["problem_submitted"] = True

        if tutor_output.evaluation_passed:
            problem.approved_at = datetime.utcnow()
            self.logging_module.save_problem_definition(problem)

            user_state.problem_approved = True
            self.logging_module.save_user_state(user_state)

            # Transition to solution design
            return self.main_chat.generate_message(
                "problem_feedback",
                {"feedback": tutor_output.model_dump(), "passed": True}
            ) + "\n\n" + self._transition_to_solution_design(user_state)

        else:
            self.logging_module.save_user_state(user_state)

            return self.main_chat.generate_message(
                "problem_feedback",
                {"feedback": tutor_output.model_dump(), "passed": False}
            )

    def _handle_solution_design(self, user_state: UserState, message: str) -> str:
        """Handle solution design state."""

        # First time? Prompt for solution
        if not user_state.context.get("solution_submitted"):
            if user_state.context.get("awaiting_solution"):
                # User is submitting solution
                return self._evaluate_solution(user_state, message)
            else:
                # Show solution prompt
                user_state.context["awaiting_solution"] = True
                self.logging_module.save_user_state(user_state)

                return self.main_chat.generate_message("solution_prompt", {})

        # Solution was evaluated but not approved
        elif not user_state.solution_approved:
            # User is resubmitting
            return self._evaluate_solution(user_state, message)

        else:
            return "Your solution design is already approved! Moving to execution..."

    def _evaluate_solution(self, user_state: UserState, message: str) -> str:
        """Evaluate solution design."""

        # Load problem context
        problem = self.logging_module.load_problem_definition(
            user_state.user_id,
            user_state.problem_id
        )

        # Parse solution (simplified)
        solution = SolutionDesign(
            solution_id=user_state.solution_id or f"sol_{uuid.uuid4().hex[:8]}",
            problem_id=user_state.problem_id,
            project_id=user_state.project_id,
            user_id=user_state.user_id,
            solution_approach=message[:500],
            key_components=["Component 1", "Component 2"],  # Parse from message
            methodology=message[500:] if len(message) > 500 else "To be refined",
            expected_outcomes=["Outcome 1"]
        )

        # Evaluate with tutor
        request_id = f"req_{uuid.uuid4().hex[:8]}"

        tutor_input = ProblemSolutionTutorInput(
            user_id=user_state.user_id,
            request_id=request_id,
            project_id=user_state.project_id,
            mode="solution",
            solution_design=solution,
            problem_context=problem
        )

        tutor_output = self.problem_solution_tutor.process(tutor_input)

        # Update solution with evaluation
        solution.evaluation_passed = tutor_output.evaluation_passed
        solution.evaluation_feedback = tutor_output.overall_feedback

        for key, value in tutor_output.scores.items():
            setattr(solution, f"{key}_score", value)

        solution.improvement_suggestions = tutor_output.improvement_suggestions

        # Save solution
        if not user_state.solution_id:
            user_state.solution_id = solution.solution_id

        self.logging_module.save_solution_design(solution)
        user_state.context["solution_submitted"] = True

        if tutor_output.evaluation_passed:
            solution.approved_at = datetime.utcnow()
            self.logging_module.save_solution_design(solution)

            user_state.solution_approved = True
            self.logging_module.save_user_state(user_state)

            # Transition to execution
            return self.main_chat.generate_message(
                "solution_feedback",
                {"feedback": tutor_output.model_dump(), "passed": True}
            ) + "\n\n" + self._transition_to_execution(user_state)

        else:
            self.logging_module.save_user_state(user_state)

            return self.main_chat.generate_message(
                "solution_feedback",
                {"feedback": tutor_output.model_dump(), "passed": False}
            )

    def _handle_execution(self, user_state: UserState, message: str) -> str:
        """Handle execution state."""

        # Create execution plan if not exists
        if not user_state.context.get("execution_plan_created"):
            return self._create_execution_plan(user_state)

        # Handle progress updates
        return self._process_progress_update(user_state, message)

    def _create_execution_plan(self, user_state: UserState) -> str:
        """Create execution plan."""

        # Load problem and solution
        problem = self.logging_module.load_problem_definition(
            user_state.user_id,
            user_state.problem_id
        )
        solution = self.logging_module.load_solution_design(
            user_state.user_id,
            user_state.solution_id
        )

        # Create plan with execution coach
        request_id = f"req_{uuid.uuid4().hex[:8]}"

        coach_input = ExecutionCoachInput(
            user_id=user_state.user_id,
            request_id=request_id,
            project_id=user_state.project_id,
            action="create_plan",
            problem_definition=problem,
            solution_design=solution
        )

        coach_output = self.execution_coach.process(coach_input)

        if not coach_output.success:
            return "I had trouble creating your execution plan. Let me try again..."

        # Save milestones
        for milestone in coach_output.milestones:
            self.logging_module.save_milestone(milestone)

        # Update state
        user_state.context["execution_plan_created"] = True
        user_state.total_milestones = len(coach_output.milestones)
        user_state.current_milestone_id = coach_output.milestones[0].milestone_id
        user_state.execution_started_at = datetime.utcnow()
        self.logging_module.save_user_state(user_state)

        # Present plan
        return self.main_chat.generate_message(
            "execution_plan",
            {
                "milestones": coach_output.milestones,
                "feedback": coach_output.feedback
            }
        )

    def _process_progress_update(self, user_state: UserState, message: str) -> str:
        """Process progress update from user."""

        # Get current milestone
        current_milestone = self.logging_module.load_milestone(
            user_state.user_id,
            user_state.current_milestone_id
        )

        if not current_milestone:
            return "I couldn't find your current milestone. Let me help you get back on track."

        # Process update with execution coach
        request_id = f"req_{uuid.uuid4().hex[:8]}"

        coach_input = ExecutionCoachInput(
            user_id=user_state.user_id,
            request_id=request_id,
            project_id=user_state.project_id,
            action="update_progress",
            current_milestone_id=user_state.current_milestone_id,
            progress_update=message,
            blockers=[],
            all_milestones=[current_milestone]
        )

        coach_output = self.execution_coach.process(coach_input)

        # Update milestone status
        if coach_output.milestone_status_update:
            current_milestone.status = coach_output.milestone_status_update
            self.logging_module.save_milestone(current_milestone)

            if coach_output.milestone_status_update.value == "completed":
                user_state.milestones_completed += 1

                # Check if all milestones done
                if user_state.milestones_completed >= user_state.total_milestones:
                    self.logging_module.save_user_state(user_state)
                    return coach_output.feedback + "\n\n" + self._transition_to_review(user_state)

        self.logging_module.save_user_state(user_state)

        return self.main_chat.generate_message(
            "milestone_update",
            {
                "feedback": coach_output.feedback,
                "next_action": coach_output.next_action,
                "stagnation": coach_output.stagnation_detected,
                "tips": coach_output.tips
            }
        )

    def _handle_review(self, user_state: UserState, message: str) -> str:
        """Handle review state."""

        # Request artifacts if not submitted
        if not user_state.context.get("artifacts_submitted"):
            if user_state.context.get("awaiting_artifacts"):
                # User is submitting artifacts
                return self._review_artifacts(user_state, message)
            else:
                user_state.context["awaiting_artifacts"] = True
                self.logging_module.save_user_state(user_state)

                return self.main_chat.generate_message("review_request", {})

        # Artifacts reviewed, waiting for resume generation approval
        elif not user_state.resume_generated:
            parsed = self.main_chat.parse_user_input(message, "approval")

            if parsed["approved"]:
                return self._generate_resume(user_state)
            else:
                return "Take your time reviewing the feedback. Let me know when you're ready for resume content! (Yes)"

        else:
            return "Your resume content has been generated! Is there anything else I can help with?"

    def _review_artifacts(self, user_state: UserState, message: str) -> str:
        """Review submitted artifacts."""

        # Parse artifacts (simplified)
        artifacts = [
            ArtifactSubmission(
                artifact_type="Project Deliverable",
                artifact_description=message,
                artifact_url=None
            )
        ]

        # Load project proposal
        project = self.logging_module.load_project(user_state.user_id, user_state.project_id)

        # Review with reviewer agent
        request_id = f"req_{uuid.uuid4().hex[:8]}"

        reviewer_input = ReviewerInput(
            user_id=user_state.user_id,
            request_id=request_id,
            project_id=user_state.project_id,
            action="review_artifacts",
            submitted_artifacts=artifacts,
            project_proposal=project.proposal if project else None
        )

        reviewer_output = self.reviewer.process(reviewer_input)

        if not reviewer_output.success or not reviewer_output.review:
            return "I had trouble reviewing your artifacts. Please try again."

        # Save review
        self.logging_module.save_artifact_review(reviewer_output.review)

        user_state.review_id = reviewer_output.review.review_id
        user_state.context["artifacts_submitted"] = True
        self.logging_module.save_user_state(user_state)

        return self.main_chat.generate_message(
            "review_feedback",
            {"review": reviewer_output.review}
        )

    def _generate_resume(self, user_state: UserState) -> str:
        """Generate resume content."""

        # Load review
        review = self.logging_module.load_artifact_review(
            user_state.user_id,
            user_state.review_id
        )

        # Load problem and solution
        problem = self.logging_module.load_problem_definition(
            user_state.user_id,
            user_state.problem_id
        )
        solution = self.logging_module.load_solution_design(
            user_state.user_id,
            user_state.solution_id
        )

        # Generate resume
        request_id = f"req_{uuid.uuid4().hex[:8]}"

        reviewer_input = ReviewerInput(
            user_id=user_state.user_id,
            request_id=request_id,
            project_id=user_state.project_id,
            action="generate_resume",
            problem_definition=problem,
            solution_design=solution,
            artifact_review=review
        )

        reviewer_output = self.reviewer.process(reviewer_input)

        if not reviewer_output.success:
            return "I had trouble generating your resume content. Please try again."

        # Mark resume as generated
        user_state.resume_generated = True
        self.logging_module.save_user_state(user_state)

        # Transition to completed
        response = self.main_chat.generate_message(
            "resume_delivery",
            {
                "resume": {
                    "project_title": reviewer_output.project_title,
                    "project_one_liner": reviewer_output.project_one_liner,
                    "project_description": reviewer_output.project_description,
                    "bullets": reviewer_output.resume_bullets,
                    "suggested_skills": reviewer_output.suggested_skills,
                    "talking_points": reviewer_output.interview_talking_points
                }
            }
        )

        return response + "\n\n" + self._transition_to_completed(user_state)

    def _handle_completed(self, user_state: UserState, message: str) -> str:
        """Handle completed state."""

        return self.main_chat.generate_message("completion", {})

    # ========================================================================
    # State Transitions
    # ========================================================================

    def _transition_to(
        self,
        user_state: UserState,
        to_state: StateType,
        reason: str
    ) -> None:
        """
        Transition to a new state.

        Args:
            user_state: Current user state
            to_state: Target state
            reason: Reason for transition
        """

        # Validate transition
        can_transition, message = self.state_machine.can_transition(
            user_state.current_state,
            to_state,
            user_state.model_dump()
        )

        if not can_transition:
            logger.warning(
                "Invalid transition attempted",
                user_id=user_state.user_id,
                from_state=user_state.current_state,
                to_state=to_state,
                reason=message
            )
            return

        # Log transition
        transition = StateTransition(
            from_state=user_state.current_state,
            to_state=to_state,
            reason=reason
        )

        self.logging_module.log_state_transition(transition, user_state.user_id)

        # Update state
        user_state.previous_state = user_state.current_state
        user_state.current_state = to_state
        user_state.state_entered_at = datetime.utcnow()

        self.logging_module.save_user_state(user_state)

        logger.info(
            "State transition",
            user_id=user_state.user_id,
            from_state=transition.from_state,
            to_state=transition.to_state
        )

    def _transition_to_project_generation(self, user_state: UserState) -> str:
        """Transition to project generation."""

        self._transition_to(
            user_state,
            StateType.PROJECT_GENERATION,
            "Onboarding completed"
        )

        return "Perfect! Now let me design a project tailored specifically for you...\n\n" + \
               self._handle_project_generation(user_state, "")

    def _transition_to_problem_definition(self, user_state: UserState) -> str:
        """Transition to problem definition."""

        self._transition_to(
            user_state,
            StateType.PROBLEM_DEFINITION,
            "Project approved"
        )

        return self._handle_problem_definition(user_state, "")

    def _transition_to_solution_design(self, user_state: UserState) -> str:
        """Transition to solution design."""

        self._transition_to(
            user_state,
            StateType.SOLUTION_DESIGN,
            "Problem approved"
        )

        return self._handle_solution_design(user_state, "")

    def _transition_to_execution(self, user_state: UserState) -> str:
        """Transition to execution."""

        self._transition_to(
            user_state,
            StateType.EXECUTION,
            "Solution approved"
        )

        return self._handle_execution(user_state, "")

    def _transition_to_review(self, user_state: UserState) -> str:
        """Transition to review."""

        self._transition_to(
            user_state,
            StateType.REVIEW,
            "All milestones completed"
        )

        return self._handle_review(user_state, "")

    def _transition_to_completed(self, user_state: UserState) -> str:
        """Transition to completed."""

        self._transition_to(
            user_state,
            StateType.COMPLETED,
            "Resume generated"
        )

        return ""  # Message already generated by resume delivery
