#!/usr/bin/env python3
"""
Configuration Management - Handles loading and saving configuration.
"""

import os
from pathlib import Path
from typing import Optional, Any
import yaml


DEFAULT_CONFIG = {
    "model": "sonar-pro",
    "system_prompt": "You are a helpful AI assistant with real-time search capabilities.",
    "input_token_limit": 3000,
    "output_token_limit": 1000,
    "auto_save": False,
    "session_dir": "~/.perplexity-cli/sessions",
}


class Config:
    """Manages CLI configuration."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to config file. Defaults to ~/.perplexity-cli/config.yaml
        """
        if config_path:
            self.config_path = Path(config_path).expanduser()
        else:
            self.config_path = Path.home() / ".perplexity-cli" / "config.yaml"

        self._config = DEFAULT_CONFIG.copy()
        self._load()

    def _load(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f) or {}
                self._config.update(user_config)
            except (yaml.YAMLError, IOError):
                pass

    def save(self) -> None:
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self._config, f, default_flow_style=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value

    @property
    def api_key(self) -> str:
        """Get API key from environment or config."""
        return os.environ.get("PPLX_API_KEY", self._config.get("api_key", ""))

    @property
    def model(self) -> str:
        """Get the model to use."""
        return self._config.get("model", DEFAULT_CONFIG["model"])

    @model.setter
    def model(self, value: str) -> None:
        """Set the model."""
        self._config["model"] = value

    @property
    def system_prompt(self) -> str:
        """Get the system prompt."""
        return self._config.get("system_prompt", DEFAULT_CONFIG["system_prompt"])

    @system_prompt.setter
    def system_prompt(self, value: str) -> None:
        """Set the system prompt."""
        self._config["system_prompt"] = value

    @property
    def input_token_limit(self) -> int:
        """Get input token limit."""
        return self._config.get("input_token_limit", DEFAULT_CONFIG["input_token_limit"])

    @property
    def output_token_limit(self) -> int:
        """Get output token limit."""
        return self._config.get("output_token_limit", DEFAULT_CONFIG["output_token_limit"])

    @property
    def auto_save(self) -> bool:
        """Get auto-save setting."""
        return self._config.get("auto_save", DEFAULT_CONFIG["auto_save"])

    @property
    def session_dir(self) -> str:
        """Get session directory."""
        return self._config.get("session_dir", DEFAULT_CONFIG["session_dir"])
