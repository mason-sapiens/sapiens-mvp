"""
Main Chat Agent.

The only agent that directly talks to the user.
Never makes decisions - only relays Orchestrator instructions in natural language.
"""

from typing import Dict, Any, Optional
from .base import BaseAgent


class MainChatAgent(BaseAgent):
    """
    User-facing conversational agent.

    Responsibilities:
    - Translate Orchestrator instructions into natural conversation
    - Parse user responses
    - Maintain friendly, encouraging tone
    - NEVER make state decisions

    This agent does NOT decide what happens next.
    It only formats messages for the user.
    """

    def __init__(self, **kwargs):
        super().__init__(agent_name="MainChat", **kwargs)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and generate appropriate output.

        Args:
            input_data: Dictionary containing message_type, context, etc.

        Returns:
            Dictionary with generated message
        """
        message_type = input_data.get("message_type", "")
        context = input_data.get("context", {})
        custom_message = input_data.get("custom_message")

        message = self.generate_message(message_type, context, custom_message)

        return {
            "message": message,
            "message_type": message_type
        }

    def generate_message(
        self,
        message_type: str,
        context: Dict[str, Any],
        custom_message: Optional[str] = None
    ) -> str:
        """
        Generate a user-facing message.

        Args:
            message_type: Type of message to generate
            context: Context data for the message
            custom_message: Optional custom message override

        Returns:
            Natural language message for the user
        """

        if custom_message:
            return self._add_personality(custom_message)

        if message_type == "welcome":
            return self._generate_welcome()
        elif message_type == "onboarding_question":
            return self._generate_onboarding_question(context)
        elif message_type == "project_proposal":
            return self._generate_project_proposal(context)
        elif message_type == "problem_prompt":
            return self._generate_problem_prompt(context)
        elif message_type == "problem_feedback":
            return self._generate_problem_feedback(context)
        elif message_type == "solution_prompt":
            return self._generate_solution_prompt(context)
        elif message_type == "solution_feedback":
            return self._generate_solution_feedback(context)
        elif message_type == "execution_plan":
            return self._generate_execution_plan(context)
        elif message_type == "milestone_update":
            return self._generate_milestone_update(context)
        elif message_type == "review_request":
            return self._generate_review_request(context)
        elif message_type == "review_feedback":
            return self._generate_review_feedback(context)
        elif message_type == "resume_delivery":
            return self._generate_resume_delivery(context)
        elif message_type == "completion":
            return self._generate_completion(context)
        else:
            return "I'm here to help you with your project. What would you like to do?"

    def parse_user_input(
        self,
        user_message: str,
        expected_type: str
    ) -> Dict[str, Any]:
        """
        Parse user input based on expected type.

        Args:
            user_message: User's message
            expected_type: What type of input we expect

        Returns:
            Parsed data dictionary
        """

        # Simple parsing - in production, use more sophisticated NLP
        parsed = {
            "raw_message": user_message,
            "type": expected_type
        }

        if expected_type == "approval":
            # Check for approval/rejection
            message_lower = user_message.lower()
            if any(word in message_lower for word in ["yes", "approve", "looks good", "proceed", "confirm"]):
                parsed["approved"] = True
            elif any(word in message_lower for word in ["no", "reject", "change", "different", "not"]):
                parsed["approved"] = False
            else:
                parsed["approved"] = None  # Unclear

        return parsed

    def _add_personality(self, message: str) -> str:
        """Add friendly, professional tone to message."""

        # In production, could use Claude to enhance tone
        return message

    def _generate_welcome(self) -> str:
        """Generate welcome message."""

        return """Welcome to Sapiens! I'm here to guide you through building a portfolio project that will impress recruiters.

Over the next 2-3 weeks, we'll work together to:
1. Design a project tailored to your target role
2. Define a meaningful problem to solve
3. Create a solution strategy
4. Execute and build real deliverables
5. Generate resume-ready content

Let's get started! To create the perfect project for you, I need to understand your goals.

**What role are you targeting?** (e.g., Product Manager, Data Analyst, Marketing Associate)"""

    def _generate_onboarding_question(self, context: Dict[str, Any]) -> str:
        """Generate onboarding question."""

        question = context.get("question", "")
        return f"\n{question}"

    def _generate_project_proposal(self, context: Dict[str, Any]) -> str:
        """Generate project proposal presentation."""

        proposal = context.get("proposal")
        if not proposal:
            return "I'm working on generating a project proposal for you..."

        message = f"""Great! I've designed a project specifically for you:

# {proposal.title}

**Project Type:** {proposal.project_type}

**Why This Project:**
{proposal.why_relevant}

**What You'll Build:**
{proposal.description}

**Deliverables:**
"""

        for i, deliverable in enumerate(proposal.deliverables, 1):
            message += f"\n{i}. **{deliverable.name}**: {deliverable.description}"

        message += f"""

**Skills You'll Demonstrate:**
{chr(10).join(f"- {skill}" for skill in proposal.skills_demonstrated)}

**Estimated Time:** {proposal.estimated_duration_weeks} weeks

**Why Recruiters Will Love This:**
{proposal.recruiter_appeal}

---

What do you think? Does this project excite you? (Yes/No or request changes)"""

        return message

    def _generate_problem_prompt(self, context: Dict[str, Any]) -> str:
        """Generate problem definition prompt."""

        return """Now let's define the specific problem you'll address in this project.

A strong problem definition should:
- Identify a specific pain point or opportunity
- Clarify who experiences this problem
- Explain why it matters
- Be addressable in 2-3 weeks

Please provide:

1. **Problem Statement** (1-2 sentences): What specific problem are you solving?

2. **Target Audience**: Who experiences this problem?

3. **Context**: Why does this problem matter? What's the current situation?

4. **Success Metrics**: How will you measure if you've addressed the problem well?

Take your time to think through this carefully."""

    def _generate_problem_feedback(self, context: Dict[str, Any]) -> str:
        """Generate problem evaluation feedback."""

        feedback = context.get("feedback")
        passed = context.get("passed", False)

        if passed:
            message = f"""Excellent! Your problem definition is strong. Here's my evaluation:

{feedback.get('overall_feedback', '')}

**Strengths:**
{chr(10).join(f"- {s}" for s in feedback.get('strengths', []))}

**Scores:**
"""
            for criterion, score in feedback.get('scores', {}).items():
                message += f"- {criterion.replace('_', ' ').title()}: {score}/10\n"

            message += "\nYou're ready to move to solution design!"

        else:
            message = f"""Good start! Your problem definition needs some refinement. Here's my feedback:

{feedback.get('overall_feedback', '')}

**What's Working:**
{chr(10).join(f"- {s}" for s in feedback.get('strengths', [])) if feedback.get('strengths') else 'Getting your ideas down'}

**Suggestions for Improvement:**
{chr(10).join(f"- {s}" for s in feedback.get('suggestions', []))}

**Scores:**
"""
            for criterion, score in feedback.get('scores', {}).items():
                message += f"- {criterion.replace('_', ' ').title()}: {score}/10\n"

            if feedback.get('example_improvements'):
                message += f"\n**Examples:**\n{feedback['example_improvements']}"

            message += "\n\nPlease revise your problem definition based on this feedback."

        return message

    def _generate_solution_prompt(self, context: Dict[str, Any]) -> str:
        """Generate solution design prompt."""

        return """Great! Now let's design your solution approach.

A strong solution design should:
- Logically address the problem you defined
- Be innovative or differentiated
- Be feasible to implement in 2-3 weeks
- Have clear, measurable outcomes

Please provide:

1. **Solution Approach** (2-3 sentences): What's your high-level approach?

2. **Key Components**: What are the main elements or parts of your solution?

3. **Methodology**: What methods, frameworks, or processes will you use?

4. **Expected Outcomes**: What will this solution achieve?

5. **Resource Requirements** (optional): What tools, data, or resources do you need?

Think strategically about how to create maximum impact."""

    def _generate_solution_feedback(self, context: Dict[str, Any]) -> str:
        """Generate solution evaluation feedback."""

        feedback = context.get("feedback")
        passed = context.get("passed", False)

        if passed:
            message = f"""Outstanding! Your solution design is solid. Here's my evaluation:

{feedback.get('overall_feedback', '')}

**Strengths:**
{chr(10).join(f"- {s}" for s in feedback.get('strengths', []))}

**Scores:**
"""
            for criterion, score in feedback.get('scores', {}).items():
                message += f"- {criterion.replace('_', ' ').title()}: {score}/10\n"

            message += "\nYou're ready to start execution! Let's create your milestone plan."

        else:
            message = f"""Good thinking! Your solution design needs some refinement. Here's my feedback:

{feedback.get('overall_feedback', '')}

**What's Working:**
{chr(10).join(f"- {s}" for s in feedback.get('strengths', [])) if feedback.get('strengths') else 'Good initial thinking'}

**Suggestions for Improvement:**
{chr(10).join(f"- {s}" for s in feedback.get('suggestions', []))}

**Scores:**
"""
            for criterion, score in feedback.get('scores', {}).items():
                message += f"- {criterion.replace('_', ' ').title()}: {score}/10\n"

            if feedback.get('example_improvements'):
                message += f"\n**Examples:**\n{feedback['example_improvements']}"

            message += "\n\nPlease revise your solution design based on this feedback."

        return message

    def _generate_execution_plan(self, context: Dict[str, Any]) -> str:
        """Generate execution plan presentation."""

        milestones = context.get("milestones", [])
        feedback = context.get("feedback", "")

        message = f"""Excellent! Here's your execution plan:

{feedback}

**Your Milestones:**
"""

        for milestone in milestones:
            message += f"""
### {milestone.order}. {milestone.title}
- **Goal**: {milestone.description}
- **Deliverable**: {milestone.deliverable}
- **Estimated Time**: {milestone.estimated_days} days
- **Next Action**: {milestone.next_action}
"""

        message += f"""

**Total Estimated Time:** {sum(m.estimated_days for m in milestones)} days

---

Ready to start? Your first milestone is: **{milestones[0].title}**

**Your next action:** {milestones[0].next_action}

When you make progress, share an update and I'll guide you to the next step!"""

        return message

    def _generate_milestone_update(self, context: Dict[str, Any]) -> str:
        """Generate milestone progress update."""

        feedback = context.get("feedback", "")
        next_action = context.get("next_action", "")
        stagnation = context.get("stagnation", False)

        message = feedback

        if stagnation:
            message += "\n\n⚠️ I notice you might be stuck. Let's get you unstuck!"

        message += f"\n\n**Your next action:** {next_action}"

        if context.get("tips"):
            message += f"\n\n**Tips:**\n"
            for tip in context["tips"]:
                message += f"- {tip}\n"

        return message

    def _generate_review_request(self, context: Dict[str, Any]) -> str:
        """Generate review request."""

        return """Congratulations on completing your project work! Now it's time for the final review.

Please submit your final artifacts:

1. **Artifact Type** (e.g., Report, Presentation, Prototype)
2. **Description** of what you've created
3. **Link or file** (if available)

Submit each deliverable, and I'll provide an objective evaluation based on the project criteria."""

    def _generate_review_feedback(self, context: Dict[str, Any]) -> str:
        """Generate review feedback."""

        review = context.get("review")

        message = f"""# Project Review Complete

{review.overall_feedback}

**Overall Score:** {review.overall_score}/10

**Criterion Scores:**
"""

        for criterion, score in review.criterion_scores.items():
            message += f"- {criterion}: {score}/10\n"

        message += f"""

**Strengths:**
{chr(10).join(f"- {s}" for s in review.strengths)}

**Areas for Improvement:**
{chr(10).join(f"- {s}" for s in review.areas_for_improvement)}

**Recruiter Perspective:**
{review.recruiter_appeal_assessment}

**Skills You Demonstrated:**
{chr(10).join(f"- {s}" for s in review.skills_demonstrated)}

---

Ready to generate your resume content? (Yes/No)"""

        return message

    def _generate_resume_delivery(self, context: Dict[str, Any]) -> str:
        """Generate resume content delivery."""

        resume = context.get("resume")

        message = f"""# Your Resume Content

Here's your resume-ready content, grounded in the actual work you completed:

## Project Title for Resume
**{resume['project_title']}**

{resume['project_one_liner']}

## Resume Bullets
"""

        for i, bullet in enumerate(resume.get('bullets', []), 1):
            message += f"\n{i}. {bullet.bullet_text}"
            message += f"\n   *Skills: {', '.join(bullet.skills_highlighted)}*\n"

        message += f"""

## Cover Letter Description
{resume.get('project_description', '')}

## Skills to Add to Resume
{chr(10).join(f"- {s}" for s in resume.get('suggested_skills', []))}

## Interview Talking Points
{chr(10).join(f"- {p}" for p in resume.get('talking_points', []))}

---

**Next Steps:**
1. Copy these bullets into your resume
2. Tailor them for specific job applications
3. Practice discussing your project using the talking points
4. Keep your project artifacts accessible for portfolio

Congratulations on completing your project!"""

        return message

    def _generate_completion(self, context: Dict[str, Any]) -> str:
        """Generate completion message."""

        return """Congratulations! You've successfully completed your project journey with Sapiens.

You now have:
- A completed, recruiter-relevant project
- Professional resume bullets grounded in real work
- Interview talking points
- Tangible deliverables to showcase

**What's Next:**
1. Update your resume with the bullets provided
2. Add this project to your LinkedIn
3. Prepare your portfolio artifacts for interviews
4. Start applying to roles with confidence!

Thank you for using Sapiens. Best of luck with your job search!"""

        return message
