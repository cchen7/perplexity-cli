#!/usr/bin/env python3
"""
Perplexity API Client - Handles communication with the Perplexity Sonar API.
"""

import json
import os
from typing import Generator, List, Dict, Any, Optional

import requests


class PerplexityAPI:
    """Client for interacting with the Perplexity Sonar API."""

    API_URL = "https://api.perplexity.ai/chat/completions"
    AVAILABLE_MODELS = ["sonar", "sonar-pro", "sonar-reasoning", "sonar-reasoning-pro"]
    DEFAULT_MODEL = "sonar-pro"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the API client.

        Args:
            api_key: Perplexity API key. Falls back to PPLX_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("PPLX_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "API key not found. Set PPLX_API_KEY environment variable or pass api_key."
            )

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = DEFAULT_MODEL,
        stream: bool = True,
    ) -> Generator[str, None, Dict[str, Any]]:
        """
        Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            model: The model to use.
            stream: Whether to stream the response.

        Yields:
            Content chunks if streaming.

        Returns:
            Final response metadata including citations.
        """
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        data = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }

        if stream:
            return self._stream_response(headers, data)
        else:
            return self._sync_response(headers, data)

    def _stream_response(
        self, headers: Dict[str, str], data: Dict[str, Any]
    ) -> Generator[str, None, Dict[str, Any]]:
        """Handle streaming response."""
        citations = []
        full_content = ""

        with requests.post(
            self.API_URL, headers=headers, json=data, stream=True
        ) as response:
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue

                line_str = line.decode("utf-8")
                if not line_str.startswith("data: "):
                    continue

                json_str = line_str[6:]
                if json_str == "[DONE]":
                    break

                try:
                    chunk = json.loads(json_str)
                    if "citations" in chunk:
                        citations = chunk["citations"]

                    if "choices" in chunk and chunk["choices"]:
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            full_content += content
                            yield content
                except json.JSONDecodeError:
                    continue

        return {"citations": citations, "content": full_content}

    def _sync_response(
        self, headers: Dict[str, str], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle non-streaming response."""
        response = requests.post(self.API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        content = ""
        if "choices" in result and result["choices"]:
            content = result["choices"][0].get("message", {}).get("content", "")

        return {
            "content": content,
            "citations": result.get("citations", []),
        }

    def summarize(
        self, text: str, model: str = DEFAULT_MODEL
    ) -> str:
        """
        Summarize a conversation to reduce token count.

        Args:
            text: The text to summarize.
            model: The model to use.

        Returns:
            Summarized text.
        """
        messages = [
            {
                "role": "system",
                "content": "Summarize the following conversation concisely, preserving key context and facts.",
            },
            {"role": "user", "content": text},
        ]

        result = self._sync_response(
            {
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            {"model": model, "messages": messages, "stream": False},
        )

        return result.get("content", text)
