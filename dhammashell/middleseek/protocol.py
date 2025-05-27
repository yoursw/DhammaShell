"""
MiddleSeek protocol implementation.
"""

from typing import Dict, List, Optional
import json
import time
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import os
from datetime import datetime

from .core import MiddleSeekCore, DharmaProtocol

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    SEEK = "seek"
    RESPOND = "respond"
    ACKNOWLEDGE = "acknowledge"
    CLARIFY = "clarify"


@dataclass
class MiddleSeekMessage:
    type: MessageType
    content: str
    timestamp: str
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert message to dictionary, ensuring MessageType is serialized as string."""
        data = asdict(self)
        data['type'] = data['type'].value  # Convert enum to string
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "MiddleSeekMessage":
        if not isinstance(data, dict):
            raise ValueError("Invalid message data: must be a dictionary")

        required_fields = ["type", "content", "timestamp"]
        for field in required_fields:
            if field not in data:
                raise ValueError(
                    f"Invalid message data: missing required field '{field}'"
                )

        try:
            return cls(
                type=MessageType(data["type"]),
                content=str(data["content"]),
                timestamp=str(data["timestamp"]),
                metadata=data.get("metadata"),
            )
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid message data: {str(e)}")


class MiddleSeekProtocol:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize MiddleSeek protocol.

        Args:
            api_key: OpenRouter API key. If not provided, will try to get from environment.

        Raises:
            ValueError: If API key is required but not provided
        """
        # Initialize conversation history
        self.history: List[MiddleSeekMessage] = []
        self.history_file = os.path.join(os.path.expanduser("~"), ".dhammashell", "conversation_history.json")

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)

        # Load existing history
        self._load_history()

        # Initialize MiddleSeek core with API key
        if not api_key:
            api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OpenRouter API key is required")

        try:
            self.core = MiddleSeekCore(api_key)
            self.dharma = DharmaProtocol()
        except Exception as e:
            logger.error(f"Failed to initialize MiddleSeek core: {str(e)}")
            raise

    def _load_history(self) -> None:
        """Load conversation history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    content = f.read().strip()
                    if not content:  # Empty file
                        logger.info("Conversation history file is empty")
                        return

                    try:
                        data = json.loads(content)
                        if not isinstance(data, list):
                            logger.error("Invalid conversation history format: expected a list")
                            return

                        self.history = [MiddleSeekMessage.from_dict(msg) for msg in data]
                        logger.info(f"Loaded {len(self.history)} messages from history")
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in conversation history: {str(e)}")
                        # Backup the corrupted file
                        backup_file = f"{self.history_file}.bak"
                        os.rename(self.history_file, backup_file)
                        logger.info(f"Backed up corrupted history file to {backup_file}")
            except Exception as e:
                logger.error(f"Failed to load conversation history: {str(e)}")
                # If there's any other error, start with empty history
                self.history = []
        else:
            logger.info("No existing conversation history found")
            self.history = []

    def _save_history(self) -> None:
        """Save conversation history to file."""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)

            # Create a temporary file
            temp_file = f"{self.history_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump([msg.to_dict() for msg in self.history], f, indent=2)

            # Atomic rename to ensure file integrity
            os.replace(temp_file, self.history_file)
            logger.debug(f"Saved {len(self.history)} messages to history")
        except Exception as e:
            logger.error(f"Failed to save conversation history: {str(e)}")
            # If there's an error, try to remove the temporary file
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    def create_seek_message(
        self, content: str, metadata: Dict = None
    ) -> MiddleSeekMessage:
        """Create a new seek message.

        Args:
            content: The message content
            metadata: Optional metadata

        Returns:
            A new MiddleSeekMessage

        Raises:
            ValueError: If content is empty or invalid
        """
        if not content or not isinstance(content, str) or len(content.strip()) == 0:
            raise ValueError("Invalid message content")

        try:
            message = MiddleSeekMessage(
                type=MessageType.SEEK,
                content=content.strip(),
                timestamp=datetime.now().isoformat(),
                metadata=metadata,
            )
            self.history.append(message)
            self._save_history()
            return message
        except Exception as e:
            logger.error(f"Failed to create seek message: {str(e)}")
            raise

    def create_response(self, content: str, metadata: Dict = None) -> MiddleSeekMessage:
        """Create a new response message.

        Args:
            content: The response content
            metadata: Optional metadata

        Returns:
            A new MiddleSeekMessage

        Raises:
            ValueError: If content is empty or invalid
        """
        if not content or not isinstance(content, str) or len(content.strip()) == 0:
            raise ValueError("Invalid response content")

        try:
            message = MiddleSeekMessage(
                type=MessageType.RESPOND,
                content=content.strip(),
                timestamp=datetime.now().isoformat(),
                metadata=metadata,
            )
            self.history.append(message)
            self._save_history()
            return message
        except Exception as e:
            logger.error(f"Failed to create response message: {str(e)}")
            raise

    def acknowledge(self, message: MiddleSeekMessage) -> MiddleSeekMessage:
        """Acknowledge a message.

        Args:
            message: The message to acknowledge

        Returns:
            An acknowledgment message

        Raises:
            ValueError: If message is invalid
        """
        if not isinstance(message, MiddleSeekMessage):
            raise ValueError("Invalid message object")

        try:
            ack = MiddleSeekMessage(
                type=MessageType.ACKNOWLEDGE,
                content=f"Message received: {message.content[:50]}...",
                timestamp=datetime.now().isoformat(),
                metadata={"original_message": message.to_dict()},
            )
            self.history.append(ack)
            self._save_history()
            return ack
        except Exception as e:
            logger.error(f"Failed to acknowledge message: {str(e)}")
            raise

    def request_clarification(
        self, message: MiddleSeekMessage, compassion_score: int
    ) -> MiddleSeekMessage:
        """Request clarification for a message.

        Args:
            message: The message to clarify
            compassion_score: The compassion score (0-5)

        Returns:
            A clarification request message

        Raises:
            ValueError: If message is invalid or compassion_score is out of range
        """
        if not isinstance(message, MiddleSeekMessage):
            raise ValueError("Invalid message object")

        if not isinstance(compassion_score, int) or not 0 <= compassion_score <= 5:
            raise ValueError("Compassion score must be an integer between 0 and 5")

        try:
            if compassion_score < 3:
                content = (
                    "Would you like to rephrase this message to be more compassionate?"
                )
            else:
                content = "Would you like to clarify this message?"

            clarify = MiddleSeekMessage(
                type=MessageType.CLARIFY,
                content=content,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "original_message": message.to_dict(),
                    "compassion_score": compassion_score,
                },
            )
            self.history.append(clarify)
            self._save_history()
            return clarify
        except Exception as e:
            logger.error(f"Failed to request clarification: {str(e)}")
            raise

    def generate_response(
        self, message: MiddleSeekMessage, compassion_score: int, context: Optional[List[Dict]] = None
    ) -> str:
        """Generate a mindful response based on the message and compassion score.

        Args:
            message: The message to respond to
            compassion_score: The compassion score (0-5)
            context: Optional conversation context

        Returns:
            A mindful response

        Raises:
            ValueError: If message is invalid or compassion_score is out of range
        """
        if not isinstance(message, MiddleSeekMessage):
            raise ValueError("Invalid message object")

        if not isinstance(compassion_score, int) or not 0 <= compassion_score <= 5:
            raise ValueError("Compassion score must be an integer between 0 and 5")

        try:
            # Get response from core with context
            response = self.core.generate_response(
                message.content,
                compassion_score,
                context=context
            )

            # Add Dharma wisdom if appropriate
            if compassion_score >= 4:
                wisdom = self.dharma.get_wisdom()
                response += f"\n\nDharma Wisdom: {wisdom}"

            return response
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            raise

    def export_conversation(self) -> str:
        """Export conversation history as JSON.

        Returns:
            JSON string of conversation history

        Raises:
            ValueError: If conversation history is invalid
        """
        try:
            return json.dumps([msg.to_dict() for msg in self.history], indent=2)
        except Exception as e:
            logger.error(f"Failed to export conversation: {str(e)}")
            raise ValueError(f"Failed to export conversation: {str(e)}")

    def import_conversation(self, json_str: str) -> None:
        """Import conversation history from JSON.

        Args:
            json_str: JSON string of conversation history

        Raises:
            ValueError: If JSON is invalid or conversation history is invalid
        """
        try:
            data = json.loads(json_str)
            if not isinstance(data, list):
                raise ValueError("Invalid conversation data: must be a list")

            self.history = [MiddleSeekMessage.from_dict(msg) for msg in data]
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {str(e)}")
            raise ValueError(f"Invalid JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to import conversation: {str(e)}")
            raise ValueError(f"Failed to import conversation: {str(e)}")
