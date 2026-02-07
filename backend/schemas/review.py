"""Review and resume generation schemas."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ArtifactSubmission(BaseModel):
    """User's submitted final artifacts."""

    artifact_type: str  # e.g., "report", "presentation", "prototype"
    artifact_url: Optional[str] = None
    artifact_description: str
    file_name: Optional[str] = None


class ArtifactReview(BaseModel):
    """
    Objective evaluation of final artifacts by Reviewer agent.
    Uses the evaluation criteria defined in the project proposal.
    """

    review_id: str
    project_id: str
    user_id: str

    submitted_artifacts: List[ArtifactSubmission]

    # Overall evaluation
    overall_score: float = Field(
        ge=0.0,
        le=10.0,
        description="Overall quality score"
    )

    overall_feedback: str = Field(
        ...,
        description="High-level assessment of the work"
    )

    # Criterion-by-criterion evaluation
    criterion_scores: Dict[str, float] = Field(
        ...,
        description="Score for each evaluation criterion (0-10)"
    )

    criterion_feedback: Dict[str, str] = Field(
        ...,
        description="Detailed feedback for each criterion"
    )

    # Strengths and improvements
    strengths: List[str] = Field(
        ...,
        description="What was done well"
    )

    areas_for_improvement: List[str] = Field(
        ...,
        description="What could be improved"
    )

    # Recruiter perspective
    recruiter_appeal_assessment: str = Field(
        ...,
        description="How this work would appeal to recruiters"
    )

    skills_demonstrated: List[str] = Field(
        ...,
        description="Skills clearly demonstrated in the work"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)

    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResumeBullet(BaseModel):
    """
    A single resume bullet point.
    Generated from actual work done, not aspirational claims.
    """

    bullet_text: str = Field(
        ...,
        description="Action-oriented resume bullet with metrics where possible"
    )

    skills_highlighted: List[str] = Field(
        ...,
        description="Skills this bullet showcases"
    )

    evidence_source: str = Field(
        ...,
        description="Reference to the specific work that supports this bullet"
    )

    bullet_type: str = Field(
        ...,
        description="Category (e.g., 'research', 'analysis', 'design', 'execution')"
    )


class ResumePackage(BaseModel):
    """
    Complete resume generation output.
    Grounded in actual work done during the project.
    """

    resume_id: str
    project_id: str
    user_id: str
    review_id: str

    # Resume content
    project_title: str
    project_one_liner: str = Field(
        ...,
        description="One-sentence project description for resume header"
    )

    resume_bullets: List[ResumeBullet] = Field(
        ...,
        min_length=3,
        max_length=5,
        description="3-5 strong resume bullets"
    )

    # Additional content
    project_description: str = Field(
        ...,
        description="2-3 sentence project description for cover letters"
    )

    suggested_skills_section: List[str] = Field(
        ...,
        description="Skills to add to the resume skills section"
    )

    interview_talking_points: List[str] = Field(
        ...,
        description="Key points to discuss in interviews"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)

    metadata: Dict[str, Any] = Field(default_factory=dict)
