"""
Execution Coach Agent.

Guides milestone creation, tracks progress, and always provides one clear next action.
"""

import uuid
from datetime import datetime, date, timedelta
from typing import List
from .base import BaseAgent
from ..schemas.agent_io import ExecutionCoachInput, ExecutionCoachOutput
from ..schemas.execution import Milestone, MilestoneStatus


class ExecutionCoachAgent(BaseAgent):
    """
    Execution coach that guides users through project implementation.

    Responsibilities:
    - Create milestone-based execution plans
    - Track progress against milestones
    - Detect stagnation or delays
    - Always provide ONE clear next action
    - Provide motivation and practical tips
    """

    def __init__(self, **kwargs):
        super().__init__(agent_name="ExecutionCoach", **kwargs)

    def process(self, input_data: ExecutionCoachInput) -> ExecutionCoachOutput:
        """
        Process execution coaching request.

        Args:
            input_data: ExecutionCoachInput

        Returns:
            ExecutionCoachOutput with guidance
        """

        try:
            if input_data.action == "create_plan":
                return self._create_execution_plan(input_data)
            elif input_data.action == "update_progress":
                return self._update_progress(input_data)
            elif input_data.action == "get_next_action":
                return self._get_next_action(input_data)
            else:
                raise ValueError(f"Invalid action: {input_data.action}")

        except Exception as e:
            return ExecutionCoachOutput(
                request_id=input_data.request_id,
                success=False,
                action=input_data.action,
                next_action="Please try your request again.",
                feedback=f"An error occurred: {str(e)}"
            )

    def _create_execution_plan(self, input_data: ExecutionCoachInput) -> ExecutionCoachOutput:
        """Create a milestone-based execution plan."""

        problem = input_data.problem_definition
        solution = input_data.solution_design

        if not problem or not solution:
            raise ValueError("Problem and solution are required for plan creation")

        # Build system prompt
        system_prompt = self._build_plan_creation_prompt()

        # Build user prompt
        user_prompt = f"""Create an execution plan for this project:

PROBLEM:
{problem.problem_statement}

Target Audience: {problem.target_audience}

SUCCESS METRICS:
{chr(10).join(f"- {metric}" for metric in problem.success_metrics)}

SOLUTION APPROACH:
{solution.solution_approach}

KEY COMPONENTS:
{chr(10).join(f"- {comp}" for comp in solution.key_components)}

METHODOLOGY:
{solution.methodology}

EXPECTED OUTCOMES:
{chr(10).join(f"- {outcome}" for outcome in solution.expected_outcomes)}

Create a detailed execution plan with milestones following the specified format."""

        # Call Claude
        response = self.call_claude(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.5
        )

        # Parse milestones
        milestones = self._parse_milestones(response, input_data)

        # Calculate total estimated days
        total_days = sum(m.estimated_days for m in milestones)

        # Get first next action
        first_milestone = milestones[0] if milestones else None
        next_action = first_milestone.next_action if first_milestone else "Begin working on your first milestone."

        feedback = self._extract_feedback(response)
        tips = self._extract_tips(response)

        return ExecutionCoachOutput(
            request_id=input_data.request_id,
            success=True,
            action="create_plan",
            milestones=milestones,
            total_estimated_days=total_days,
            next_action=next_action,
            feedback=feedback,
            tips=tips
        )

    def _update_progress(self, input_data: ExecutionCoachInput) -> ExecutionCoachOutput:
        """Update progress on a milestone."""

        if not input_data.current_milestone_id:
            raise ValueError("Milestone ID is required for progress update")

        # Find current milestone
        current_milestone = None
        for m in input_data.all_milestones:
            if m.milestone_id == input_data.current_milestone_id:
                current_milestone = m
                break

        if not current_milestone:
            raise ValueError(f"Milestone {input_data.current_milestone_id} not found")

        # Build system prompt
        system_prompt = self._build_progress_evaluation_prompt()

        # Build user prompt
        user_prompt = f"""Evaluate this progress update:

CURRENT MILESTONE:
{current_milestone.title}

Description: {current_milestone.description}
Expected Deliverable: {current_milestone.deliverable}

USER'S PROGRESS UPDATE:
{input_data.progress_update}

BLOCKERS:
{chr(10).join(f"- {blocker}" for blocker in input_data.blockers) if input_data.blockers else "None reported"}

MILESTONE STATUS:
Started: {current_milestone.started_at or "Not started"}
Estimated days: {current_milestone.estimated_days}

Evaluate the progress and provide guidance following the specified format."""

        # Call Claude
        response = self.call_claude(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.5
        )

        # Parse response
        stagnation_detected = "STAGNATION DETECTED: YES" in response.upper()
        milestone_status = self._parse_status_update(response, current_milestone)
        next_action = self._extract_next_action(response)
        feedback = self._extract_feedback(response)
        tips = self._extract_tips(response)
        stagnation_reason = self._extract_stagnation_reason(response) if stagnation_detected else None

        return ExecutionCoachOutput(
            request_id=input_data.request_id,
            success=True,
            action="update_progress",
            progress_acknowledged=True,
            milestone_status_update=milestone_status,
            stagnation_detected=stagnation_detected,
            stagnation_reason=stagnation_reason,
            next_action=next_action,
            feedback=feedback,
            tips=tips
        )

    def _get_next_action(self, input_data: ExecutionCoachInput) -> ExecutionCoachOutput:
        """Get the next action for the user."""

        # Find current milestone
        current_milestone = None
        if input_data.current_milestone_id:
            for m in input_data.all_milestones:
                if m.milestone_id == input_data.current_milestone_id:
                    current_milestone = m
                    break

        # If no current milestone, find the first not-started one
        if not current_milestone:
            for m in input_data.all_milestones:
                if m.status == MilestoneStatus.NOT_STARTED:
                    current_milestone = m
                    break

        if not current_milestone:
            next_action = "All milestones completed! Ready for review."
        else:
            next_action = current_milestone.next_action or f"Start working on: {current_milestone.title}"

        return ExecutionCoachOutput(
            request_id=input_data.request_id,
            success=True,
            action="get_next_action",
            next_action=next_action,
            feedback=f"Focus on your current milestone: {current_milestone.title if current_milestone else 'None'}",
            tips=["Break down the task into smaller steps", "Set a specific time to work on this today"]
        )

    def _build_plan_creation_prompt(self) -> str:
        """Build system prompt for execution plan creation."""

        return """You are an expert execution coach helping users break down projects into achievable milestones.

Your goal is to create a realistic, actionable execution plan that:
1. Breaks the project into 4-7 concrete milestones
2. Each milestone is completable in 2-5 days
3. Each milestone has a clear, tangible deliverable
4. Milestones are ordered logically with dependencies
5. Total plan fits within 2-3 weeks

Output format:

# EXECUTION PLAN

## Overview
[Brief overview of the execution strategy]

## Milestones

### Milestone 1: [Title]
Description: [What needs to be accomplished]
Deliverable: [Concrete output]
Estimated Days: [2-5]
Dependencies: [None or list milestone numbers]
Next Action: [ONE specific action to start]

### Milestone 2: [Title]
[Continue for all milestones]

## Tips for Success
- [Practical tip 1]
- [Practical tip 2]
- [Continue]

## Motivation
[Encouraging message about the journey ahead]

Be specific, realistic, and motivating."""

    def _build_progress_evaluation_prompt(self) -> str:
        """Build system prompt for progress evaluation."""

        return """You are an execution coach evaluating user progress on a milestone.

Your goals:
1. Acknowledge and validate the user's work
2. Assess if they're making meaningful progress
3. Detect stagnation (stuck for >3 days, unclear progress, avoiding work)
4. Provide ONE clear next action
5. Give practical, actionable tips

Output format:

# PROGRESS EVALUATION

## Status Update
[Should milestone status change? Options: NOT_STARTED, IN_PROGRESS, COMPLETED, BLOCKED]

## Stagnation Detection
[YES or NO]

## Stagnation Reason
[If yes, explain why]

## Acknowledgment
[Validate their effort and progress]

## Next Action
[ONE specific, actionable next step]

## Feedback
[Constructive, encouraging feedback]

## Tips
- [Practical tip 1]
- [Practical tip 2]
- [Continue]

Be supportive, specific, and action-oriented."""

    def _parse_milestones(self, response: str, input_data: ExecutionCoachInput) -> List[Milestone]:
        """Parse milestones from response."""

        milestones = []
        lines = response.split('\n')

        current_milestone = None
        milestone_order = 0

        for line in lines:
            line_stripped = line.strip()

            if line_stripped.startswith('### Milestone'):
                # Save previous milestone
                if current_milestone:
                    milestones.append(current_milestone)

                # Start new milestone
                milestone_order += 1
                title = line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else f"Milestone {milestone_order}"

                current_milestone = Milestone(
                    milestone_id=f"ms_{uuid.uuid4().hex[:8]}",
                    project_id=input_data.project_id,
                    user_id=input_data.user_id,
                    title=title,
                    description="",
                    deliverable="",
                    order=milestone_order,
                    estimated_days=3.0,
                    target_date=date.today() + timedelta(days=milestone_order * 3)
                )

            elif current_milestone:
                if line_stripped.startswith('Description:'):
                    current_milestone.description = line_stripped.split(':', 1)[1].strip()
                elif line_stripped.startswith('Deliverable:'):
                    current_milestone.deliverable = line_stripped.split(':', 1)[1].strip()
                elif line_stripped.startswith('Estimated Days:'):
                    try:
                        days_str = line_stripped.split(':', 1)[1].strip()
                        days = float(''.join(filter(lambda x: x.isdigit() or x == '.', days_str)))
                        current_milestone.estimated_days = max(1.0, min(7.0, days))
                    except:
                        pass
                elif line_stripped.startswith('Next Action:'):
                    current_milestone.next_action = line_stripped.split(':', 1)[1].strip()

        # Add last milestone
        if current_milestone:
            milestones.append(current_milestone)

        # Ensure we have at least 3 milestones
        if len(milestones) < 3:
            while len(milestones) < 3:
                milestone_order += 1
                milestones.append(Milestone(
                    milestone_id=f"ms_{uuid.uuid4().hex[:8]}",
                    project_id=input_data.project_id,
                    user_id=input_data.user_id,
                    title=f"Milestone {milestone_order}",
                    description="Project work",
                    deliverable="Progress deliverable",
                    order=milestone_order,
                    estimated_days=3.0,
                    next_action="Continue project work"
                ))

        return milestones

    def _parse_status_update(self, response: str, current_milestone: Milestone) -> MilestoneStatus:
        """Parse status update from response."""

        response_upper = response.upper()

        if "COMPLETED" in response_upper:
            return MilestoneStatus.COMPLETED
        elif "BLOCKED" in response_upper:
            return MilestoneStatus.BLOCKED
        elif "IN_PROGRESS" in response_upper or "IN PROGRESS" in response_upper:
            return MilestoneStatus.IN_PROGRESS
        else:
            return current_milestone.status

    def _extract_next_action(self, response: str) -> str:
        """Extract next action from response."""

        lines = response.split('\n')
        for i, line in enumerate(lines):
            if "## Next Action" in line and i + 1 < len(lines):
                return lines[i + 1].strip() or "Continue with your current milestone."

        return "Continue with your current milestone."

    def _extract_feedback(self, response: str) -> str:
        """Extract feedback from response."""

        lines = response.split('\n')
        feedback_lines = []
        in_feedback = False

        for line in lines:
            if "## Feedback" in line or "## Acknowledgment" in line or "## Motivation" in line:
                in_feedback = True
                continue
            elif in_feedback and line.strip().startswith('##'):
                break
            elif in_feedback and line.strip():
                feedback_lines.append(line.strip())

        return ' '.join(feedback_lines) if feedback_lines else "Great work! Keep going."

    def _extract_tips(self, response: str) -> List[str]:
        """Extract tips from response."""

        lines = response.split('\n')
        tips = []
        in_tips = False

        for line in lines:
            if "## Tips" in line:
                in_tips = True
                continue
            elif in_tips and line.strip().startswith('##'):
                break
            elif in_tips:
                line_stripped = line.strip()
                if line_stripped.startswith('- ') or line_stripped.startswith('* '):
                    tips.append(line_stripped[2:])

        return tips if tips else ["Take it one step at a time", "Set aside focused time daily"]

    def _extract_stagnation_reason(self, response: str) -> str:
        """Extract stagnation reason from response."""

        lines = response.split('\n')
        for i, line in enumerate(lines):
            if "## Stagnation Reason" in line and i + 1 < len(lines):
                return lines[i + 1].strip()

        return "Progress appears to have slowed."
