"""
State Machine definition.
Defines valid states and transitions.
"""

from typing import Dict, List, Set
from ..schemas.state import StateType


class StateMachine:
    """
    Defines the state machine for the user journey.

    States:
    - onboarding: Collecting user profile
    - project_generation: Creating project proposal
    - problem_definition: Defining the problem
    - solution_design: Designing the solution
    - execution: Working on milestones
    - review: Reviewing artifacts
    - completed: Journey complete

    Transitions are explicit and controlled.
    """

    def __init__(self):
        """Initialize state machine."""

        # Define valid transitions
        self.transitions: Dict[StateType, Set[StateType]] = {
            StateType.ONBOARDING: {
                StateType.PROJECT_GENERATION
            },
            StateType.PROJECT_GENERATION: {
                StateType.PROBLEM_DEFINITION,
                StateType.ONBOARDING  # Can go back if user wants to change profile
            },
            StateType.PROBLEM_DEFINITION: {
                StateType.SOLUTION_DESIGN,
                StateType.PROJECT_GENERATION  # Can go back if user wants different project
            },
            StateType.SOLUTION_DESIGN: {
                StateType.EXECUTION,
                StateType.PROBLEM_DEFINITION  # Can go back to revise problem
            },
            StateType.EXECUTION: {
                StateType.REVIEW,
                StateType.SOLUTION_DESIGN  # Can go back if major pivot needed
            },
            StateType.REVIEW: {
                StateType.COMPLETED,
                StateType.EXECUTION  # Can go back for revisions
            },
            StateType.COMPLETED: set()  # Terminal state
        }

    def is_valid_transition(
        self,
        from_state: StateType,
        to_state: StateType
    ) -> bool:
        """
        Check if a state transition is valid.

        Args:
            from_state: Current state
            to_state: Desired next state

        Returns:
            True if transition is valid
        """

        if from_state not in self.transitions:
            return False

        return to_state in self.transitions[from_state]

    def get_valid_next_states(self, current_state: StateType) -> Set[StateType]:
        """
        Get all valid next states from current state.

        Args:
            current_state: Current state

        Returns:
            Set of valid next states
        """

        return self.transitions.get(current_state, set())

    def get_required_data(self, state: StateType) -> List[str]:
        """
        Get required data fields for a state.

        Args:
            state: State to check

        Returns:
            List of required field names
        """

        requirements = {
            StateType.ONBOARDING: ["target_role", "target_domain"],
            StateType.PROJECT_GENERATION: ["target_role", "target_domain"],
            StateType.PROBLEM_DEFINITION: ["project_id", "project_approved"],
            StateType.SOLUTION_DESIGN: ["problem_id", "problem_approved"],
            StateType.EXECUTION: ["solution_id", "solution_approved"],
            StateType.REVIEW: ["milestones_completed"],
            StateType.COMPLETED: ["review_id", "resume_generated"]
        }

        return requirements.get(state, [])

    def can_transition(
        self,
        from_state: StateType,
        to_state: StateType,
        user_state_data: Dict
    ) -> tuple[bool, str]:
        """
        Check if transition is allowed given current data.

        Args:
            from_state: Current state
            to_state: Desired next state
            user_state_data: Current user state data

        Returns:
            (can_transition, reason)
        """

        # Check if transition is structurally valid
        if not self.is_valid_transition(from_state, to_state):
            return False, f"Invalid transition from {from_state} to {to_state}"

        # Check if required data is present
        required_fields = self.get_required_data(to_state)

        for field in required_fields:
            if field not in user_state_data or not user_state_data[field]:
                return False, f"Missing required field: {field}"

        return True, "Transition allowed"
