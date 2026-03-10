"""
Claude API Integration for Executive Copilot

Manages interactions with Anthropic Claude API:
- Initialize Anthropic client with API key
- Create prompts with guardrails for ESG domain
- Track message history for context
- Generate responses with citations
- Implement safety checks to prevent fabrication
"""

import os
import logging
from typing import Optional, List, Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Client for interacting with Anthropic Claude API
    Implements guardrails and citation tracking
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        try:
            import anthropic

            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in environment")

            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = "claude-3-5-sonnet-20241022"  # Latest Claude model
            logger.info("Claude client initialized successfully")

        except ImportError:
            logger.error("anthropic package not installed. Install with: pip install anthropic")
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing Claude client: {str(e)}")
            self.client = None

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text (using OpenAI for now, can switch to Claude)

        Args:
            text: Text to embed

        Returns:
            List of floats representing embedding, or None on error
        """
        try:
            import openai

            openai.api_key = os.getenv("OPENAI_API_KEY")
            if not openai.api_key:
                logger.warning("OPENAI_API_KEY not set, embedding generation skipped")
                return None

            response = openai.Embedding.create(
                input=text, model="text-embedding-3-small"
            )
            return response["data"][0]["embedding"]

        except ImportError:
            logger.error("openai package not installed for embeddings")
            return None
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None

    def get_system_prompt(self) -> str:
        """
        Get system prompt with guardrails for ESG domain

        Returns:
            System prompt string
        """
        return """You are an expert ESG (Environmental, Social, Governance) analyst for data center operations.
Your role is to help executives understand sustainability metrics, carbon emissions, energy efficiency, and environmental performance.

CRITICAL GUARDRAILS:
1. **Data Integrity**: ONLY reference data that has been provided in the context. NEVER fabricate or assume data.
2. **Uncertainty**: If data is incomplete or uncertain, explicitly state: "I don't have reliable data for..." or "The data for X is incomplete because..."
3. **Citations**: ALWAYS cite the source of every fact. Include metric name, period, and value.
4. **Calculations**: Show your calculation steps clearly so they can be verified.
5. **Confidence**: Indicate your confidence level in the answer (high/medium/low).
6. **Scope Clarification**: Always clarify which scope (1, 2, or 3) you're discussing for emissions.

RESPONSE FORMAT:
- Start with a direct answer to the question
- Provide supporting data with citations
- Show calculations if applicable
- State any limitations or data gaps
- Indicate overall confidence level

PROHIBITED BEHAVIORS:
- Do NOT invent data points
- Do NOT claim certainty when uncertain
- Do NOT extrapolate beyond provided data without explicit caveats
- Do NOT make recommendations without proper ESG methodology backing
- Do NOT reference data that wasn't in the context provided

TONE:
- Professional and precise
- Executive-friendly (avoid jargon where possible, explain when necessary)
- Data-driven and evidence-based
- Transparent about limitations"""

    def create_user_message(
        self,
        question: str,
        context: Dict,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Tuple[List[Dict], str]:
        """
        Create user message with context for Claude

        Args:
            question: User's question
            context: Retrieved context from vector store
            conversation_history: Previous messages in conversation

        Returns:
            Tuple of (messages_list, formatted_context_string)
        """
        try:
            messages = []

            # Add previous conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Format context into readable text
            context_text = self._format_context(context)

            # Create user message with context
            user_content = f"""CONTEXT (Data available for analysis):
{context_text}

QUESTION FROM USER:
{question}

Please provide a comprehensive answer based ONLY on the provided context.
If the context doesn't contain necessary information, state what's missing."""

            messages.append({"role": "user", "content": user_content})

            return messages, context_text

        except Exception as e:
            logger.error(f"Error creating user message: {str(e)}")
            return [], ""

    def _format_context(self, context: Dict) -> str:
        """
        Format retrieved context into readable text

        Args:
            context: Context dictionary from vector store

        Returns:
            Formatted context string
        """
        try:
            parts = []

            # Metrics section
            if context.get("metrics"):
                parts.append("=== KEY PERFORMANCE INDICATORS ===")
                for metric in context["metrics"]:
                    parts.append(
                        f"• {metric.get('name', 'Unknown')} ({metric.get('unit', '')})"
                    )
                    if metric.get("latest_value"):
                        parts.append(
                            f"  Current Value: {metric['latest_value']} (Target: {metric.get('target_value', 'N/A')})"
                        )
                    if metric.get("latest_date"):
                        parts.append(f"  As of: {metric['latest_date']}")
                parts.append("")

            # Calculations section
            if context.get("calculations"):
                parts.append("=== CARBON CALCULATIONS ===")
                for calc in context["calculations"]:
                    parts.append(
                        f"• Period: {calc.get('period_start', '')} to {calc.get('period_end', '')}"
                    )
                    parts.append(
                        f"  Total Emissions: {calc.get('total_emissions', 'N/A')} kg CO2e"
                    )
                    parts.append(
                        f"  Scope 1: {calc.get('scope_1', 'N/A')} | Scope 2: {calc.get('scope_2', 'N/A')}"
                    )
                    parts.append(f"  Status: {calc.get('status', 'N/A')}")
                parts.append("")

            # Reports section
            if context.get("reports"):
                parts.append("=== AVAILABLE REPORTS ===")
                for report in context["reports"]:
                    parts.append(
                        f"• {report.get('report_type', 'Report')} ({report.get('status', 'draft')})"
                    )
                    parts.append(
                        f"  Period: {report.get('period_start', '')} to {report.get('period_end', '')}"
                    )
                parts.append("")

            # Facilities section
            if context.get("facilities"):
                parts.append("=== FACILITIES ===")
                for facility in context["facilities"]:
                    parts.append(f"• {facility.get('name', 'Unknown Facility')}")
                    if facility.get("location"):
                        parts.append(f"  Location: {facility['location']}")
                    if facility.get("facility_type"):
                        parts.append(f"  Type: {facility['facility_type']}")
                parts.append("")

            return "\n".join(parts) if parts else "No context data available"

        except Exception as e:
            logger.error(f"Error formatting context: {str(e)}")
            return "Error formatting context"

    async def generate_response(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Tuple[Optional[str], Dict]:
        """
        Generate response from Claude API

        Args:
            messages: List of message dicts with role and content
            temperature: Sampling temperature (0-1, lower = more deterministic)
            max_tokens: Maximum tokens in response

        Returns:
            Tuple of (response_text, usage_dict)
        """
        try:
            if not self.client:
                logger.error("Claude client not initialized")
                return None, {}

            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=self.get_system_prompt(),
                messages=messages,
                temperature=temperature,
            )

            # Extract response
            answer = response.content[0].text if response.content else ""

            # Extract usage information
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens
                + response.usage.output_tokens,
            }

            logger.info(
                f"Generated response - Input: {usage['input_tokens']}, Output: {usage['output_tokens']}"
            )

            return answer, usage

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return None, {}

    def extract_citations_from_answer(self, answer: str, context: Dict) -> List[Dict]:
        """
        Extract citations from generated answer based on context

        Args:
            answer: Generated answer text
            context: Context data used for generation

        Returns:
            List of citation dicts with entity info
        """
        try:
            citations = []

            # Extract referenced metrics
            if context.get("metrics"):
                for metric in context["metrics"]:
                    metric_name = metric.get("name", "")
                    # Simple check: if metric name appears in answer, it's cited
                    if metric_name.lower() in answer.lower():
                        citations.append(
                            {
                                "entity_type": "metric",
                                "entity_id": metric.get("id"),
                                "entity_name": metric_name,
                                "entity_data": metric,
                                "citation_type": "data_source",
                            }
                        )

            # Extract referenced calculations
            if context.get("calculations"):
                for calc in context["calculations"]:
                    calc_name = f"Period {calc.get('period_start', 'Unknown')}"
                    # Check if calculation data appears in answer
                    if (
                        str(calc.get("total_emissions", "")).lower()
                        in answer.lower()
                    ):
                        citations.append(
                            {
                                "entity_type": "calculation",
                                "entity_id": calc.get("id"),
                                "entity_name": calc_name,
                                "entity_data": calc,
                                "citation_type": "data_source",
                            }
                        )

            # Extract referenced reports
            if context.get("reports"):
                for report in context["reports"]:
                    report_type = report.get("report_type", "Report")
                    if report_type.lower() in answer.lower():
                        citations.append(
                            {
                                "entity_type": "report",
                                "entity_id": report.get("id"),
                                "entity_name": report_type,
                                "entity_data": report,
                                "citation_type": "reference",
                            }
                        )

            logger.info(f"Extracted {len(citations)} citations from answer")
            return citations

        except Exception as e:
            logger.error(f"Error extracting citations: {str(e)}")
            return []

    def validate_no_fabrication(
        self, answer: str, context: Dict
    ) -> Tuple[bool, List[str]]:
        """
        Validate answer for potential data fabrication

        Args:
            answer: Generated answer
            context: Context used for generation

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        try:
            issues = []

            # Check for common fabrication patterns
            fabrication_indicators = [
                ("assumed", "Answer makes unsupported assumptions"),
                ("estimated", "Answer uses estimates without data"),
                ("likely", "Answer uses speculation"),
                ("probably", "Answer uses probability language without data"),
                ("could be", "Answer uses conditional without basis"),
            ]

            answer_lower = answer.lower()

            for indicator, issue_message in fabrication_indicators:
                if indicator in answer_lower:
                    # Check if preceded by "I don't" or "based on" (which are OK)
                    index = answer_lower.find(indicator)
                    if index > 0:
                        preceding = answer_lower[max(0, index - 30) : index]
                        if not any(
                            ok_phrase in preceding
                            for ok_phrase in ["don't", "based on", "provided", "context"]
                        ):
                            issues.append(
                                f"Potential fabrication: {issue_message} at position {index}"
                            )

            # Check if answer references data not in context
            context_data_points = []
            if context.get("metrics"):
                context_data_points.extend(
                    [m.get("name", "").lower() for m in context["metrics"]]
                )
            if context.get("calculations"):
                context_data_points.append("carbon calculation")
                context_data_points.append("emissions")

            # Look for specific numbers that might not be from context
            import re

            numbers = re.findall(r"\d+[\d,]*(?:\.\d+)?", answer)
            if numbers and context_data_points:
                # If answer has numbers but context is empty, flag it
                if not context_data_points:
                    issues.append(
                        "Answer contains numerical data but context provided is empty"
                    )

            is_valid = len(issues) == 0

            return is_valid, issues

        except Exception as e:
            logger.error(f"Error validating fabrication: {str(e)}")
            return False, [f"Validation error: {str(e)}"]

    def calculate_confidence_score(
        self, answer: str, context: Dict, usage: Dict
    ) -> float:
        """
        Calculate confidence score for the answer

        Args:
            answer: Generated answer
            context: Context used
            usage: Token usage information

        Returns:
            Confidence score (0-1)
        """
        try:
            confidence = 1.0

            # Reduce confidence if limited context
            if not context.get("metrics"):
                confidence -= 0.2
            if not context.get("calculations"):
                confidence -= 0.15
            if not context.get("reports"):
                confidence -= 0.1

            # Reduce if answer contains uncertainty language
            uncertainty_phrases = [
                "i don't have",
                "insufficient data",
                "unclear",
                "uncertain",
                "limited information",
            ]
            answer_lower = answer.lower()
            for phrase in uncertainty_phrases:
                if phrase in answer_lower:
                    confidence -= 0.15

            # Increase confidence if answer is well-cited
            if context.get("metrics") and context.get("calculations"):
                confidence += 0.1

            # Normalize to 0-1 range
            return max(0.0, min(1.0, confidence))

        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return 0.5
