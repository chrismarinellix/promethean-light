"""Anonymization service for protecting PII when sending data to external LLMs"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import hashlib


@dataclass
class Substitution:
    """Represents a single anonymization substitution"""
    original: str
    token: str
    entity_type: str
    confidence: int  # 0-100
    position: Tuple[int, int]  # Start, end indices
    detection_method: str  # "regex", "spacy", "whitelist"


class Anonymizer:
    """
    Hybrid PII anonymizer for LLM context protection.

    Uses multiple detection methods:
    - Regex patterns for structured data (emails, phones, paths)
    - spaCy NER for names and organizations
    - Custom whitelists for known entities (clients, projects)
    """

    def __init__(
        self,
        enable_spacy: bool = True,
        known_clients: Optional[List[str]] = None,
        known_projects: Optional[List[str]] = None,
        known_employees: Optional[List[str]] = None,
    ):
        self.enable_spacy = enable_spacy
        self.known_clients = known_clients or []
        self.known_projects = known_projects or []
        self.known_employees = known_employees or []

        # Counters for token generation
        self._person_counter = 0
        self._email_counter = 0
        self._phone_counter = 0
        self._org_counter = 0
        self._client_counter = 0
        self._project_counter = 0
        self._location_counter = 0

        # Maps for consistent tokenization within a session
        self._token_cache: Dict[str, str] = {}
        self._reverse_cache: Dict[str, str] = {}

        # Load spaCy model lazily
        self._nlp = None

    @property
    def nlp(self):
        """Lazy load spaCy model"""
        if self._nlp is None and self.enable_spacy:
            try:
                import spacy
                self._nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("⚠️  spaCy model not found. Run: python -m spacy download en_core_web_sm")
                print("   Falling back to regex-only anonymization")
                self.enable_spacy = False
        return self._nlp

    def anonymize_for_llm(
        self,
        text: str
    ) -> Tuple[str, Dict[str, Substitution]]:
        """
        Anonymize text before sending to external LLM.

        Returns:
            (anonymized_text, mapping_dict)
        """
        substitutions: Dict[str, Substitution] = {}
        anonymized = text

        # 1. Apply whitelist-based anonymization (highest priority)
        anonymized, whitelist_subs = self._anonymize_whitelists(anonymized)
        substitutions.update(whitelist_subs)

        # 2. Apply regex-based anonymization (structured data)
        anonymized, regex_subs = self._anonymize_regex(anonymized)
        substitutions.update(regex_subs)

        # 3. Apply spaCy NER (context-aware)
        if self.enable_spacy:
            anonymized, ner_subs = self._anonymize_ner(anonymized)
            substitutions.update(ner_subs)

        # 4. Anonymize file paths
        anonymized, path_subs = self._anonymize_paths(anonymized)
        substitutions.update(path_subs)

        return anonymized, substitutions

    def deanonymize_with_markup(
        self,
        text: str,
        substitutions: Dict[str, Substitution],
        markup_style: str = "italic"
    ) -> Tuple[str, str]:
        """
        De-anonymize text and add visual markup for verification.

        Args:
            text: Anonymized text from LLM
            substitutions: Mapping from anonymize_for_llm()
            markup_style: "italic", "bold", "color_coded", "html"

        Returns:
            (plain_text_with_markdown, html_with_markup)
        """
        plain_text = text
        html_text = text

        # Sort by token length (longest first) to avoid partial replacements
        sorted_subs = sorted(
            substitutions.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )

        for token, sub in sorted_subs:
            original = sub.original
            confidence = sub.confidence

            # Replace in plain text with markdown markup
            if markup_style == "italic":
                plain_text = plain_text.replace(token, f"*{original}*")
            elif markup_style == "bold":
                plain_text = plain_text.replace(token, f"**{original}**")
            else:
                plain_text = plain_text.replace(token, original)

            # Replace in HTML with styled span
            html_markup = self._get_html_markup(original, confidence, token)
            html_text = html_text.replace(token, html_markup)

        return plain_text, html_text

    def _get_html_markup(self, text: str, confidence: int, token: str) -> str:
        """Generate HTML markup with confidence color coding"""
        if confidence >= 90:
            bg_color = "#e8f5e9"  # Light green
            border_color = "#4caf50"  # Green
        elif confidence >= 70:
            bg_color = "#fff9c4"  # Light yellow
            border_color = "#ffc107"  # Yellow
        else:
            bg_color = "#ffebee"  # Light red
            border_color = "#f44336"  # Red

        return (
            f'<span class="deano" '
            f'data-token="{token}" '
            f'data-confidence="{confidence}" '
            f'style="font-style: italic; '
            f'background: {bg_color}; '
            f'border-bottom: 2px solid {border_color}; '
            f'padding: 2px 4px; '
            f'border-radius: 3px;" '
            f'title="Confidence: {confidence}%, Original token: {token}">'
            f'{text}'
            f'</span>'
        )

    def _anonymize_whitelists(self, text: str) -> Tuple[str, Dict[str, Substitution]]:
        """Anonymize known entities from whitelists"""
        substitutions = {}

        # Clients (highest confidence - we know these)
        for client in self.known_clients:
            if client in text:
                token = self._get_cached_token(client, "client")
                text = text.replace(client, token)
                substitutions[token] = Substitution(
                    original=client,
                    token=token,
                    entity_type="CLIENT",
                    confidence=100,
                    position=(0, 0),  # Position tracking would require more complex logic
                    detection_method="whitelist"
                )

        # Projects
        for project in self.known_projects:
            if project in text:
                token = self._get_cached_token(project, "project")
                text = text.replace(project, token)
                substitutions[token] = Substitution(
                    original=project,
                    token=token,
                    entity_type="PROJECT",
                    confidence=100,
                    position=(0, 0),
                    detection_method="whitelist"
                )

        # Employees
        for employee in self.known_employees:
            if employee in text:
                token = self._get_cached_token(employee, "person")
                text = text.replace(employee, token)
                substitutions[token] = Substitution(
                    original=employee,
                    token=token,
                    entity_type="PERSON",
                    confidence=100,
                    position=(0, 0),
                    detection_method="whitelist"
                )

        return text, substitutions

    def _anonymize_regex(self, text: str) -> Tuple[str, Dict[str, Substitution]]:
        """Anonymize structured data using regex patterns"""
        substitutions = {}

        # Email addresses (very high confidence)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            email = match.group()
            token = self._get_cached_token(email, "email")
            text = text.replace(email, token)
            substitutions[token] = Substitution(
                original=email,
                token=token,
                entity_type="EMAIL",
                confidence=99,
                position=match.span(),
                detection_method="regex"
            )

        # Phone numbers (Australian and international formats)
        phone_patterns = [
            r'\+61\s?\d{1,2}\s?\d{4}\s?\d{4}',  # +61 format
            r'\b04\d{2}\s?\d{3}\s?\d{3}\b',  # 04xx format
            r'\(\d{2,3}\)\s?\d{4}\s?\d{4}',  # (xx) format
        ]
        for pattern in phone_patterns:
            for match in re.finditer(pattern, text):
                phone = match.group()
                token = self._get_cached_token(phone, "phone")
                text = text.replace(phone, token)
                substitutions[token] = Substitution(
                    original=phone,
                    token=token,
                    entity_type="PHONE",
                    confidence=95,
                    position=match.span(),
                    detection_method="regex"
                )

        return text, substitutions

    def _anonymize_ner(self, text: str) -> Tuple[str, Dict[str, Substitution]]:
        """Anonymize using spaCy Named Entity Recognition"""
        if not self.nlp:
            return text, {}

        substitutions = {}
        doc = self.nlp(text)

        # Process entities (sort by length descending to avoid partial replacements)
        entities = sorted(doc.ents, key=lambda e: len(e.text), reverse=True)

        for ent in entities:
            # Skip if already processed by whitelist/regex
            if any(token in ent.text for token in substitutions.keys()):
                continue

            entity_text = ent.text
            entity_type = ent.label_

            # Map spaCy entity types to our types
            if entity_type == "PERSON":
                token = self._get_cached_token(entity_text, "person")
                confidence = min(int(95), 100)  # spaCy is ~90-95% accurate
                final_type = "PERSON"
            elif entity_type == "ORG":
                token = self._get_cached_token(entity_text, "org")
                confidence = min(int(85), 100)  # Orgs are harder
                final_type = "ORGANIZATION"
            elif entity_type == "GPE":  # Geo-political entity (locations)
                token = self._get_cached_token(entity_text, "location")
                confidence = min(int(80), 100)
                final_type = "LOCATION"
            else:
                continue  # Skip other entity types

            # Boost confidence if entity is capitalized properly
            if entity_text.istitle() or entity_text.isupper():
                confidence = min(confidence + 5, 100)

            text = text.replace(entity_text, token)
            substitutions[token] = Substitution(
                original=entity_text,
                token=token,
                entity_type=final_type,
                confidence=confidence,
                position=(ent.start_char, ent.end_char),
                detection_method="spacy"
            )

        return text, substitutions

    def _anonymize_paths(self, text: str) -> Tuple[str, Dict[str, Substitution]]:
        """Anonymize file paths to remove usernames"""
        substitutions = {}

        # Windows paths: C:/Users/username/...
        path_pattern = r'([A-Z]:[/\\]Users[/\\])([^/\\]+)([/\\])'
        for match in re.finditer(path_pattern, text):
            full_match = match.group()
            prefix = match.group(1)
            username = match.group(2)
            suffix = match.group(3)

            token = f"[USER_{self._get_user_id(username)}]"
            replacement = f"{prefix}{token}{suffix}"

            text = text.replace(full_match, replacement)
            substitutions[token] = Substitution(
                original=username,
                token=token,
                entity_type="USERNAME",
                confidence=100,
                position=match.span(),
                detection_method="regex"
            )

        return text, substitutions

    def _get_cached_token(self, original: str, entity_type: str) -> str:
        """Get or create a consistent token for an entity"""
        # Use hash for cache key to handle case variations
        cache_key = f"{entity_type}:{original.lower()}"

        if cache_key in self._token_cache:
            return self._token_cache[cache_key]

        # Generate new token
        if entity_type == "person":
            self._person_counter += 1
            token = f"[PERSON_{self._person_counter:03d}]"
        elif entity_type == "email":
            self._email_counter += 1
            token = f"[EMAIL_{self._email_counter:03d}]"
        elif entity_type == "phone":
            self._phone_counter += 1
            token = f"[PHONE_{self._phone_counter:03d}]"
        elif entity_type == "org":
            self._org_counter += 1
            token = f"[ORG_{self._org_counter:03d}]"
        elif entity_type == "client":
            self._client_counter += 1
            # Use letter sequence for clients: A, B, C, ...
            letter = chr(65 + self._client_counter - 1) if self._client_counter <= 26 else f"{self._client_counter}"
            token = f"[CLIENT_{letter}]"
        elif entity_type == "project":
            self._project_counter += 1
            token = f"[PROJECT_{self._project_counter:03d}]"
        elif entity_type == "location":
            self._location_counter += 1
            token = f"[LOCATION_{self._location_counter:03d}]"
        else:
            token = f"[REDACTED_{entity_type.upper()}]"

        # Cache both directions
        self._token_cache[cache_key] = token
        self._reverse_cache[token] = original

        return token

    def _get_user_id(self, username: str) -> str:
        """Generate consistent user ID from username"""
        # Use first 3 chars of hash for short ID
        hash_val = hashlib.md5(username.encode()).hexdigest()[:3].upper()
        return hash_val

    def get_stats(self, substitutions: Dict[str, Substitution]) -> Dict[str, Any]:
        """Get statistics about anonymization"""
        if not substitutions:
            return {
                "total_substitutions": 0,
                "avg_confidence": 0,
                "low_confidence_count": 0,
                "by_type": {}
            }

        confidences = [sub.confidence for sub in substitutions.values()]
        low_confidence = sum(1 for c in confidences if c < 70)

        by_type = {}
        for sub in substitutions.values():
            entity_type = sub.entity_type
            by_type[entity_type] = by_type.get(entity_type, 0) + 1

        return {
            "total_substitutions": len(substitutions),
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "low_confidence_count": low_confidence,
            "by_type": by_type,
            "min_confidence": min(confidences) if confidences else 0,
            "max_confidence": max(confidences) if confidences else 0,
        }
