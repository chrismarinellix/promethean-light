"""Chatbot with RAG (Retrieval-Augmented Generation) using OpenAI"""

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
    """RAG-powered chatbot using OpenAI API"""

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

    def _get_openai_client(self):
        """Get OpenAI client with API key from encrypted storage"""
        if self._openai_client is not None:
            return self._openai_client

        # Load API key from database
        stmt = select(ApiKey).where(ApiKey.service == "openai", ApiKey.enabled == True)
        api_key_record = self.session.exec(stmt).first()

        if not api_key_record:
            raise ValueError(
                "OpenAI API key not configured. "
                "Run: mydata api-key add openai <your-key>"
            )

        # Decrypt API key
        api_key = self.crypto.decrypt_str(api_key_record.encrypted_key)

        # Initialize OpenAI client
        try:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )

        return self._openai_client

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

        # Staff queries
        staff_keywords = ["staff", "team", "employee", "people", "members", "who works", "team members"]
        if any(kw in query_lower for kw in staff_keywords):
            return self._format_staff_summary()

        return None

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
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_context_chunks: int = 5,
    ) -> Dict[str, Any]:
        """
        Send a chat message and get a response using RAG.

        Args:
            message: User message
            conversation_id: Optional conversation ID to continue
            model: OpenAI model to use
            temperature: Temperature for generation
            max_context_chunks: Maximum number of document chunks to retrieve

        Returns:
            Dictionary with response, conversation_id, and metadata
        """
        client = self._get_openai_client()

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

        # Build conversation history
        messages = []

        # System message with RAG context (anonymized if enabled)
        system_message = f"""You are a helpful AI assistant with access to a knowledge base.
Use the following context from the knowledge base to answer questions. If the context doesn't contain relevant information, say so clearly.

CONTEXT FROM KNOWLEDGE BASE:
{anonymized_context}

Instructions:
- Answer based on the provided context when possible
- If information is not in the context, clearly state that
- Be concise and helpful
- Cite sources when relevant (e.g., "According to Document 1...")
"""
        messages.append({"role": "system", "content": system_message})

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

        # Call OpenAI API (with anonymized data if enabled)
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )

            assistant_message = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

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
