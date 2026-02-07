"""
Database models for PostgreSQL.
SQLAlchemy ORM models for production database.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, JSON, Text, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..schemas.state import StateType
from ..schemas.project import ProjectType
from ..schemas.execution import MilestoneStatus

Base = declarative_base()


class UserStateModel(Base):
    """User state table."""

    __tablename__ = "user_states"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True, nullable=False, index=True)

    # State
    current_state = Column(SQLEnum(StateType), nullable=False)
    previous_state = Column(SQLEnum(StateType), nullable=True)

    # Timestamps
    state_entered_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Onboarding data
    target_role = Column(String, nullable=True)
    target_domain = Column(String, nullable=True)
    background = Column(Text, nullable=True)
    interests = Column(Text, nullable=True)

    # Project data
    project_id = Column(String, nullable=True)
    project_approved = Column(Boolean, default=False)

    # Problem-solution data
    problem_id = Column(String, nullable=True)
    problem_approved = Column(Boolean, default=False)
    solution_id = Column(String, nullable=True)
    solution_approved = Column(Boolean, default=False)

    # Execution data
    execution_started_at = Column(DateTime, nullable=True)
    current_milestone_id = Column(String, nullable=True)
    milestones_completed = Column(Integer, default=0)
    total_milestones = Column(Integer, default=0)

    # Review data
    review_id = Column(String, nullable=True)
    resume_generated = Column(Boolean, default=False)

    # Context and metadata
    context = Column(JSON, default=dict)
    meta_data = Column(JSON, default=dict)


class ProjectModel(Base):
    """Project table."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)

    # Project data (stored as JSON)
    proposal = Column(JSON, nullable=False)

    status = Column(String, default="proposed")

    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    problem_id = Column(String, nullable=True)
    solution_id = Column(String, nullable=True)

    meta_data = Column(JSON, default=dict)


class ProblemDefinitionModel(Base):
    """Problem definition table."""

    __tablename__ = "problem_definitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(String, unique=True, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)

    problem_statement = Column(Text, nullable=False)
    target_audience = Column(Text, nullable=False)
    problem_context = Column(Text, nullable=False)
    success_metrics = Column(JSON, nullable=False)

    # Evaluation
    evaluation_passed = Column(Boolean, default=False)
    evaluation_feedback = Column(Text, nullable=True)

    market_relevance_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    feasibility_score = Column(Float, nullable=True)

    improvement_suggestions = Column(JSON, default=list)

    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

    meta_data = Column(JSON, default=dict)


class SolutionDesignModel(Base):
    """Solution design table."""

    __tablename__ = "solution_designs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    solution_id = Column(String, unique=True, nullable=False, index=True)
    problem_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)

    solution_approach = Column(Text, nullable=False)
    key_components = Column(JSON, nullable=False)
    methodology = Column(Text, nullable=False)
    expected_outcomes = Column(JSON, nullable=False)
    resource_requirements = Column(Text, nullable=True)

    # Evaluation
    evaluation_passed = Column(Boolean, default=False)
    evaluation_feedback = Column(Text, nullable=True)

    logical_coherence_score = Column(Float, nullable=True)
    innovation_score = Column(Float, nullable=True)
    implementation_feasibility_score = Column(Float, nullable=True)
    impact_potential_score = Column(Float, nullable=True)

    improvement_suggestions = Column(JSON, default=list)

    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

    meta_data = Column(JSON, default=dict)


class MilestoneModel(Base):
    """Milestone table."""

    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    milestone_id = Column(String, unique=True, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    deliverable = Column(Text, nullable=False)

    order = Column(Integer, nullable=False)
    status = Column(SQLEnum(MilestoneStatus), default=MilestoneStatus.NOT_STARTED)

    estimated_days = Column(Float, nullable=False)
    target_date = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    depends_on = Column(JSON, default=list)
    next_action = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    meta_data = Column(JSON, default=dict)


class ConversationLogModel(Base):
    """Conversation log table."""

    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    message_type = Column(String, nullable=False)  # user_message, agent_response

    # For user messages
    message = Column(Text, nullable=True)

    # For agent responses
    agent = Column(String, nullable=True)
    response = Column(Text, nullable=True)

    meta_data = Column(JSON, default=dict)


class ArtifactReviewModel(Base):
    """Artifact review table."""

    __tablename__ = "artifact_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(String, unique=True, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)

    submitted_artifacts = Column(JSON, nullable=False)

    overall_score = Column(Float, nullable=False)
    overall_feedback = Column(Text, nullable=False)

    criterion_scores = Column(JSON, nullable=False)
    criterion_feedback = Column(JSON, nullable=False)

    strengths = Column(JSON, nullable=False)
    areas_for_improvement = Column(JSON, nullable=False)

    recruiter_appeal_assessment = Column(Text, nullable=False)
    skills_demonstrated = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    meta_data = Column(JSON, default=dict)


class StateTransitionModel(Base):
    """State transition log table."""

    __tablename__ = "state_transitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)

    from_state = Column(SQLEnum(StateType), nullable=False)
    to_state = Column(SQLEnum(StateType), nullable=False)
    reason = Column(Text, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    data = Column(JSON, default=dict)
