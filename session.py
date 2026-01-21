#!/usr/bin/env python3
"""
Session Management - Handles saving and loading conversation sessions.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class Session:
    """Manages conversation sessions with save/load functionality."""

    def __init__(self, session_dir: Optional[str] = None):
        """
        Initialize session manager.

        Args:
            session_dir: Directory to store sessions. Defaults to ~/.perplexity-cli/sessions
        """
        if session_dir:
            self.session_dir = Path(session_dir).expanduser()
        else:
            self.session_dir = Path.home() / ".perplexity-cli" / "sessions"
        
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.messages: List[Dict[str, str]] = []
        self.current_file: Optional[str] = None
        self.created_at: str = datetime.now().isoformat()
        self.model: str = "sonar-pro"

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the session."""
        self.messages.append({"role": role, "content": content})

    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in the session."""
        return self.messages.copy()

    def clear(self) -> None:
        """Clear all messages from the session."""
        self.messages = []
        self.created_at = datetime.now().isoformat()

    def save(self, name: Optional[str] = None) -> str:
        """
        Save the current session to disk.

        Args:
            name: Optional name for the session file.

        Returns:
            The filename of the saved session.
        """
        if name:
            filename = f"{name}.json"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{timestamp}.json"

        filepath = self.session_dir / filename
        
        data = {
            "created_at": self.created_at,
            "saved_at": datetime.now().isoformat(),
            "model": self.model,
            "messages": self.messages,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.current_file = filename
        return filename

    def load(self, filename: str) -> bool:
        """
        Load a session from disk.

        Args:
            filename: The session file to load.

        Returns:
            True if successful, False otherwise.
        """
        filepath = self.session_dir / filename
        if not filepath.exists():
            # Try adding .json extension
            filepath = self.session_dir / f"{filename}.json"
            if not filepath.exists():
                return False

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.messages = data.get("messages", [])
            self.created_at = data.get("created_at", datetime.now().isoformat())
            self.model = data.get("model", "sonar-pro")
            self.current_file = filepath.name
            return True
        except (json.JSONDecodeError, KeyError):
            return False

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all saved sessions.

        Returns:
            List of session metadata dicts.
        """
        sessions = []
        for filepath in self.session_dir.glob("*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Get first user message as preview
                preview = ""
                for msg in data.get("messages", []):
                    if msg.get("role") == "user":
                        preview = msg.get("content", "")[:50]
                        if len(msg.get("content", "")) > 50:
                            preview += "..."
                        break

                sessions.append({
                    "filename": filepath.name,
                    "created_at": data.get("created_at", ""),
                    "saved_at": data.get("saved_at", ""),
                    "model": data.get("model", "unknown"),
                    "message_count": len(data.get("messages", [])),
                    "preview": preview,
                })
            except (json.JSONDecodeError, KeyError):
                continue

        # Sort by saved_at, most recent first
        sessions.sort(key=lambda x: x.get("saved_at", ""), reverse=True)
        return sessions

    def delete(self, filename: str) -> bool:
        """
        Delete a saved session.

        Args:
            filename: The session file to delete.

        Returns:
            True if successful, False otherwise.
        """
        filepath = self.session_dir / filename
        if not filepath.exists():
            filepath = self.session_dir / f"{filename}.json"
        
        if filepath.exists():
            filepath.unlink()
            return True
        return False
