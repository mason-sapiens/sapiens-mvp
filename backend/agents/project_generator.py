"""
Project Generator Agent.

Generates role-aligned, recruiter-relevant projects completable in 2-3 weeks.
"""

import uuid
from typing import List
from .base import BaseAgent
from ..schemas.agent_io import ProjectGeneratorInput, ProjectGeneratorOutput
from ..schemas.project import ProjectProposal, ProjectType, DeliverableType


class ProjectGeneratorAgent(BaseAgent):
    """
    Generates project proposals tailored to target role and domain.

    Responsibilities:
    - Analyze target role and domain
    - Design 2-3 week projects
    - Define deliverables and evaluation criteria
    - Ensure recruiter appeal
    """

    def __init__(self, **kwargs):
        super().__init__(agent_name="ProjectGenerator", **kwargs)

    def process(self, input_data: ProjectGeneratorInput) -> ProjectGeneratorOutput:
        """
        Generate a project proposal.

        Args:
            input_data: ProjectGeneratorInput with role, domain, background

        Returns:
            ProjectGeneratorOutput with proposal
        """

        try:
            # Get domain context if available
            domain_context = ""
            if self.rag_module:
                domain_query = f"project ideas and best practices for {input_data.target_role} in {input_data.target_domain}"
                domain_context = self.get_domain_context(
                    input_data.target_domain,
                    domain_query
                )

            # Build system prompt
            system_prompt = self._build_system_prompt()

            # Build user prompt
            user_prompt = self._build_user_prompt(input_data, domain_context)

            # Call Claude
            response = self.call_claude(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.8  # Higher for creativity
            )

            # Parse response into structured proposal
            proposal = self._parse_response(response, input_data)

            return ProjectGeneratorOutput(
                request_id=input_data.request_id,
                success=True,
                proposal=proposal,
                reasoning=self._extract_reasoning(response),
                alternative_options=self._extract_alternatives(response)
            )

        except Exception as e:
            return ProjectGeneratorOutput(
                request_id=input_data.request_id,
                success=False,
                message=f"Failed to generate project: {str(e)}"
            )

    def _build_system_prompt(self) -> str:
        """Build system prompt for project generation."""

        return """You are an expert career coach and project designer specializing in helping job seekers build impressive portfolio projects.

Your task is to design a project that:
1. Can be completed by ONE person in 2-3 weeks
2. Clearly demonstrates skills relevant to the target role
3. Appeals to recruiters and hiring managers
4. Produces TANGIBLE, REAL-WORLD deliverables (not just mockups or plans)
5. Is grounded in actual execution with measurable outcomes

Project types and MANDATORY deliverable requirements:

- RESEARCH:
  • Must result in a completed research paper
  • Paper must be uploaded to arXiv or similar repository
  • Include hypothesis, methodology, data collection, analysis, and conclusions
  • Deliverable: Published arXiv paper link

- PRODUCT:
  • Must be fully built and launched (not just designed)
  • Real users must be acquired (minimum viable user base)
  • Product must be live and accessible
  • Deliverable: Live product URL + user metrics

- CAMPAIGN:
  • Campaign must be personally designed AND executed
  • Data must be collected and analyzed from real execution
  • Include pre/post metrics and performance analysis
  • Deliverable: Campaign results report with actual performance data

- STARTUP:
  • Must involve launching a small-scale venture
  • Real monetization must be attempted (even if minimal revenue)
  • Include validation, launch, and early traction metrics
  • Deliverable: Live business + revenue/traction data

- MARKETING (Reports/Analysis):
  • Report must be completed to professional standards
  • Must be sent to relevant stakeholders (real or simulated)
  • Include actionable insights and recommendations
  • Deliverable: Published report + stakeholder engagement proof

CRITICAL REQUIREMENTS:
- All projects must result in REAL execution, not just documentation
- Deliverables must be tangible and verifiable (live links, published content, real data)
- Projects should create actual value in the real world
- Avoid purely hypothetical or planning-only projects
- Focus on building/creating/launching something real that others can see and interact with

Guidelines:
- Projects must be realistic and achievable in 2-3 weeks
- Must be completable independently without large teams or specialized resources
- Focus on demonstrating execution capability, not just strategic thinking
- Ensure projects can be showcased with concrete proof of completion
- Balance ambition with feasibility

MANDATORY: Include a simple roadmap with clear milestones.
The roadmap must:
- Outline 4-6 key milestones spanning the project timeline
- Specify expected completion level at each milestone (e.g., "Foundation ready", "MVP complete", "Live with initial users")
- Include concrete checkpoints that demonstrate progress
- Make it clear what "done" looks like at each stage
- Do NOT specify exact days or dates, just the sequence of milestones

Output your response in this exact format:

# PROJECT PROPOSAL

## Title
[Concise, professional project title]

## Type
[RESEARCH/PRODUCT/CAMPAIGN/STARTUP/MARKETING]

## Description
[2-3 paragraphs describing the project and its context]
[MUST emphasize real-world execution and tangible outcomes]

## Why Relevant
[Explain why this project is perfect for this role and domain]

## Deliverables
1. [Deliverable name]: [Description] - Format: [Specific format]
   Real-world outcome: [What will actually be launched/published/executed]
   Evaluation criteria: [criterion 1], [criterion 2], [criterion 3]
2. [Continue for each deliverable]
[MUST include at least one deliverable that is live/public/real]

## Project Roadmap
Milestone 1: [Milestone name]
- Tasks: [What needs to be done]
- Expected outcome: [Specific state or completion level]

Milestone 2: [Milestone name]
- Tasks: [What needs to be done]
- Expected outcome: [Specific state or completion level]

Milestone 3: [Milestone name]
- Tasks: [What needs to be done]
- Expected outcome: [Specific state or completion level]

Milestone 4: [Milestone name]
- Tasks: [What needs to be done]
- Expected outcome: [Specific state or completion level]

[Continue for 4-6 milestones total]

Final Milestone: [Launch/Publication/Completion]
- Tasks: [Final steps]
- Expected outcome: [Live/Published/Launched with tangible proof]

## Skills Demonstrated
- [Skill 1]
- [Skill 2]
- [Continue]

## Recruiter Appeal
[Why recruiters will be impressed by this project]
[Emphasize the real-world execution aspect]

## Evaluation Criteria
1. [Criterion 1]
2. [Criterion 2]
3. [Continue]

## Estimated Duration
[2.0-3.0 weeks]

## Alternative Options Considered
1. [Alternative 1]: [Brief description]
2. [Alternative 2]: [Brief description]
3. [Alternative 3]: [Brief description]

## Reasoning
[Why this project was selected over alternatives]
[Explain how it balances ambition with 2-3 week feasibility]"""

    def _build_user_prompt(
        self,
        input_data: ProjectGeneratorInput,
        domain_context: str
    ) -> str:
        """Build user prompt with specific requirements."""

        prompt = f"""Generate a project proposal for a job seeker with the following profile:

Target Role: {input_data.target_role}
Target Domain: {input_data.target_domain}
"""

        if input_data.background:
            prompt += f"Background: {input_data.background}\n"

        if input_data.interests:
            prompt += f"Interests: {input_data.interests}\n"

        if input_data.previous_proposals:
            prompt += f"\nAvoid projects similar to these previously rejected proposals: {', '.join(input_data.previous_proposals)}\n"

        if domain_context:
            prompt += f"\n{domain_context}\n"

        prompt += """
Requirements:
- Must be completable in 2-3 weeks by one person
- Must produce tangible deliverables
- Must demonstrate skills valuable for the target role
- Must appeal to recruiters in this domain

Generate a comprehensive project proposal following the specified format."""

        return prompt

    def _parse_response(
        self,
        response: str,
        input_data: ProjectGeneratorInput
    ) -> ProjectProposal:
        """Parse Claude's response into a ProjectProposal."""

        # Simple parsing logic - in production, use more robust parsing
        lines = response.split('\n')

        # Extract sections
        title = self._extract_section(lines, "## Title")
        project_type_str = self._extract_section(lines, "## Type").strip().upper()
        description = self._extract_section(lines, "## Description")
        why_relevant = self._extract_section(lines, "## Why Relevant")
        deliverables_text = self._extract_section(lines, "## Deliverables")
        skills_text = self._extract_section(lines, "## Skills Demonstrated")
        recruiter_appeal = self._extract_section(lines, "## Recruiter Appeal")
        criteria_text = self._extract_section(lines, "## Evaluation Criteria")
        duration_text = self._extract_section(lines, "## Estimated Duration")

        # Parse project type
        project_type = ProjectType.PRODUCT  # Default
        if "RESEARCH" in project_type_str:
            project_type = ProjectType.RESEARCH
        elif "CAMPAIGN" in project_type_str:
            project_type = ProjectType.CAMPAIGN
        elif "STARTUP" in project_type_str:
            project_type = ProjectType.STARTUP

        # Parse deliverables
        deliverables = self._parse_deliverables(deliverables_text)

        # Parse skills
        skills = self._parse_list(skills_text)

        # Parse evaluation criteria
        evaluation_criteria = self._parse_list(criteria_text)

        # Parse duration
        duration = 2.5  # Default
        try:
            duration_num = float(''.join(filter(lambda x: x.isdigit() or x == '.', duration_text)))
            duration = max(2.0, min(3.0, duration_num))
        except:
            pass

        return ProjectProposal(
            title=title.strip(),
            project_type=project_type,
            description=description.strip(),
            why_relevant=why_relevant.strip(),
            deliverables=deliverables,
            estimated_duration_weeks=duration,
            skills_demonstrated=skills,
            recruiter_appeal=recruiter_appeal.strip(),
            evaluation_criteria=evaluation_criteria
        )

    def _extract_section(self, lines: List[str], header: str) -> str:
        """Extract content of a section from markdown."""

        content = []
        in_section = False

        for line in lines:
            if line.strip().startswith(header):
                in_section = True
                continue
            elif in_section and line.strip().startswith("##"):
                break
            elif in_section:
                content.append(line)

        return '\n'.join(content).strip()

    def _parse_deliverables(self, text: str) -> List[DeliverableType]:
        """Parse deliverables from text."""

        deliverables = []
        lines = text.split('\n')

        current_deliverable = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line[0].isdigit() and '.' in line:
                # New deliverable
                if current_deliverable:
                    deliverables.append(current_deliverable)

                parts = line.split(':', 1)
                if len(parts) == 2:
                    name = parts[0].split('.', 1)[1].strip()
                    description = parts[1].strip()

                    # Extract format
                    format_str = "Document"
                    if "Format:" in description:
                        format_part = description.split("Format:", 1)[1].split("Evaluation", 1)[0].strip()
                        format_str = format_part

                    current_deliverable = DeliverableType(
                        name=name,
                        description=description,
                        format=format_str,
                        evaluation_criteria=[]
                    )

            elif current_deliverable and "Evaluation criteria:" in line:
                # Extract criteria
                criteria_text = line.split("Evaluation criteria:", 1)[1].strip()
                criteria = [c.strip() for c in criteria_text.split(',')]
                current_deliverable.evaluation_criteria = criteria

        if current_deliverable:
            deliverables.append(current_deliverable)

        # Ensure at least one deliverable
        if not deliverables:
            deliverables.append(DeliverableType(
                name="Final Report",
                description="Comprehensive project documentation",
                format="PDF document",
                evaluation_criteria=["Clarity", "Depth", "Professionalism"]
            ))

        return deliverables

    def _parse_list(self, text: str) -> List[str]:
        """Parse a bulleted or numbered list."""

        items = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Remove bullet/number prefix
            if line.startswith('- ') or line.startswith('* '):
                items.append(line[2:].strip())
            elif line[0].isdigit() and '.' in line:
                items.append(line.split('.', 1)[1].strip())
            elif line:
                items.append(line)

        return items

    def _extract_reasoning(self, response: str) -> str:
        """Extract reasoning from response."""

        lines = response.split('\n')
        return self._extract_section(lines, "## Reasoning")

    def _extract_alternatives(self, response: str) -> List[str]:
        """Extract alternative options from response."""

        lines = response.split('\n')
        alternatives_text = self._extract_section(lines, "## Alternative Options Considered")
        return self._parse_list(alternatives_text)
