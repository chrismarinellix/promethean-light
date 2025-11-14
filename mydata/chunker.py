"""Intelligent chunking for large files - optimized for token efficiency"""

from pathlib import Path
from typing import List, Dict
import re


class SmartChunker:
    """Intelligently chunks files by topic, region, or structure"""

    def __init__(self, max_chunk_size: int = 2000):
        self.max_chunk_size = max_chunk_size

    def chunk_staff_file(self, file_path: Path) -> List[Dict]:
        """Chunk staff file by region and topic"""
        content = file_path.read_text(encoding='utf-8')

        chunks = []

        # Split into logical sections
        sections = self._split_by_sections(content)

        for section_name, section_text in sections.items():
            # Further chunk if section is too large
            if len(section_text) > self.max_chunk_size:
                sub_chunks = self._chunk_by_paragraphs(section_text, self.max_chunk_size)
                for i, chunk_text in enumerate(sub_chunks):
                    chunks.append({
                        "text": chunk_text,
                        "metadata": {
                            "section": section_name,
                            "chunk_index": i,
                            "source_file": str(file_path)
                        }
                    })
            else:
                chunks.append({
                    "text": section_text,
                    "metadata": {
                        "section": section_name,
                        "source_file": str(file_path)
                    }
                })

        return chunks

    def _split_by_sections(self, content: str) -> Dict[str, str]:
        """Split content into logical sections"""
        sections = {}

        # Detect Australia staff section
        australia_match = re.search(
            r'(?:Employee.*Description.*AUD.*GRD.*)(.*?)(?=Employee.*Description.*MYR|Employee ID.*INR|$)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if australia_match:
            sections['australia_staff'] = australia_match.group(0)[:self.max_chunk_size]

        # Detect Malaysia staff section
        malaysia_match = re.search(
            r'(?:Employee.*Description.*MYR.*GRD.*)(.*?)(?=Employee ID.*INR|$)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if malaysia_match:
            sections['malaysia_staff'] = malaysia_match.group(0)[:self.max_chunk_size]

        # Detect India staff section (CTC format)
        india_match = re.search(
            r'(?:Employee ID.*ANNUAL.*CTC.*)(.*?)(?:---|\n\n\n)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if india_match:
            sections['india_staff'] = india_match.group(0)[:self.max_chunk_size]

        # Detect retention bonus section
        bonus_match = re.search(
            r'(?:retention bonus|10%.*February|10%.*August)(.*?)(?:\n\n\n|---)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if bonus_match:
            sections['retention_bonuses'] = bonus_match.group(0)[:self.max_chunk_size]

        # Everything else goes into general
        if not sections:
            sections['general'] = content[:self.max_chunk_size]

        return sections

    def _chunk_by_paragraphs(self, text: str, max_size: int) -> List[str]:
        """Chunk text by paragraphs with overlap"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) < max_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text[:max_size]]
