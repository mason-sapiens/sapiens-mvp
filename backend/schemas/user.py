"""User and profile schemas."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserProfile(BaseModel):
    """User profile information collected during onboarding."""

    target_role: str = Field(
        ...,
        description="Target job role (e.g., 'Product Manager', 'ML Engineer', 'Marketing Analyst')"
    )
    target_domain: str = Field(
        ...,
        description="Target industry/domain (e.g., 'FinTech', 'Healthcare', 'E-commerce')"
    )
    background: Optional[str] = Field(
        None,
        description="Educational and professional background"
    )
    interests: Optional[str] = Field(
        None,
        description="Specific interests or focus areas"
    )
    current_level: Optional[str] = Field(
        None,
        description="Current career level (e.g., 'student', 'entry-level', 'mid-level')"
    )
    skills: List[str] = Field(
        default_factory=list,
        description="Current skills and competencies"
    )
    time_commitment: Optional[str] = Field(
        None,
        description="Available time per week (e.g., '10-15 hours')"
    )


class User(BaseModel):
    """Core user model."""

    user_id: str
    email: Optional[EmailStr] = None
    name: Optional[str] = None

    profile: Optional[UserProfile] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Payment and access
    payment_status: str = "pending"  # pending, paid, expired
    access_expires_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "usr_123456",
                "email": "user@example.com",
                "name": "Jane Doe",
                "profile": {
                    "target_role": "Product Manager",
                    "target_domain": "FinTech",
                    "background": "Economics major, 1 year in consulting",
                    "interests": "Payment systems, financial inclusion"
                }
            }
        }
