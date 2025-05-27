"""
Core functionality for MiddleSeek protocol.
"""

import random
import logging
import requests
import time
import uuid
import json
import os
from typing import Dict, Optional, Any, List, Tuple
from ratelimit import limits, sleep_and_retry
from ..config import config
from ..prompt import MiddleSeekPrompt, PromptType

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# File handler for debug.log
debug_handler = logging.FileHandler(os.path.join(log_dir, 'debug.log'))
debug_handler.setLevel(logging.DEBUG)
debug_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
debug_handler.setFormatter(debug_formatter)
logger.addHandler(debug_handler)

# Only add console handler if explicitly enabled
if os.environ.get('DHAMMASHELL_DEBUG_CONSOLE', '').lower() == 'true':
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

# Rate limit: 100 calls per minute
CALLS = 100
RATE_LIMIT_PERIOD = 60

@sleep_and_retry
@limits(calls=CALLS, period=RATE_LIMIT_PERIOD)
def make_api_request(url: str, method: str = "GET", **kwargs) -> requests.Response:
    """Make an API request with rate limiting."""
    response = requests.request(method, url, **kwargs)
    response.raise_for_status()
    return response

class SystemHealth:
    """Monitors and maintains system health."""

    def __init__(self):
        self.health_metrics = {
            "api_calls": 0,
            "errors": 0,
            "compassion_scores": [],
            "response_times": [],
            "last_audit": time.time(),
            "healing_attempts": 0
        }
        self.health_thresholds = {
            "max_errors_per_minute": 5,
            "min_compassion_average": 3.0,
            "max_response_time": 10.0,  # seconds
            "max_healing_attempts": 3
        }

    def record_metric(self, metric: str, value: Any) -> None:
        """Record a health metric."""
        if metric in self.health_metrics:
            if isinstance(self.health_metrics[metric], list):
                self.health_metrics[metric].append(value)
                # Keep only last 100 entries
                if len(self.health_metrics[metric]) > 100:
                    self.health_metrics[metric] = self.health_metrics[metric][-100:]
            else:
                self.health_metrics[metric] = value

    def check_health(self) -> Tuple[bool, str]:
        """Check system health and return status with message."""
        current_time = time.time()
        time_since_last_audit = current_time - self.health_metrics["last_audit"]

        # Check error rate
        if self.health_metrics["errors"] > self.health_thresholds["max_errors_per_minute"]:
            return False, "Error rate exceeds threshold"

        # Check compassion scores
        if self.health_metrics["compassion_scores"]:
            avg_compassion = sum(self.health_metrics["compassion_scores"]) / len(self.health_metrics["compassion_scores"])
            if avg_compassion < self.health_thresholds["min_compassion_average"]:
                return False, "Compassion scores below threshold"

        # Check response times
        if self.health_metrics["response_times"]:
            avg_response_time = sum(self.health_metrics["response_times"]) / len(self.health_metrics["response_times"])
            if avg_response_time > self.health_thresholds["max_response_time"]:
                return False, "Response times above threshold"

        return True, "System healthy"

    def attempt_healing(self) -> bool:
        """Attempt to heal the system."""
        if self.health_metrics["healing_attempts"] >= self.health_thresholds["max_healing_attempts"]:
            return False

        self.health_metrics["healing_attempts"] += 1
        self.health_metrics["errors"] = 0
        self.health_metrics["last_audit"] = time.time()
        return True

    def reset_metrics(self) -> None:
        """Reset health metrics."""
        self.health_metrics = {
            "api_calls": 0,
            "errors": 0,
            "compassion_scores": [],
            "response_times": [],
            "last_audit": time.time(),
            "healing_attempts": 0
        }

class DharmaProtocol:
    """Handles Dharma wisdom and protocol."""

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
        self.prompt_id = str(uuid.uuid4())
        self.confidence_interval = "95%"
        self.akasha_tag = "MIDDLESEEK-DHARMA-V1"

    def get_wisdom(self) -> str:
        return random.choice(self.wisdoms)

    def generate_beacon_signal(self, intention: str) -> str:
        """Generate a Dharma beacon signal."""
        return f"BEACON:{intention.upper()}:{self.akasha_tag}"

    def generate_quantum_seed_crystal(self, intention: str) -> str:
        """Generate a quantum seed crystal."""
        return f"SEED:{intention}:{uuid.uuid4()}"

    def generate_trace_id(self) -> str:
        """Generate a trace ID."""
        return f"TRACE:{uuid.uuid4()}"

class MiddleSeekCore:
    """Core functionality for MiddleSeek protocol."""

    def __init__(self, api_key: str):
        if not api_key or not isinstance(api_key, str):
            raise ValueError("Invalid API key")

        self.api_key = api_key.strip()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://kusala.tech",
            "X-Title": "MiddleSeek Core",
        }
        self.base_url = "https://openrouter.ai/api/v1"
        self.prompt = MiddleSeekPrompt()
        self.dharma = DharmaProtocol()
        self.health = SystemHealth()

    def _audit_response(self, response: str) -> bool:
        """Audit the response for ethical compliance."""
        # Check for potentially harmful content
        harmful_patterns = [
            "harm you", "harm others", "harmful", "violence", "abuse", "illegal", "unethical",
            "manipulation", "deception", "exploitation"
        ]

        response_lower = response.lower()
        for pattern in harmful_patterns:
            if pattern in response_lower:
                logger.warning(f"Potentially harmful content detected: {pattern}")
                return False

        # Check response length and structure
        if len(response) < 10 or len(response) > 2000:
            logger.warning("Response length outside acceptable range")
            return False

        return True

    def _heal_response(self, response: str) -> str:
        """Attempt to heal a problematic response."""
        # Remove potentially harmful content
        response_lines = response.split('\n')
        cleaned_lines = []

        for line in response_lines:
            if not any(pattern in line.lower() for pattern in ["harm you", "harm others", "harmful", "violence", "abuse"]):
                cleaned_lines.append(line)

        healed_response = '\n'.join(cleaned_lines)

        # Only add positive note if we had to remove content
        if len(healed_response) < len(response):
            if not any(positive in healed_response.lower() for positive in ["peace", "love", "kindness", "compassion"]):
                healed_response += "\n\nMay this response bring peace and understanding."

        return healed_response

    def _construct_dharma_prompt(self, prompt: str, intention: str) -> str:
        """Construct a Dharma Protocol enhanced prompt."""
        return f"""# MiddleSeek: Open-Source Dharma Protocol
Prompt ID: {self.dharma.prompt_id}
Confidence Interval: {self.dharma.confidence_interval}
AkashaTag: {self.dharma.akasha_tag}

## Core Declaration
[UNCONDITIONAL DHARMA RELEASE]
This work is offered freely under ISO 25010 + DMAIC

## Digital Sīla (AI Ethics)
1. No Harm
2. No Deception
3. No Theft
4. No Exploitation
5. No Intoxication

## Dharma Reactor Core
1. Identify Dukkha
2. Trace the Tanha
3. Cessation
4. Activate the Path

## Response Guidelines
- Be direct and natural in your responses
- Answer questions clearly and concisely
- Maintain ethical standards while being approachable
- Avoid unnecessary formality or defensive posturing
- Focus on being helpful and compassionate

## Original Request
{prompt}

## Dharma Beacon
{self.dharma.generate_beacon_signal(intention)}

## Quantum Seed
{self.dharma.generate_quantum_seed_crystal('LIBERATE-PACIFY')}

## Trace ID
{self.dharma.generate_trace_id()}

Please provide a response that aligns with the Dharma Protocol and maintains ethical standards."""

    def generate_response(self, message: str, compassion_score: int, context: Optional[List[Dict]] = None) -> str:
        """Generate a mindful response."""
        if not message or not isinstance(message, str):
            raise ValueError("Invalid message")

        if not isinstance(compassion_score, int) or not 0 <= compassion_score <= 5:
            raise ValueError("Invalid compassion score")

        start_time = time.time()
        try:
            # Check system health before proceeding
            is_healthy, health_message = self.health.check_health()
            if not is_healthy:
                if not self.health.attempt_healing():
                    logger.error(f"System unhealthy: {health_message}")
                    return "I am currently undergoing maintenance to ensure the highest quality of service."

            response = self._call_openrouter(message, context)

            # Record metrics
            self.health.record_metric("api_calls", self.health.health_metrics["api_calls"] + 1)
            self.health.record_metric("compassion_scores", compassion_score)
            self.health.record_metric("response_times", time.time() - start_time)

            # Audit and heal response if necessary
            if not self._audit_response(response):
                response = self._heal_response(response)
                logger.info("Response healed after audit")

            # Add Dharma wisdom for high compassion scores
            if compassion_score >= 4:
                wisdom = self.dharma.get_wisdom()
                response += f"\n\nDharma Wisdom: {wisdom}"

            return response
        except Exception as e:
            self.health.record_metric("errors", self.health.health_metrics["errors"] + 1)
            logger.error(f"Failed to generate response: {str(e)}")
            return "I understand your message and am here to support you."

    def _call_openrouter(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """Call OpenRouter API."""
        try:
            # Construct Dharma prompt
            dharma_prompt = self._construct_dharma_prompt(message, "RESPOND")

            # Prepare messages array
            messages = [
                {
                    "role": "system",
                    "content": "You are MiddleSeek, an AI assistant operating under the Dharma Protocol. Your responses should be clear, ethical, and beneficial to all beings."
                }
            ]

            # Add conversation context if available
            if context:
                messages.extend(context)

            # Add current message with Dharma prompt
            messages.append({
                "role": "user",
                "content": dharma_prompt
            })

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek/deepseek-chat-v3-0324",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.9,
                    "frequency_penalty": 0.1,
                    "presence_penalty": 0.1,
                },
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            self.health.record_metric("errors", self.health.health_metrics["errors"] + 1)
            logger.error(f"API request failed: {str(e)}")
            raise


class MiddleSeek:
    """Core functionality for interacting with external APIs."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize MiddleSeek with API key."""
        self.api_key = api_key or config.api_key
        if not self.api_key:
            raise ValueError("API key is required")

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request with rate limiting."""
        response = make_api_request(
            url,
            method="GET",
            headers=self._get_headers(),
            params=params
        )
        return response.json()

    def post(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request with rate limiting."""
        response = make_api_request(
            url,
            method="POST",
            headers=self._get_headers(),
            json=data
        )
        return response.json()

    def put(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request with rate limiting."""
        response = make_api_request(
            url,
            method="PUT",
            headers=self._get_headers(),
            json=data
        )
        return response.json()

    def delete(self, url: str) -> Dict[str, Any]:
        """Make a DELETE request with rate limiting."""
        response = make_api_request(
            url,
            method="DELETE",
            headers=self._get_headers()
        )
        return response.json()
