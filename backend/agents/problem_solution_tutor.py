"""
Problem-Solution Tutor Agent.

Evaluates both problem definitions and solution designs.
Uses different evaluation lenses for each.
"""

from typing import Dict
from .base import BaseAgent
from ..schemas.agent_io import (
    ProblemSolutionTutorInput,
    ProblemSolutionTutorOutput
)


class ProblemSolutionTutorAgent(BaseAgent):
    """
    Evaluates problem definitions and solution designs.

    Problem evaluation lens:
    - Market/research relevance
    - Clarity and specificity
    - Feasibility within 2-3 weeks

    Solution evaluation lens:
    - Logical coherence
    - Innovation and differentiation
    - Implementation feasibility
    - Impact potential
    """

    def __init__(self, **kwargs):
        super().__init__(agent_name="ProblemSolutionTutor", **kwargs)

    def process(self, input_data: ProblemSolutionTutorInput) -> ProblemSolutionTutorOutput:
        """
        Evaluate problem definition or solution design.

        Args:
            input_data: ProblemSolutionTutorInput

        Returns:
            ProblemSolutionTutorOutput with evaluation
        """

        try:
            if input_data.mode == "problem":
                return self._evaluate_problem(input_data)
            elif input_data.mode == "solution":
                return self._evaluate_solution(input_data)
            else:
                raise ValueError(f"Invalid mode: {input_data.mode}")

        except Exception as e:
            return ProblemSolutionTutorOutput(
                request_id=input_data.request_id,
                success=False,
                mode=input_data.mode,
                evaluation_passed=False,
                overall_feedback=f"Evaluation failed: {str(e)}",
                next_steps="Please try again."
            )

    def _evaluate_problem(self, input_data: ProblemSolutionTutorInput) -> ProblemSolutionTutorOutput:
        """Evaluate problem definition using market/research lens."""

        problem = input_data.problem_definition
        if not problem:
            raise ValueError("Problem definition is required for problem evaluation")

        # Build system prompt
        system_prompt = self._build_problem_evaluation_prompt()

        # Build user prompt
        user_prompt = f"""Evaluate this problem definition:

PROJECT CONTEXT:
Project ID: {problem.project_id}

PROBLEM STATEMENT:
{problem.problem_statement}

TARGET AUDIENCE:
{problem.target_audience}

CONTEXT:
{problem.problem_context}

SUCCESS METRICS:
{chr(10).join(f"- {metric}" for metric in problem.success_metrics)}

Provide a thorough evaluation following the specified format."""

        # Call Claude
        response = self.call_claude(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3  # Lower for consistent evaluation
        )

        # Parse evaluation
        scores = self._parse_scores(response, "problem")
        feedback = self._parse_feedback(response)
        strengths = self._parse_strengths(response)
        suggestions = self._parse_suggestions(response)
        next_steps = self._parse_next_steps(response)

        # Determine if passed
        avg_score = sum(scores.values()) / len(scores)
        passed = avg_score >= 7.0 and all(score >= 6.0 for score in scores.values())

        return ProblemSolutionTutorOutput(
            request_id=input_data.request_id,
            success=True,
            mode="problem",
            evaluation_passed=passed,
            scores=scores,
            overall_feedback=feedback,
            strengths=strengths,
            improvement_suggestions=suggestions,
            next_steps=next_steps,
            example_improvements=self._generate_examples(response) if not passed else None
        )

    def _evaluate_solution(self, input_data: ProblemSolutionTutorInput) -> ProblemSolutionTutorOutput:
        """Evaluate solution design using VC/practitioner lens."""

        solution = input_data.solution_design
        problem = input_data.problem_context

        if not solution:
            raise ValueError("Solution design is required for solution evaluation")

        # Build system prompt
        system_prompt = self._build_solution_evaluation_prompt()

        # Build user prompt
        user_prompt = f"""Evaluate this solution design:

PROBLEM CONTEXT:
{problem.problem_statement if problem else "N/A"}

SOLUTION APPROACH:
{solution.solution_approach}

KEY COMPONENTS:
{chr(10).join(f"- {comp}" for comp in solution.key_components)}

METHODOLOGY:
{solution.methodology}

EXPECTED OUTCOMES:
{chr(10).join(f"- {outcome}" for outcome in solution.expected_outcomes)}

RESOURCE REQUIREMENTS:
{solution.resource_requirements or "Not specified"}

Provide a thorough evaluation following the specified format."""

        # Call Claude
        response = self.call_claude(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3
        )

        # Parse evaluation
        scores = self._parse_scores(response, "solution")
        feedback = self._parse_feedback(response)
        strengths = self._parse_strengths(response)
        suggestions = self._parse_suggestions(response)
        next_steps = self._parse_next_steps(response)

        # Determine if passed
        avg_score = sum(scores.values()) / len(scores)
        passed = avg_score >= 7.0 and all(score >= 6.0 for score in scores.values())

        return ProblemSolutionTutorOutput(
            request_id=input_data.request_id,
            success=True,
            mode="solution",
            evaluation_passed=passed,
            scores=scores,
            overall_feedback=feedback,
            strengths=strengths,
            improvement_suggestions=suggestions,
            next_steps=next_steps,
            example_improvements=self._generate_examples(response) if not passed else None
        )

    def _build_problem_evaluation_prompt(self) -> str:
        """Build system prompt for problem evaluation."""

        return """You are an expert tutor evaluating problem definitions using a market/research lens.

Your goal is to help job seekers define problems that are:
1. Relevant to the market or domain
2. Clear and specific
3. Feasible to address in 2-3 weeks

Evaluation criteria (0-10 scale):
- Market Relevance: How relevant is this problem to the target market/domain?
- Clarity: How clearly and specifically is the problem defined?
- Feasibility: How feasible is it to address this problem in 2-3 weeks?

Output format:

# EVALUATION SCORES
Market Relevance: [0-10]
Clarity: [0-10]
Feasibility: [0-10]

# OVERALL FEEDBACK
[2-3 paragraphs of constructive feedback]

# STRENGTHS
- [Strength 1]
- [Strength 2]
- [Continue]

# IMPROVEMENT SUGGESTIONS
- [Specific, actionable suggestion 1]
- [Specific, actionable suggestion 2]
- [Continue]

# EXAMPLES OF IMPROVEMENTS
[Concrete examples of how to strengthen the problem definition]

# NEXT STEPS
[Clear guidance on what to do next]

Be constructive, specific, and encouraging. Focus on helping the user improve."""

    def _build_solution_evaluation_prompt(self) -> str:
        """Build system prompt for solution evaluation."""

        return """You are an expert tutor evaluating solution designs using a VC/practitioner lens.

Your goal is to help job seekers design solutions that are:
1. Logically coherent and well-structured
2. Innovative or differentiated
3. Feasible to implement in 2-3 weeks
4. High-impact and impressive

Evaluation criteria (0-10 scale):
- Logical Coherence: How logically sound is the solution approach?
- Innovation: How innovative or differentiated is this solution?
- Implementation Feasibility: How feasible is it to implement in 2-3 weeks?
- Impact Potential: How impactful could this solution be if executed well?

Output format:

# EVALUATION SCORES
Logical Coherence: [0-10]
Innovation: [0-10]
Implementation Feasibility: [0-10]
Impact Potential: [0-10]

# OVERALL FEEDBACK
[2-3 paragraphs of constructive feedback]

# STRENGTHS
- [Strength 1]
- [Strength 2]
- [Continue]

# IMPROVEMENT SUGGESTIONS
- [Specific, actionable suggestion 1]
- [Specific, actionable suggestion 2]
- [Continue]

# EXAMPLES OF IMPROVEMENTS
[Concrete examples of how to strengthen the solution]

# NEXT STEPS
[Clear guidance on what to do next]

Be constructive, specific, and encouraging. Focus on helping the user improve."""

    def _parse_scores(self, response: str, mode: str) -> Dict[str, float]:
        """Parse evaluation scores from response."""

        scores = {}
        lines = response.split('\n')

        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                key = parts[0].strip()
                value_str = parts[1].strip()

                # Extract number
                try:
                    value = float(''.join(filter(lambda x: x.isdigit() or x == '.', value_str)))
                    value = max(0.0, min(10.0, value))

                    if mode == "problem":
                        if "Market Relevance" in key:
                            scores["market_relevance"] = value
                        elif "Clarity" in key:
                            scores["clarity"] = value
                        elif "Feasibility" in key:
                            scores["feasibility"] = value
                    elif mode == "solution":
                        if "Logical Coherence" in key:
                            scores["logical_coherence"] = value
                        elif "Innovation" in key:
                            scores["innovation"] = value
                        elif "Implementation Feasibility" in key:
                            scores["implementation_feasibility"] = value
                        elif "Impact Potential" in key:
                            scores["impact_potential"] = value
                except:
                    pass

        # Ensure all scores are present with defaults
        if mode == "problem":
            scores.setdefault("market_relevance", 5.0)
            scores.setdefault("clarity", 5.0)
            scores.setdefault("feasibility", 5.0)
        else:
            scores.setdefault("logical_coherence", 5.0)
            scores.setdefault("innovation", 5.0)
            scores.setdefault("implementation_feasibility", 5.0)
            scores.setdefault("impact_potential", 5.0)

        return scores

    def _parse_feedback(self, response: str) -> str:
        """Parse overall feedback."""

        lines = response.split('\n')
        feedback = []
        in_section = False

        for line in lines:
            if "# OVERALL FEEDBACK" in line:
                in_section = True
                continue
            elif in_section and line.strip().startswith('#'):
                break
            elif in_section and line.strip():
                feedback.append(line)

        return '\n'.join(feedback).strip() or "Evaluation completed."

    def _parse_strengths(self, response: str) -> list:
        """Parse strengths."""

        return self._parse_list_section(response, "# STRENGTHS")

    def _parse_suggestions(self, response: str) -> list:
        """Parse improvement suggestions."""

        return self._parse_list_section(response, "# IMPROVEMENT SUGGESTIONS")

    def _parse_next_steps(self, response: str) -> str:
        """Parse next steps."""

        lines = response.split('\n')
        next_steps = []
        in_section = False

        for line in lines:
            if "# NEXT STEPS" in line:
                in_section = True
                continue
            elif in_section and line.strip().startswith('#'):
                break
            elif in_section and line.strip():
                next_steps.append(line)

        return '\n'.join(next_steps).strip() or "Revise based on feedback and resubmit."

    def _parse_list_section(self, response: str, header: str) -> list:
        """Parse a list section."""

        lines = response.split('\n')
        items = []
        in_section = False

        for line in lines:
            if header in line:
                in_section = True
                continue
            elif in_section and line.strip().startswith('#'):
                break
            elif in_section:
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    items.append(line[2:].strip())
                elif line and line[0].isdigit() and '.' in line:
                    items.append(line.split('.', 1)[1].strip())

        return items

    def _generate_examples(self, response: str) -> str:
        """Extract example improvements."""

        lines = response.split('\n')
        examples = []
        in_section = False

        for line in lines:
            if "# EXAMPLES OF IMPROVEMENTS" in line:
                in_section = True
                continue
            elif in_section and line.strip().startswith('#'):
                break
            elif in_section and line.strip():
                examples.append(line)

        return '\n'.join(examples).strip() or None
