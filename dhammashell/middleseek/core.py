"""
Core functionality for MiddleSeek protocol.
"""

import random
import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DharmaProtocol:
    """Handles Dharma wisdom."""

    def __init__(self):
        self.wisdoms = [
            "The root of suffering is attachment.",
            "All conditioned things are impermanent.",
            "With our thoughts, we make the world.",
            "Peace comes from within.",
            "The mind is everything.",
            "In the end, only three things matter: how much you loved, how gently you lived, and how gracefully you let go.",
            "The way is not in the sky. The way is in the heart.",
            "You yourself deserve your love and affection.",
            "The only real failure is not to be true to the best one knows.",
            "Happiness never decreases by being shared.",
        ]

    def get_wisdom(self) -> str:
        return random.choice(self.wisdoms)


class MiddleSeekCore:
    """Core functionality for MiddleSeek protocol."""

    def __init__(self, api_key: str):
        if not api_key or not isinstance(api_key, str):
            raise ValueError("Invalid API key")

        self.api_key = api_key.strip()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/kusalatech/dhammashell",
            "X-Title": "DhammaShell",
        }
        self.base_url = "https://openrouter.ai/api/v1"

    def generate_response(self, message: str, compassion_score: int) -> str:
        """Generate a mindful response."""
        if not message or not isinstance(message, str):
            raise ValueError("Invalid message")

        if not isinstance(compassion_score, int) or not 0 <= compassion_score <= 5:
            raise ValueError("Invalid compassion score")

        try:
            response = self._call_openrouter(message)

            # Add Dharma wisdom for high compassion scores
            if compassion_score >= 4:
                wisdom = DharmaProtocol().get_wisdom()
                response += f"\n\nDharma Wisdom: {wisdom}"

            return response

        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            return "I understand your message and am here to support you."

    def _call_openrouter(self, message: str) -> str:
        """Call OpenRouter API."""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "anthropic/claude-3-opus-20240229",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a mindful and compassionate AI assistant. Respond with kindness and understanding.",
                        },
                        {"role": "user", "content": message},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise
