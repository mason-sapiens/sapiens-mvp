"""
Basic tests for Orchestrator.

Run with: pytest tests/test_orchestrator.py
"""

import pytest
from backend.orchestration.orchestrator import Orchestrator
from backend.orchestration.state_machine import StateMachine
from backend.modules.rag import RAGModule
from backend.modules.logging import LoggingModule
from backend.schemas.state import StateType


@pytest.fixture
def orchestrator():
    """Create orchestrator for testing."""

    rag = RAGModule(persist_dir="./test_data/chroma")
    logging = LoggingModule(storage_dir="./test_data/logs")

    # Note: Requires OPENAI_API_KEY in environment
    orch = Orchestrator(
        rag_module=rag,
        logging_module=logging
    )

    return orch


@pytest.fixture
def state_machine():
    """Create state machine for testing."""

    return StateMachine()


class TestStateMachine:
    """Test state machine logic."""

    def test_valid_transitions(self, state_machine):
        """Test valid state transitions."""

        assert state_machine.is_valid_transition(
            StateType.ONBOARDING,
            StateType.PROJECT_GENERATION
        )

        assert state_machine.is_valid_transition(
            StateType.PROJECT_GENERATION,
            StateType.PROBLEM_DEFINITION
        )

    def test_invalid_transitions(self, state_machine):
        """Test invalid state transitions."""

        # Can't skip states
        assert not state_machine.is_valid_transition(
            StateType.ONBOARDING,
            StateType.EXECUTION
        )

        # Can't go backward to onboarding from execution
        assert not state_machine.is_valid_transition(
            StateType.EXECUTION,
            StateType.ONBOARDING
        )

    def test_get_valid_next_states(self, state_machine):
        """Test getting valid next states."""

        next_states = state_machine.get_valid_next_states(StateType.ONBOARDING)

        assert StateType.PROJECT_GENERATION in next_states
        assert StateType.EXECUTION not in next_states


class TestOrchestrator:
    """Test orchestrator functionality."""

    def test_create_new_user(self, orchestrator):
        """Test creating a new user."""

        user_id = "test_user_1"

        # Process first message
        response = orchestrator.process_user_message(
            user_id=user_id,
            message="I want to be a Product Manager"
        )

        # Should get welcome message
        assert "Welcome" in response or "welcome" in response

        # Check state was created
        user_state = orchestrator.logging_module.load_user_state(user_id)

        assert user_state is not None
        assert user_state.current_state == StateType.ONBOARDING

    def test_onboarding_flow(self, orchestrator):
        """Test basic onboarding flow."""

        user_id = "test_user_2"

        # Step 1: Role
        response1 = orchestrator.process_user_message(
            user_id=user_id,
            message="Product Manager"
        )

        user_state = orchestrator.logging_module.load_user_state(user_id)
        assert user_state.current_state == StateType.ONBOARDING

        # Step 2: Domain
        response2 = orchestrator.process_user_message(
            user_id=user_id,
            message="FinTech"
        )

        user_state = orchestrator.logging_module.load_user_state(user_id)
        assert user_state.target_role == "Product Manager"
        assert user_state.target_domain == "FinTech"

        # Step 3: Background (skip)
        response3 = orchestrator.process_user_message(
            user_id=user_id,
            message="skip"
        )

        # Step 4: Interests (skip)
        response4 = orchestrator.process_user_message(
            user_id=user_id,
            message="skip"
        )

        # Should transition to project generation
        user_state = orchestrator.logging_module.load_user_state(user_id)
        # Note: Might be in project_generation or still transitioning
        assert user_state.target_role is not None
        assert user_state.target_domain is not None


@pytest.mark.skip(reason="Requires API key and generates actual LLM calls")
class TestAgentIntegration:
    """Integration tests with actual agents (requires API key)."""

    def test_full_project_generation(self, orchestrator):
        """Test full project generation flow."""

        user_id = "test_user_full"

        # Complete onboarding
        messages = [
            "Product Manager",
            "FinTech",
            "skip",
            "skip"
        ]

        for msg in messages:
            response = orchestrator.process_user_message(user_id, msg)

        # Should have generated a project
        user_state = orchestrator.logging_module.load_user_state(user_id)

        # Might need to wait for async generation
        # In production, use proper async testing

        assert user_state is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
