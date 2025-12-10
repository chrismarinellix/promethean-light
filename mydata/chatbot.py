"""Chatbot with RAG (Retrieval-Augmented Generation) using Anthropic Claude or OpenAI GPT-4o"""

import json
import re
from typing import List, Optional, Dict, Any, Tuple
from sqlmodel import Session, select
from .models import ChatConversation, ChatMessage, ApiKey, Document
from .crypto import CryptoManager
from .embedder import Embedder
from .vectordb import VectorDB
from .hybrid_search import HybridSearcher
from .anonymizer import Anonymizer
from . import summaries


class ChatBot:
    """RAG-powered chatbot using Anthropic Claude (primary) or OpenAI GPT-4o (fallback)"""

    def __init__(
        self,
        session: Session,
        crypto: CryptoManager,
        embedder: Embedder,
        vectordb: VectorDB,
        hybrid_searcher: Optional[HybridSearcher] = None,
        anonymizer: Optional[Anonymizer] = None,
    ):
        self.session = session
        self.crypto = crypto
        self.embedder = embedder
        self.vectordb = vectordb
        self.hybrid_searcher = hybrid_searcher
        self.anonymizer = anonymizer
        self._openai_client = None
        self._anthropic_client = None
        self._llm_provider = None  # Will be set to 'anthropic' or 'openai'

    def _get_anthropic_client(self):
        """Get Anthropic client with API key from encrypted storage"""
        if self._anthropic_client is not None:
            return self._anthropic_client

        # Load API key from database
        stmt = select(ApiKey).where(ApiKey.service == "anthropic", ApiKey.enabled == True)
        api_key_record = self.session.exec(stmt).first()

        if not api_key_record:
            return None  # Anthropic not configured, will fall back to OpenAI

        # Decrypt API key
        api_key = self.crypto.decrypt_str(api_key_record.encrypted_key)

        # Initialize Anthropic client
        try:
            import anthropic
            self._anthropic_client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            return None  # anthropic package not installed

        return self._anthropic_client

    def _get_openai_client(self):
        """Get OpenAI client with API key from encrypted storage"""
        if self._openai_client is not None:
            return self._openai_client

        # Load API key from database
        stmt = select(ApiKey).where(ApiKey.service == "openai", ApiKey.enabled == True)
        api_key_record = self.session.exec(stmt).first()

        if not api_key_record:
            return None  # OpenAI not configured

        # Decrypt API key
        api_key = self.crypto.decrypt_str(api_key_record.encrypted_key)

        # Initialize OpenAI client
        try:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=api_key)
        except ImportError:
            return None  # openai package not installed

        return self._openai_client

    def get_active_llm_provider(self) -> str:
        """Return which LLM provider is active (for UI display)"""
        # Try Anthropic first
        if self._get_anthropic_client():
            return "Anthropic"
        # Fall back to OpenAI
        if self._get_openai_client():
            return "OpenAI"
        return "None"

    def _retrieve_context(self, query: str, limit: int = 5) -> Tuple[List[Dict], str]:
        """
        Retrieve relevant documents for RAG context.

        Returns:
            Tuple of (results_list, formatted_context_string)
        """
        # Embed query
        query_vector = self.embedder.embed(query)

        # Vector search (get more results for hybrid re-ranking)
        vector_results = self.vectordb.search(
            query_vector=query_vector,
            limit=limit * 3,
        )

        # Apply hybrid search if available
        if self.hybrid_searcher:
            results = self.hybrid_searcher.search(
                query=query,
                vector_results=vector_results,
                limit=limit
            )
        else:
            results = vector_results[:limit]

        # Format context for LLM
        context_parts = []
        for i, hit in enumerate(results, 1):
            text = hit.get("payload", hit).get("text", "")
            source = hit.get("payload", hit).get("source", "unknown")
            score = hit.get("hybrid_score", hit.get("score", 0))

            context_parts.append(
                f"[Document {i}] (source: {source}, relevance: {score:.3f})\n{text}\n"
            )

        context_str = "\n".join(context_parts)
        return results, context_str

    def _check_for_summary(self, query: str) -> Optional[str]:
        """
        Check if query matches a pre-computed summary topic.
        Returns formatted summary text if matched, None otherwise.
        """
        query_lower = query.lower()

        # Project Sentinel queries - check first as it's specific
        sentinel_keywords = ["sentinel", "project sentinel", "prize draw", "macbook prize", "improvement initiative"]
        if any(kw in query_lower for kw in sentinel_keywords):
            return self._format_sentinel_summary()

        # Team pay / salary queries - most specific first
        pay_keywords = ["team pay", "all pay", "salary table", "all salaries", "compensation", "pay structure", "staff salaries"]
        if any(kw in query_lower for kw in pay_keywords):
            return self._format_all_staff_table()

        # Staff queries
        staff_keywords = ["staff", "team", "employee", "people", "members", "who works", "team members"]
        if any(kw in query_lower for kw in staff_keywords):
            return self._format_staff_summary()

        # Retention bonus queries
        bonus_keywords = ["retention", "bonus", "bonuses"]
        if any(kw in query_lower for kw in bonus_keywords):
            return self._format_retention_summary()

        return None

    def _format_sentinel_summary(self) -> str:
        """Format Project Sentinel summary"""
        data = summaries.get_project_sentinel_summary()
        parts = []
        parts.append("## PROJECT SENTINEL - CONTINUOUS IMPROVEMENT INITIATIVE\n")
        parts.append(f"**Lead:** {data.get('lead', 'N/A')}")
        parts.append(f"**Prize Draw Date:** {data.get('prize_draw_date', 'N/A')}")
        parts.append(f"**Scoring Deadline:** {data.get('scoring_deadline', 'N/A')}")
        parts.append(f"**Prizes:** {', '.join(data.get('prizes', []))}\n")

        parts.append("### Submissions Summary")
        parts.append(f"- **Total Submissions:** {data.get('total_submissions', 0)}")
        parts.append(f"- **Funded:** {data.get('funded_count', 0)}")
        parts.append(f"- **Active:** {data.get('active_count', 0)}")
        parts.append(f"- **Under Review:** {data.get('under_review_count', 0)}\n")

        parts.append("### All Submissions")
        parts.append("| # | Proposer | Topic | Status |")
        parts.append("|---|----------|-------|--------|")
        for sub in data.get("submissions", []):
            focus = f" - {sub.get('focus', '')}" if sub.get('focus') else ""
            parts.append(f"| {sub.get('number', '')} | {sub.get('proposer', '')} | {sub.get('topic', '')}{focus} | {sub.get('status', '')} |")

        parts.append("\n### Scoring Criteria")
        parts.append("| Criterion | Weight |")
        parts.append("|-----------|--------|")
        for crit in data.get("scoring_criteria", []):
            parts.append(f"| {crit.get('criterion', '')} | {crit.get('weight', '')} |")

        return "\n".join(parts)

    def _format_all_staff_table(self) -> str:
        """Format complete team pay table across all regions"""
        parts = []
        parts.append("## COMPLETE TEAM PAY - ALL REGIONS\n")

        # Australia
        aus = summaries.get_australia_staff_summary()
        if aus and aus.get("staff"):
            parts.append("### Australia Staff")
            parts.append(f"**Headcount: {len(aus['staff'])}**\n")
            parts.append("| Name | Position | Base Salary (AUD) | Retention Bonus | Total |")
            parts.append("|------|----------|-------------------|-----------------|-------|")
            for s in aus["staff"]:
                name = s.get("name", "")
                pos = s.get("position", "")
                salary = s.get("salary", s.get("base_salary", ""))
                bonus = s.get("retention_bonus", "-")
                total = s.get("total", salary)
                parts.append(f"| {name} | {pos} | {salary} | {bonus} | {total} |")

        # India
        india = summaries.get_india_staff_summary()
        if india and india.get("staff"):
            parts.append("\n### India Staff")
            parts.append(f"**Headcount: {len(india['staff'])}**\n")
            parts.append("| Name | Level | CTC (INR) | CTC (AUD) | Retention Bonus | Total (AUD) |")
            parts.append("|------|-------|-----------|-----------|-----------------|-------------|")
            for s in india["staff"]:
                parts.append(f"| {s.get('name', '')} | {s.get('level', '')} | {s.get('ctc_inr', '')} | {s.get('ctc_aud', '')} | {s.get('retention_bonus', '-')} | {s.get('total_with_bonus_aud', s.get('ctc_aud', ''))} |")

        # Malaysia
        malaysia = summaries.get_malaysia_staff_summary()
        if malaysia and malaysia.get("staff"):
            parts.append("\n### Malaysia Staff")
            parts.append(f"**Headcount: {len(malaysia['staff'])}**\n")
            parts.append("| Name | Level | Salary (MYR) | Salary (AUD) | Retention Bonus |")
            parts.append("|------|-------|--------------|--------------|-----------------|")
            for s in malaysia["staff"]:
                parts.append(f"| {s.get('name', '')} | {s.get('level', '')} | {s.get('salary_myr', '')} | {s.get('salary_aud', '')} | {s.get('retention_bonus', '-')} |")

        # Totals
        total_aus = len(aus.get("staff", [])) if aus else 0
        total_india = len(india.get("staff", [])) if india else 0
        total_malaysia = len(malaysia.get("staff", [])) if malaysia else 0
        total_all = total_aus + total_india + total_malaysia

        parts.append(f"\n### Summary")
        parts.append(f"- **Total Headcount:** {total_all}")
        parts.append(f"- Australia: {total_aus}")
        parts.append(f"- India: {total_india}")
        parts.append(f"- Malaysia: {total_malaysia}")

        return "\n".join(parts)

    def _format_retention_summary(self) -> str:
        """Format retention bonus summary"""
        data = summaries.get_retention_bonus_summary()
        parts = ["## RETENTION BONUS SUMMARY\n"]

        parts.append(f"**Total staff with bonuses:** {data.get('total_staff_with_bonuses', 0)}")
        parts.append(f"**Total annual cost:** {data.get('total_annual_cost_aud', 'N/A')}\n")

        parts.append("### Expires Feb 2026")
        parts.append("| Name | Bonus | Amount |")
        parts.append("|------|-------|--------|")
        for s in data.get("expires_feb_2026", []):
            parts.append(f"| {s.get('name', '')} | {s.get('bonus', '')} | {s.get('amount_aud', '')} |")

        parts.append("\n### Expires Aug 2026")
        parts.append("| Name | Bonus | Amount |")
        parts.append("|------|-------|--------|")
        for s in data.get("expires_aug_2026", []):
            amount = s.get('amount_aud', s.get('amount_myr', s.get('amount_inr', '')))
            parts.append(f"| {s.get('name', '')} | {s.get('bonus', '')} | {amount} |")

        return "\n".join(parts)

    def _format_staff_summary(self) -> str:
        """Format all staff summaries into a readable context"""
        parts = []

        # Australia staff
        aus = summaries.get_australia_staff_summary()
        if aus and aus.get("staff"):
            parts.append("## Australia Staff")
            parts.append(f"Total: {len(aus['staff'])} staff members\n")
            parts.append("| ID | Name | Position | Base Salary | With Bonus | Status |")
            parts.append("|-----|------|----------|-------------|------------|--------|")
            for s in aus["staff"]:
                status = s.get("status", "")
                parts.append(f"| {s.get('id', '')} | {s.get('name', '')} | {s.get('position', '')} | {s.get('base_salary', '')} | {s.get('with_bonus', '-')} | {status} |")

        # India staff
        india = summaries.get_india_staff_summary()
        if india and india.get("staff"):
            parts.append("\n## India Staff")
            parts.append(f"Total: {len(india['staff'])} staff members\n")
            parts.append("| ID | Name | Level | CTC (INR) | CTC (AUD) | Retention Bonus |")
            parts.append("|-----|------|-------|-----------|-----------|-----------------|")
            for s in india["staff"]:
                parts.append(f"| {s.get('id', '')} | {s.get('name', '')} | {s.get('level', '')} | {s.get('ctc_inr', '')} | {s.get('ctc_aud', '')} | {s.get('retention_bonus', 'None')} |")

        # Malaysia staff (if exists)
        try:
            mal = summaries.get_malaysia_staff_summary()
            if mal and mal.get("staff"):
                parts.append("\n## Malaysia Staff")
                parts.append(f"Total: {len(mal['staff'])} staff members\n")
                for s in mal["staff"]:
                    parts.append(f"- {s.get('name', '')}: Retention Bonus {s.get('retention_bonus', 'None')}")
        except AttributeError:
            pass

        if parts:
            return "\n".join(parts)
        return None

    def chat(
        self,
        message: str,
        conversation_id: Optional[int] = None,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
        max_context_chunks: int = 50,
    ) -> Dict[str, Any]:
        """
        Send a chat message and get a response using RAG.

        Args:
            message: User message
            conversation_id: Optional conversation ID to continue
            model: Model to use (claude-sonnet-4-20250514 for Anthropic, gpt-4o for OpenAI)
            temperature: Temperature for generation
            max_context_chunks: Maximum number of document chunks to retrieve

        Returns:
            Dictionary with response, conversation_id, and metadata
        """
        # Try Anthropic first, then OpenAI
        anthropic_client = self._get_anthropic_client()
        openai_client = self._get_openai_client()

        if not anthropic_client and not openai_client:
            raise RuntimeError("No LLM API configured. Please add an Anthropic or OpenAI API key.")

        # Get or create conversation
        if conversation_id:
            conversation = self.session.get(ChatConversation, conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
        else:
            conversation = ChatConversation()
            self.session.add(conversation)
            self.session.commit()
            self.session.refresh(conversation)

        # Save user message
        user_msg = ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content=message,
        )
        self.session.add(user_msg)
        self.session.commit()

        # Check for pre-computed summaries first
        summary_context = self._check_for_summary(message)

        # Retrieve relevant context from vector DB
        results, context_str = self._retrieve_context(message, limit=max_context_chunks)

        # Combine summary with vector results if available
        if summary_context:
            context_str = f"[PRE-COMPUTED SUMMARY - USE THIS DATA]\n{summary_context}\n\n[ADDITIONAL CONTEXT FROM SEARCH]\n{context_str}"

        # Anonymize context and query if anonymizer is enabled
        anonymized_context = context_str
        anonymized_message = message
        substitutions = {}

        if self.anonymizer:
            # Anonymize the retrieved context
            anonymized_context, context_subs = self.anonymizer.anonymize_for_llm(context_str)
            # Anonymize the user query
            anonymized_message, message_subs = self.anonymizer.anonymize_for_llm(message)
            # Combine substitutions
            substitutions = {**context_subs, **message_subs}

        # Build conversation history for Claude
        messages = []

        # System message with RAG context (anonymized if enabled)
        system_message = f"""You are a helpful AI assistant with access to a knowledge base about a Power Systems engineering team.

CONTEXT FROM KNOWLEDGE BASE:
{anonymized_context}

INSTRUCTIONS:
- Answer based on the provided context when possible
- If information is not in the context, clearly state that
- Be concise and helpful
- Cite sources when relevant

FORMATTING RULES:
- When presenting staff, salary, or compensation data: ALWAYS use markdown tables
- When presenting lists of people, projects, or items: use tables with columns
- Include ALL relevant data from the context - do not summarize or omit entries
- For salary queries: show Name, Position/Level, Region, Base Salary, Bonuses, Total
- For project queries: show Project Name, Client, Status, Key Details
- After tables, provide summary statistics (totals, averages, counts by category)
"""

        # Add conversation history (last 10 messages for context window management)
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
        )
        history = list(reversed(self.session.exec(stmt).all()))

        for msg in history:
            if msg.role in ["user", "assistant"]:
                # Use anonymized version for current user message
                content = anonymized_message if (msg.id == user_msg.id and msg.role == "user") else msg.content
                messages.append({"role": msg.role, "content": content})

        # Call LLM API (try Anthropic first, then OpenAI)
        try:
            if anthropic_client:
                # Use Anthropic Claude API
                # Claude uses separate system parameter, not in messages
                claude_model = model if model.startswith("claude") else "claude-sonnet-4-20250514"

                response = anthropic_client.messages.create(
                    model=claude_model,
                    max_tokens=4096,
                    system=system_message,
                    messages=messages,
                )

                assistant_message = response.content[0].text
                tokens_used = response.usage.input_tokens + response.usage.output_tokens
                self._llm_provider = "anthropic"

            elif openai_client:
                # Fall back to OpenAI
                openai_model = model if model.startswith("gpt") else "gpt-4o"
                all_messages = [{"role": "system", "content": system_message}] + messages

                response = openai_client.chat.completions.create(
                    model=openai_model,
                    messages=all_messages,
                    temperature=temperature,
                )

                assistant_message = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
                self._llm_provider = "openai"

            else:
                raise RuntimeError("No LLM client available")

        except Exception as e:
            # If Anthropic fails, try OpenAI as fallback
            if anthropic_client and openai_client and "anthropic" in str(type(e).__module__).lower():
                try:
                    openai_model = "gpt-4o"
                    all_messages = [{"role": "system", "content": system_message}] + messages

                    response = openai_client.chat.completions.create(
                        model=openai_model,
                        messages=all_messages,
                        temperature=temperature,
                    )

                    assistant_message = response.choices[0].message.content
                    tokens_used = response.usage.total_tokens
                    self._llm_provider = "openai"
                except Exception as e2:
                    raise RuntimeError(f"Both Anthropic and OpenAI failed. Anthropic: {e}, OpenAI: {e2}")
            else:
                provider = "Anthropic" if anthropic_client else "OpenAI"
                raise RuntimeError(f"{provider} API error: {e}")

        # De-anonymize the response if anonymizer is enabled
        response_plain = assistant_message
        response_html = assistant_message
        anonymization_stats = {}

        if self.anonymizer and substitutions:
            response_plain, response_html = self.anonymizer.deanonymize_with_markup(
                assistant_message,
                substitutions,
                markup_style="italic"
            )
            anonymization_stats = self.anonymizer.get_stats(substitutions)

        # Save assistant response (store de-anonymized version)
        sources_used = json.dumps([hit.get("id") for hit in results])
        assistant_msg = ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=response_plain if self.anonymizer else assistant_message,
            sources_used=sources_used,
            retrieved_chunks=len(results),
        )
        self.session.add(assistant_msg)

        # Update conversation title if first message
        if not conversation.title:
            # Use first 50 chars of user message as title
            conversation.title = message[:50] + ("..." if len(message) > 50 else "")

        from datetime import datetime
        conversation.updated_at = datetime.utcnow()
        self.session.commit()

        result = {
            "conversation_id": conversation.id,
            "response": response_plain if self.anonymizer else assistant_message,
            "response_html": response_html if self.anonymizer else None,
            "sources": results,
            "tokens_used": tokens_used,
            "chunks_retrieved": len(results),
        }

        # Add anonymization stats if enabled
        if anonymization_stats:
            result["anonymization"] = anonymization_stats

            # Add detailed substitutions for debugging/verification
            result["substitutions"] = [
                {
                    "original": sub.original,
                    "token": token,
                    "type": sub.entity_type,
                    "confidence": sub.confidence,
                }
                for token, sub in substitutions.items()
            ]

        return result

    def get_conversation_history(self, conversation_id: int) -> List[Dict[str, Any]]:
        """Get all messages in a conversation"""
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at)
        )
        messages = self.session.exec(stmt).all()

        return [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
                "sources_used": json.loads(msg.sources_used) if msg.sources_used else None,
                "retrieved_chunks": msg.retrieved_chunks,
            }
            for msg in messages
        ]

    def list_conversations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent conversations"""
        stmt = (
            select(ChatConversation)
            .order_by(ChatConversation.updated_at.desc())
            .limit(limit)
        )
        conversations = self.session.exec(stmt).all()

        return [
            {
                "id": conv.id,
                "title": conv.title or "Untitled",
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
            }
            for conv in conversations
        ]

    def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation and all its messages"""
        conversation = self.session.get(ChatConversation, conversation_id)
        if not conversation:
            return False

        # Delete all messages first
        stmt = select(ChatMessage).where(ChatMessage.conversation_id == conversation_id)
        messages = self.session.exec(stmt).all()
        for msg in messages:
            self.session.delete(msg)

        # Delete conversation
        self.session.delete(conversation)
        self.session.commit()
        return True
