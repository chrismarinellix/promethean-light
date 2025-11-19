"""API client for talking to running daemon"""

import requests
from typing import Optional, List, Dict
from .settings import settings


class Client:
    """Client for talking to Promethean Light daemon API"""

    def __init__(self, base_url: str = f"http://{settings.api_host}:{settings.api_port}"):
        self.base_url = base_url

    def is_alive(self) -> bool:
        """Check if daemon is running"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=1)
            return response.status_code == 200
        except Exception:
            return False

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for documents"""
        try:
            response = requests.post(
                f"{self.base_url}/search",
                json={"query": query, "limit": limit},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Search failed: {e}")

    def add_text(self, text: str, source: str = "cli") -> Dict:
        """Add text document"""
        try:
            response = requests.post(
                f"{self.base_url}/add",
                json={"text": text, "source": source},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Add failed: {e}")

    def stats(self) -> Dict:
        """Get statistics"""
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Stats failed: {e}")

    def tags(self) -> List[Dict]:
        """Get all tags"""
        try:
            response = requests.get(f"{self.base_url}/tags", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Tags failed: {e}")

    def add_email(self, email_address: str, password: str, imap_server: str = "imap.gmail.com", imap_port: int = 993) -> Dict:
        """Add email account for watching"""
        try:
            response = requests.post(
                f"{self.base_url}/email/add",
                json={
                    "email_address": email_address,
                    "password": password,
                    "imap_server": imap_server,
                    "imap_port": imap_port
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Add email failed: {e}")

    def get_summary(self, summary_name: str) -> Dict:
        """Get pre-computed summary"""
        try:
            response = requests.get(f"{self.base_url}/summary/{summary_name}", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Get summary failed: {e}")

