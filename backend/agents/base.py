"""
Base agent class.
All agents are stateless and communicate only through the Orchestrator.
"""

from abc import ABC, abstractmethod
from typing import Optional
from openai import OpenAI
import os
from ..modules.rag import RAGModule
from ..modules.logging import LoggingModule


class BaseAgent(ABC):
    """
    Base class for all agents.

    Principles:
    - Stateless: All state is managed by Orchestrator
    - Explicit I/O: Clear input/output schemas
    - No direct agent-to-agent calls
    - Single responsibility per agent
    """

    def __init__(
        self,
        agent_name: str,
        rag_module: Optional[RAGModule] = None,
        logging_module: Optional[LoggingModule] = None,
        openai_api_key: Optional[str] = None,
        model: str = "gpt-4o"
    ):
        """
        Initialize base agent.

        Args:
            agent_name: Name of this agent
            rag_module: RAG module for knowledge retrieval
            logging_module: Logging module for persistence
            openai_api_key: OpenAI API key
            model: OpenAI model to use (gpt-4o, gpt-4-turbo, etc.)
        """

        self.agent_name = agent_name
        self.rag_module = rag_module
        self.logging_module = logging_module

        # Initialize OpenAI client
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    @abstractmethod
    def process(self, input_data):
        """
        Process input and return output.

        Must be implemented by each agent.
        Should be deterministic and stateless.
        """

        pass

    def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """
        Call OpenAI API with system and user prompts.

        Args:
            system_prompt: System instructions
            user_prompt: User message
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Model's response text
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {str(e)}")

    # Alias for backward compatibility
    def call_claude(self, system_prompt: str, user_prompt: str,
                    max_tokens: int = 4096, temperature: float = 0.7) -> str:
        """Alias for call_llm for backward compatibility."""
        return self.call_llm(system_prompt, user_prompt, max_tokens, temperature)

    def get_domain_context(self, domain: str, query: str) -> str:
        """
        Get domain context from RAG module.

        Args:
            domain: Domain name
            query: Specific query

        Returns:
            Context string with citations
        """

        if not self.rag_module:
            return ""

        result = self.rag_module.retrieve(query, domain_filter=domain)

        # Format with citations
        context = f"Relevant domain knowledge:\n\n{result.context_summary}\n\n"
        context += f"Sources: {', '.join(result.sources)}"

        return context
