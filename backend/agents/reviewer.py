"""
Reviewer & Resume Agent.

Objectively evaluates final artifacts and generates resume content grounded in actual work.
"""

import uuid
from typing import List
from .base import BaseAgent
from ..schemas.agent_io import ReviewerInput, ReviewerOutput, ArtifactSubmission
from ..schemas.review import ArtifactReview, ResumeBullet
from ..schemas.project import ProjectProposal


class ReviewerAgent(BaseAgent):
    """
    Reviews final artifacts and generates resume content.

    Responsibilities:
    - Objectively evaluate artifacts against criteria
    - Generate resume bullets grounded in actual work
    - Provide constructive feedback
    - No grade inflation - honest assessment
    """

    def __init__(self, **kwargs):
        super().__init__(agent_name="Reviewer", **kwargs)

    def process(self, input_data: ReviewerInput) -> ReviewerOutput:
        """
        Process review request.

        Args:
            input_data: ReviewerInput

        Returns:
            ReviewerOutput with review or resume content
        """

        try:
            if input_data.action == "review_artifacts":
                return self._review_artifacts(input_data)
            elif input_data.action == "generate_resume":
                return self._generate_resume(input_data)
            else:
                raise ValueError(f"Invalid action: {input_data.action}")

        except Exception as e:
            return ReviewerOutput(
                request_id=input_data.request_id,
                success=False,
                action=input_data.action,
                next_steps=f"An error occurred: {str(e)}"
            )

    def _review_artifacts(self, input_data: ReviewerInput) -> ReviewerOutput:
        """Review submitted artifacts."""

        if not input_data.submitted_artifacts:
            raise ValueError("No artifacts submitted for review")

        proposal = input_data.project_proposal

        # Build system prompt
        system_prompt = self._build_review_prompt()

        # Build user prompt
        user_prompt = self._build_review_user_prompt(input_data, proposal)

        # Call Claude
        response = self.call_claude(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3  # Lower for objective evaluation
        )

        # Parse review
        review = self._parse_review(response, input_data)

        next_steps = self._extract_next_steps(response)

        return ReviewerOutput(
            request_id=input_data.request_id,
            success=True,
            action="review_artifacts",
            review=review,
            next_steps=next_steps
        )

    def _generate_resume(self, input_data: ReviewerInput) -> ReviewerOutput:
        """Generate resume content from completed work."""

        if not input_data.artifact_review:
            raise ValueError("Artifact review is required for resume generation")

        # Build system prompt
        system_prompt = self._build_resume_prompt()

        # Build user prompt
        user_prompt = self._build_resume_user_prompt(input_data)

        # Call Claude
        response = self.call_claude(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.5
        )

        # Parse resume content
        resume_bullets = self._parse_resume_bullets(response, input_data)
        project_title = self._extract_project_title(response)
        project_one_liner = self._extract_project_one_liner(response)
        project_description = self._extract_project_description(response)
        suggested_skills = self._extract_suggested_skills(response)
        talking_points = self._extract_talking_points(response)
        next_steps = self._extract_next_steps(response)

        return ReviewerOutput(
            request_id=input_data.request_id,
            success=True,
            action="generate_resume",
            resume_bullets=resume_bullets,
            project_title=project_title,
            project_one_liner=project_one_liner,
            project_description=project_description,
            suggested_skills=suggested_skills,
            interview_talking_points=talking_points,
            next_steps=next_steps
        )

    def _build_review_prompt(self) -> str:
        """Build system prompt for artifact review."""

        return """You are an objective evaluator reviewing project artifacts.

Your goals:
1. Provide honest, constructive evaluation
2. Use the project's evaluation criteria
3. No grade inflation - be truthful about quality
4. Highlight both strengths and areas for improvement
5. Help the user understand how recruiters would view this work

Evaluation approach:
- Score each criterion on 0-10 scale (be honest, not generous)
- Overall score is weighted average
- Provide specific, actionable feedback
- Focus on what was actually delivered

Output format:

# ARTIFACT REVIEW

## Overall Assessment
[2-3 paragraphs of honest assessment]

## Overall Score
[0-10]

## Criterion Scores
[Criterion 1]: [0-10]
[Criterion 2]: [0-10]
[Continue for each criterion]

## Criterion Feedback
### [Criterion 1]
[Specific feedback on this criterion]

### [Criterion 2]
[Continue for each]

## Strengths
- [Specific strength 1]
- [Specific strength 2]
- [Continue]

## Areas for Improvement
- [Specific area 1]
- [Specific area 2]
- [Continue]

## Recruiter Appeal
[How would recruiters view this work? Be honest.]

## Skills Demonstrated
- [Skill 1 with evidence]
- [Skill 2 with evidence]
- [Continue]

## Next Steps
[What to do with this feedback]

Be honest, specific, and constructive."""

    def _build_resume_prompt(self) -> str:
        """Build system prompt for resume generation."""

        return """You are a resume writer creating content grounded in actual completed work.

Critical rules:
1. ONLY include claims supported by actual deliverables
2. Use action verbs and quantify where possible
3. Focus on impact and skills demonstrated
4. 3-5 strong bullets maximum
5. Each bullet must reference actual work done

Resume bullet format:
- Start with strong action verb (Conducted, Designed, Analyzed, Built, etc.)
- Include what was done and the context
- Add metrics or scope where available
- Highlight the outcome or impact

Output format:

# RESUME PACKAGE

## Project Title
[Professional title for resume]

## Project One-Liner
[One sentence description]

## Project Description
[2-3 sentences for cover letters]

## Resume Bullets

### Bullet 1
Text: [Full resume bullet]
Skills: [Skill 1, Skill 2, Skill 3]
Evidence: [Reference to actual work]
Type: [research/analysis/design/execution]

### Bullet 2
[Continue for 3-5 bullets]

## Skills Section
[Skills to add to resume skills section]
- [Skill 1]
- [Skill 2]
- [Continue]

## Interview Talking Points
[Key points to discuss in interviews]
- [Point 1]
- [Point 2]
- [Continue]

## Next Steps
[How to use this resume content]

Be honest - only include what can be backed up by the actual work."""

    def _build_review_user_prompt(self, input_data: ReviewerInput, proposal) -> str:
        """Build user prompt for artifact review."""

        prompt = "Review these submitted artifacts:\n\n"

        # Add artifacts
        prompt += "## SUBMITTED ARTIFACTS\n\n"
        for i, artifact in enumerate(input_data.submitted_artifacts, 1):
            prompt += f"### Artifact {i}: {artifact.artifact_type}\n"
            prompt += f"Description: {artifact.artifact_description}\n"
            if artifact.artifact_url:
                prompt += f"URL: {artifact.artifact_url}\n"
            if artifact.file_name:
                prompt += f"File: {artifact.file_name}\n"
            prompt += "\n"

        # Add evaluation criteria
        if proposal:
            prompt += "\n## EVALUATION CRITERIA\n\n"
            if hasattr(proposal, 'evaluation_criteria'):
                for i, criterion in enumerate(proposal.evaluation_criteria, 1):
                    prompt += f"{i}. {criterion}\n"

        # Add project context
        if input_data.problem_definition:
            prompt += f"\n## PROJECT CONTEXT\n\n"
            prompt += f"Problem: {input_data.problem_definition.problem_statement}\n"

        if input_data.solution_design:
            prompt += f"\nSolution Approach: {input_data.solution_design.solution_approach}\n"

        prompt += "\n\nProvide a thorough, honest evaluation following the specified format."

        return prompt

    def _build_resume_user_prompt(self, input_data: ReviewerInput) -> str:
        """Build user prompt for resume generation."""

        prompt = "Generate resume content based on this completed project:\n\n"

        # Add problem
        if input_data.problem_definition:
            problem = input_data.problem_definition
            prompt += f"## PROBLEM ADDRESSED\n\n"
            prompt += f"{problem.problem_statement}\n\n"
            prompt += f"Target Audience: {problem.target_audience}\n\n"

        # Add solution
        if input_data.solution_design:
            solution = input_data.solution_design
            prompt += f"## SOLUTION IMPLEMENTED\n\n"
            prompt += f"Approach: {solution.solution_approach}\n\n"
            prompt += f"Key Components:\n"
            for comp in solution.key_components:
                prompt += f"- {comp}\n"
            prompt += f"\nMethodology: {solution.methodology}\n\n"

        # Add milestones completed
        if input_data.completed_milestones:
            prompt += f"## WORK COMPLETED\n\n"
            for milestone in input_data.completed_milestones:
                prompt += f"- {milestone.title}: {milestone.deliverable}\n"
            prompt += "\n"

        # Add review
        if input_data.artifact_review:
            review = input_data.artifact_review
            prompt += f"## ARTIFACT REVIEW\n\n"
            prompt += f"Overall Score: {review.overall_score}/10\n\n"
            prompt += f"Skills Demonstrated:\n"
            for skill in review.skills_demonstrated:
                prompt += f"- {skill}\n"
            prompt += "\n"

        prompt += "\nGenerate resume content following the specified format. Only include claims supported by actual work."

        return prompt

    def _parse_review(self, response: str, input_data: ReviewerInput) -> ArtifactReview:
        """Parse review from response."""

        overall_score = self._extract_overall_score(response)
        overall_feedback = self._extract_overall_feedback(response)
        criterion_scores = self._extract_criterion_scores(response)
        criterion_feedback = self._extract_criterion_feedback(response)
        strengths = self._extract_strengths(response)
        improvements = self._extract_improvements(response)
        recruiter_appeal = self._extract_recruiter_appeal(response)
        skills = self._extract_skills_demonstrated(response)

        return ArtifactReview(
            review_id=f"rev_{uuid.uuid4().hex[:8]}",
            project_id=input_data.project_id,
            user_id=input_data.user_id,
            submitted_artifacts=input_data.submitted_artifacts,
            overall_score=overall_score,
            overall_feedback=overall_feedback,
            criterion_scores=criterion_scores,
            criterion_feedback=criterion_feedback,
            strengths=strengths,
            areas_for_improvement=improvements,
            recruiter_appeal_assessment=recruiter_appeal,
            skills_demonstrated=skills
        )

    def _parse_resume_bullets(self, response: str, input_data: ReviewerInput) -> List[ResumeBullet]:
        """Parse resume bullets from response."""

        bullets = []
        lines = response.split('\n')

        current_bullet = None
        current_field = None

        for line in lines:
            line_stripped = line.strip()

            if line_stripped.startswith('### Bullet'):
                # Save previous bullet
                if current_bullet:
                    bullets.append(current_bullet)

                # Start new bullet
                current_bullet = {
                    'text': '',
                    'skills': [],
                    'evidence': '',
                    'type': 'execution'
                }

            elif current_bullet:
                if line_stripped.startswith('Text:'):
                    current_bullet['text'] = line_stripped.split(':', 1)[1].strip()
                elif line_stripped.startswith('Skills:'):
                    skills_str = line_stripped.split(':', 1)[1].strip()
                    current_bullet['skills'] = [s.strip() for s in skills_str.split(',')]
                elif line_stripped.startswith('Evidence:'):
                    current_bullet['evidence'] = line_stripped.split(':', 1)[1].strip()
                elif line_stripped.startswith('Type:'):
                    current_bullet['type'] = line_stripped.split(':', 1)[1].strip()

        # Add last bullet
        if current_bullet and current_bullet['text']:
            bullets.append(current_bullet)

        # Convert to ResumeBullet objects
        resume_bullets = []
        for b in bullets:
            resume_bullets.append(ResumeBullet(
                bullet_text=b['text'],
                skills_highlighted=b['skills'],
                evidence_source=b['evidence'],
                bullet_type=b['type']
            ))

        # Ensure we have at least 3 bullets
        while len(resume_bullets) < 3:
            resume_bullets.append(ResumeBullet(
                bullet_text="Completed project deliverables",
                skills_highlighted=["Project execution"],
                evidence_source="Project completion",
                bullet_type="execution"
            ))

        return resume_bullets[:5]  # Max 5 bullets

    def _extract_overall_score(self, response: str) -> float:
        """Extract overall score."""

        lines = response.split('\n')
        for line in lines:
            if "## Overall Score" in line:
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    score_line = lines[idx + 1].strip()
                    try:
                        score = float(''.join(filter(lambda x: x.isdigit() or x == '.', score_line)))
                        return max(0.0, min(10.0, score))
                    except:
                        pass

        return 7.0  # Default

    def _extract_overall_feedback(self, response: str) -> str:
        """Extract overall feedback."""

        lines = response.split('\n')
        feedback = []
        in_section = False

        for line in lines:
            if "## Overall Assessment" in line:
                in_section = True
                continue
            elif in_section and line.strip().startswith('##'):
                break
            elif in_section and line.strip():
                feedback.append(line.strip())

        return ' '.join(feedback) if feedback else "Artifacts reviewed."

    def _extract_criterion_scores(self, response: str) -> dict:
        """Extract criterion scores."""

        scores = {}
        lines = response.split('\n')
        in_section = False

        for line in lines:
            if "## Criterion Scores" in line:
                in_section = True
                continue
            elif in_section and line.strip().startswith('##'):
                break
            elif in_section and ':' in line:
                parts = line.split(':', 1)
                criterion = parts[0].strip('- ').strip()
                try:
                    score = float(''.join(filter(lambda x: x.isdigit() or x == '.', parts[1])))
                    scores[criterion] = max(0.0, min(10.0, score))
                except:
                    pass

        return scores

    def _extract_criterion_feedback(self, response: str) -> dict:
        """Extract criterion feedback."""

        feedback = {}
        lines = response.split('\n')
        in_section = False
        current_criterion = None
        current_feedback = []

        for line in lines:
            if "## Criterion Feedback" in line:
                in_section = True
                continue
            elif in_section and line.strip().startswith('##') and "Criterion" not in line:
                break
            elif in_section:
                if line.strip().startswith('###'):
                    if current_criterion:
                        feedback[current_criterion] = ' '.join(current_feedback)
                    current_criterion = line.strip('#').strip()
                    current_feedback = []
                elif current_criterion and line.strip():
                    current_feedback.append(line.strip())

        if current_criterion:
            feedback[current_criterion] = ' '.join(current_feedback)

        return feedback

    def _extract_strengths(self, response: str) -> List[str]:
        """Extract strengths."""

        return self._extract_list_section(response, "## Strengths")

    def _extract_improvements(self, response: str) -> List[str]:
        """Extract areas for improvement."""

        return self._extract_list_section(response, "## Areas for Improvement")

    def _extract_recruiter_appeal(self, response: str) -> str:
        """Extract recruiter appeal assessment."""

        lines = response.split('\n')
        appeal = []
        in_section = False

        for line in lines:
            if "## Recruiter Appeal" in line:
                in_section = True
                continue
            elif in_section and line.strip().startswith('##'):
                break
            elif in_section and line.strip():
                appeal.append(line.strip())

        return ' '.join(appeal) if appeal else "Work demonstrates relevant skills."

    def _extract_skills_demonstrated(self, response: str) -> List[str]:
        """Extract skills demonstrated."""

        return self._extract_list_section(response, "## Skills Demonstrated")

    def _extract_project_title(self, response: str) -> str:
        """Extract project title."""

        lines = response.split('\n')
        for i, line in enumerate(lines):
            if "## Project Title" in line and i + 1 < len(lines):
                return lines[i + 1].strip()

        return "Project Completed"

    def _extract_project_one_liner(self, response: str) -> str:
        """Extract project one-liner."""

        lines = response.split('\n')
        for i, line in enumerate(lines):
            if "## Project One-Liner" in line and i + 1 < len(lines):
                return lines[i + 1].strip()

        return "Completed a project"

    def _extract_project_description(self, response: str) -> str:
        """Extract project description."""

        lines = response.split('\n')
        desc = []
        in_section = False

        for line in lines:
            if "## Project Description" in line:
                in_section = True
                continue
            elif in_section and line.strip().startswith('##'):
                break
            elif in_section and line.strip():
                desc.append(line.strip())

        return ' '.join(desc) if desc else "Completed a project demonstrating relevant skills."

    def _extract_suggested_skills(self, response: str) -> List[str]:
        """Extract suggested skills."""

        return self._extract_list_section(response, "## Skills Section")

    def _extract_talking_points(self, response: str) -> List[str]:
        """Extract interview talking points."""

        return self._extract_list_section(response, "## Interview Talking Points")

    def _extract_next_steps(self, response: str) -> str:
        """Extract next steps."""

        lines = response.split('\n')
        steps = []
        in_section = False

        for line in lines:
            if "## Next Steps" in line:
                in_section = True
                continue
            elif in_section and line.strip().startswith('##'):
                break
            elif in_section and line.strip():
                steps.append(line.strip())

        return ' '.join(steps) if steps else "Use this feedback to improve your work."

    def _extract_list_section(self, response: str, header: str) -> List[str]:
        """Extract a list section."""

        lines = response.split('\n')
        items = []
        in_section = False

        for line in lines:
            if header in line:
                in_section = True
                continue
            elif in_section and line.strip().startswith('##'):
                break
            elif in_section:
                line_stripped = line.strip()
                if line_stripped.startswith('- ') or line_stripped.startswith('* '):
                    items.append(line_stripped[2:])
                elif line_stripped and line_stripped[0].isdigit() and '.' in line_stripped:
                    items.append(line_stripped.split('.', 1)[1].strip())

        return items
