"""Obsidian Vault Manager for reading and writing notes."""

from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import re

from loguru import logger


class ObsidianVaultManager:
    """Manager for interacting with Obsidian Vault files."""

    def __init__(self, vault_path: str | Path) -> None:
        """Initialize the Obsidian Vault Manager.

        Args:
            vault_path: Path to the Obsidian Vault directory.

        Raises:
            ValueError: If the vault path does not exist or is not a directory.
        """
        self.vault_path = Path(vault_path).expanduser().resolve()
        
        if not self.vault_path.exists():
            raise ValueError(f"Obsidian Vault path does not exist: {self.vault_path}")
        
        if not self.vault_path.is_dir():
            raise ValueError(f"Obsidian Vault path is not a directory: {self.vault_path}")
        
        logger.info(f"ObsidianVaultManager initialized with vault: {self.vault_path}")

    def read_note(self, note_path: str) -> str | None:
        """Read a note from the vault.

        Args:
            note_path: Relative path to the note file (e.g., 'Daily Notes/2024-01-01.md').

        Returns:
            Content of the note file, or None if file does not exist.
        """
        full_path = self.vault_path / note_path
        
        # 보안: vault 경로 밖으로 나가는 경로 방지
        try:
            full_path.resolve().relative_to(self.vault_path.resolve())
        except ValueError:
            logger.error(f"ObsidianVaultManager: Attempted to access path outside vault: {note_path}")
            return None
        
        if not full_path.exists():
            logger.warning(f"ObsidianVaultManager: Note not found: {note_path}")
            return None
        
        try:
            return full_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"ObsidianVaultManager: Error reading note '{note_path}': {e}")
            return None

    def write_note(self, note_path: str, content: str, frontmatter: Dict[str, Any] | None = None) -> bool:
        """Write a note to the vault.

        Args:
            note_path: Relative path to the note file.
            content: Content of the note (body text).
            frontmatter: Optional frontmatter dictionary to add as YAML frontmatter.

        Returns:
            True if successful, False otherwise.
        """
        full_path = self.vault_path / note_path
        
        # 보안: vault 경로 밖으로 나가는 경로 방지
        try:
            full_path.resolve().relative_to(self.vault_path.resolve())
        except ValueError:
            logger.error(f"ObsidianVaultManager: Attempted to write path outside vault: {note_path}")
            return False
        
        # 디렉토리 생성
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Frontmatter가 있으면 추가
        if frontmatter:
            frontmatter_str = "---\n"
            for key, value in frontmatter.items():
                if isinstance(value, str):
                    frontmatter_str += f"{key}: {value}\n"
                elif isinstance(value, (int, float, bool)):
                    frontmatter_str += f"{key}: {value}\n"
                else:
                    frontmatter_str += f"{key}: {json.dumps(value)}\n"
            frontmatter_str += "---\n\n"
            content = frontmatter_str + content
        
        try:
            full_path.write_text(content, encoding="utf-8")
            logger.info(f"ObsidianVaultManager: Successfully wrote note: {note_path}")
            return True
        except Exception as e:
            logger.error(f"ObsidianVaultManager: Error writing note '{note_path}': {e}")
            return False

    def create_daily_note(self, date: datetime | None = None, content: str = "") -> str | None:
        """Create a daily note with date-based naming.

        Args:
            date: Date for the daily note. If None, uses today's date.
            content: Initial content for the note.

        Returns:
            Path to the created note, or None if creation failed.
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        note_path = f"Daily Notes/{date_str}.md"
        
        frontmatter = {
            "date": date_str,
            "created": datetime.now().isoformat(),
        }
        
        if not content:
            content = f"# {date_str}\n\n"
        
        if self.write_note(note_path, content, frontmatter):
            return note_path
        return None

    def list_notes(self, directory: str = "", pattern: str = "*.md") -> List[str]:
        """List notes in the vault.

        Args:
            directory: Subdirectory to search in (relative to vault root).
            pattern: File pattern to match (default: "*.md").

        Returns:
            List of relative paths to matching notes.
        """
        search_path = self.vault_path / directory if directory else self.vault_path
        
        # 보안: vault 경로 밖으로 나가는 경로 방지
        try:
            search_path.resolve().relative_to(self.vault_path.resolve())
        except ValueError:
            logger.error(f"ObsidianVaultManager: Attempted to list path outside vault: {directory}")
            return []
        
        if not search_path.exists():
            return []
        
        notes = []
        for note_file in search_path.rglob(pattern):
            relative_path = note_file.relative_to(self.vault_path)
            notes.append(str(relative_path))
        
        return sorted(notes)

    def search_notes(self, query: str, directory: str = "") -> List[Dict[str, Any]]:
        """Search notes by content.

        Args:
            query: Search query string.
            directory: Subdirectory to search in (relative to vault root).

        Returns:
            List of dictionaries containing note path and matching lines.
        """
        notes = self.list_notes(directory)
        results = []
        
        query_lower = query.lower()
        
        for note_path in notes:
            content = self.read_note(note_path)
            if content and query_lower in content.lower():
                # 매칭되는 라인 찾기
                lines = content.split("\n")
                matching_lines = []
                for i, line in enumerate(lines, 1):
                    if query_lower in line.lower():
                        matching_lines.append({"line_number": i, "content": line.strip()})
                
                if matching_lines:
                    results.append({
                        "path": note_path,
                        "matches": matching_lines[:5],  # 최대 5개 라인만 반환
                    })
        
        return results

    def get_note_tags(self, note_path: str) -> List[str]:
        """Extract tags from a note.

        Args:
            note_path: Relative path to the note file.

        Returns:
            List of tags found in the note.
        """
        content = self.read_note(note_path)
        if not content:
            return []
        
        # Obsidian 태그 형식: #tag 또는 #tag/subtag
        tag_pattern = r'#([a-zA-Z0-9_\-/]+)'
        tags = re.findall(tag_pattern, content)
        
        return list(set(tags))  # 중복 제거

    def append_to_note(self, note_path: str, content: str) -> bool:
        """Append content to an existing note.

        Args:
            note_path: Relative path to the note file.
            content: Content to append.

        Returns:
            True if successful, False otherwise.
        """
        existing_content = self.read_note(note_path)
        if existing_content is None:
            # 파일이 없으면 새로 생성
            return self.write_note(note_path, content)
        
        new_content = existing_content + "\n\n" + content
        return self.write_note(note_path, new_content)
