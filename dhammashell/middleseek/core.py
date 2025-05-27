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
from dataclasses import dataclass
from datetime import datetime
from ratelimit import limits, sleep_and_retry
from ..config import config
from ..prompt import MiddleSeekPrompt, PromptType

# Configure root logger to prevent propagation to stdout
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger().handlers = []

# Configure module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False  # Prevent propagation to root logger

# Configure logging directory
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
logger.info(f"Log directory: {log_dir}")

# File handler for debug.log
debug_handler = logging.FileHandler(os.path.join(log_dir, 'debug.log'))
debug_handler.setLevel(logging.DEBUG)
debug_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
debug_handler.setFormatter(debug_formatter)
logger.addHandler(debug_handler)

# File handler for self-healing.log
healing_logger = logging.getLogger(f"{__name__}.healing")
healing_logger.setLevel(logging.INFO)
healing_logger.propagate = False
healing_handler = logging.FileHandler(os.path.join(log_dir, 'self_healing.log'))
healing_handler.setLevel(logging.INFO)
healing_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
healing_handler.setFormatter(healing_formatter)
healing_logger.addHandler(healing_handler)

# Only add console handler if explicitly enabled
if os.environ.get('DHAMMASHELL_DEBUG_CONSOLE', '').lower() == 'true':
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    healing_logger.addHandler(console_handler)

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
            "healing_attempts": 0
        }
        self.health_thresholds = {
            "max_errors_per_minute": 10,
            "min_compassion_average": 2.5,
            "max_response_time": 30.0,
            "max_healing_attempts": 3,
            "response_time_window": 10
        }
        self.healing_logger = logging.getLogger(f"{__name__}.healing")

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
        # Check error rate
        if self.health_metrics["errors"] > self.health_thresholds["max_errors_per_minute"]:
            self.healing_logger.warning(f"Error rate {self.health_metrics['errors']} exceeds threshold {self.health_thresholds['max_errors_per_minute']}")
            return False, "Error rate exceeds threshold"

        # Check compassion scores
        if self.health_metrics["compassion_scores"]:
            avg_compassion = sum(self.health_metrics["compassion_scores"]) / len(self.health_metrics["compassion_scores"])
            if avg_compassion < self.health_thresholds["min_compassion_average"]:
                self.healing_logger.warning(f"Average compassion score {avg_compassion:.2f} below threshold {self.health_thresholds['min_compassion_average']}")
                return False, "Compassion scores below threshold"

        # Check response times using a rolling window
        if self.health_metrics["response_times"]:
            recent_times = self.health_metrics["response_times"][-self.health_thresholds["response_time_window"]:]
            avg_response_time = sum(recent_times) / len(recent_times)
            if avg_response_time > self.health_thresholds["max_response_time"]:
                self.healing_logger.warning(f"Average response time {avg_response_time:.2f}s exceeds threshold {self.health_thresholds['max_response_time']}s")
                return False, "Response times above threshold"

        return True, "System healthy"

    def attempt_healing(self) -> bool:
        """Attempt to heal the system."""
        if self.health_metrics["healing_attempts"] >= self.health_thresholds["max_healing_attempts"]:
            self.healing_logger.error(f"Maximum healing attempts ({self.health_thresholds['max_healing_attempts']}) reached")
            return False

        self.health_metrics["healing_attempts"] += 1
        self.health_metrics["errors"] = 0
        self.healing_logger.info(f"Healing attempt {self.health_metrics['healing_attempts']} initiated")
        return True

    def reset_metrics(self) -> None:
        """Reset health metrics."""
        self.health_metrics = {
            "api_calls": 0,
            "errors": 0,
            "compassion_scores": [],
            "response_times": [],
            "healing_attempts": 0
        }
        self.healing_logger.info("Health metrics reset")

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

@dataclass
class ChatHistoryEntry:
    """Represents a single chat history entry with healing information."""
    timestamp: datetime
    message: str
    original_response: str
    healed_response: Optional[str]
    healing_reason: Optional[str]
    compassion_score: int
    context: Optional[List[Dict]]

class ChatHistory:
    """Manages chat history."""

    def __init__(self, max_entries: int = 1000):
        self.history: List[ChatHistoryEntry] = []
        self.max_entries = max_entries
        self.history_file = os.path.join(log_dir, 'chat_history.json')
        logger.info(f"Chat history file: {self.history_file}")
        self._load_history()

    def _load_history(self) -> None:
        """Load chat history from file if it exists."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.history = [
                        ChatHistoryEntry(
                            timestamp=datetime.fromisoformat(entry['timestamp']),
                            message=entry['message'],
                            original_response=entry['original_response'],
                            healed_response=entry.get('healed_response'),
                            healing_reason=entry.get('healing_reason'),
                            compassion_score=entry['compassion_score'],
                            context=entry.get('context')
                        )
                        for entry in data
                    ]
                logger.info(f"Loaded {len(self.history)} chat history entries")
            except Exception as e:
                logger.error(f"Failed to load chat history: {e}")
        else:
            logger.info("No existing chat history found, starting fresh")

    def _save_history(self) -> None:
        """Save chat history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump([
                    {
                        'timestamp': entry.timestamp.isoformat(),
                        'message': entry.message,
                        'original_response': entry.original_response,
                        'healed_response': entry.healed_response,
                        'healing_reason': entry.healing_reason,
                        'compassion_score': entry.compassion_score,
                        'context': entry.context
                    }
                    for entry in self.history
                ], f, indent=2)
            logger.debug(f"Saved {len(self.history)} chat history entries to {self.history_file}")
        except Exception as e:
            logger.error(f"Failed to save chat history: {e}")

    def add_entry(self, entry: ChatHistoryEntry) -> None:
        """Add a new entry to the chat history."""
        self.history.append(entry)
        if len(self.history) > self.max_entries:
            self.history = self.history[-self.max_entries:]
            logger.debug(f"Trimmed chat history to {self.max_entries} entries")
        self._save_history()
        if entry.healed_response:
            logger.info(f"Added healed response to chat history: {self.history_file}")
        else:
            logger.debug(f"Added response to chat history: {self.history_file}")

    def get_recent_entries(self, count: int = 10) -> List[ChatHistoryEntry]:
        """Get the most recent chat history entries."""
        return self.history[-count:]

    def get_healed_entries(self) -> List[ChatHistoryEntry]:
        """Get all entries that required healing."""
        return [entry for entry in self.history if entry.healed_response is not None]

class MiddleSeekCore:
    """Core functionality for MiddleSeek protocol."""

    def __init__(self, openrouter_api_key: str):
        if not openrouter_api_key or openrouter_api_key == "invalid-key":
            raise ValueError("Invalid OpenRouter API key")
        self._api_key = openrouter_api_key
        self.dharma = DharmaProtocol()
        self.headers = {
            "Authorization": f"Bearer {openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://kusala.tech",
            "X-Title": "MiddleSeek Core"
        }
        self.base_url = "https://openrouter.ai/api/v1"
        self.prompt = MiddleSeekPrompt()
        self.health = SystemHealth()
        self.chat_history = ChatHistory()
        self.healing_logger = logging.getLogger(f"{__name__}.healing")

    def _get_api_key(self) -> str:
        """Get the OpenRouter API key.

        Returns:
            str: The API key
        """
        return self._api_key

    def _heal_response(self, response: str, reason: str) -> str:
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

        self.healing_logger.info(f"Response healed: {reason}")
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

            # Record in chat history
            self.chat_history.add_entry(ChatHistoryEntry(
                timestamp=datetime.now(),
                message=message,
                original_response=response,
                healed_response=None,
                healing_reason=None,
                compassion_score=compassion_score,
                context=context
            ))

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
