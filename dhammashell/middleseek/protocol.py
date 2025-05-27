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
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MiddleSeekMessage':
        if not isinstance(data, dict):
            raise ValueError("Invalid message data: must be a dictionary")
            
        required_fields = ['type', 'content', 'timestamp']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Invalid message data: missing required field '{field}'")
                
        try:
            return cls(
                type=MessageType(data['type']),
                content=str(data['content']),
                timestamp=str(data['timestamp']),
                metadata=data.get('metadata')
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
    
    def create_seek_message(self, content: str, metadata: Dict = None) -> MiddleSeekMessage:
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
                metadata=metadata
            )
            self.history.append(message)
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
                metadata=metadata
            )
            self.history.append(message)
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
                metadata={"original_message": message.to_dict()}
            )
            self.history.append(ack)
            return ack
        except Exception as e:
            logger.error(f"Failed to acknowledge message: {str(e)}")
            raise
    
    def request_clarification(self, message: MiddleSeekMessage, compassion_score: int) -> MiddleSeekMessage:
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
                content = "Would you like to rephrase this message to be more compassionate?"
            else:
                content = "Would you like to clarify this message?"
                
            clarify = MiddleSeekMessage(
                type=MessageType.CLARIFY,
                content=content,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "original_message": message.to_dict(),
                    "compassion_score": compassion_score
                }
            )
            self.history.append(clarify)
            return clarify
        except Exception as e:
            logger.error(f"Failed to request clarification: {str(e)}")
            raise
    
    def generate_response(self, message: MiddleSeekMessage, compassion_score: int) -> str:
        """Generate a mindful response based on the message and compassion score.
        
        Args:
            message: The message to respond to
            compassion_score: The compassion score (0-5)
            
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
            # Get response from core
            response = self.core.generate_response(message.content, compassion_score)
            
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