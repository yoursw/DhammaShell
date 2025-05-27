"""
MiddleSeek Prompt Integration for DhammaShell.
This module implements the base MiddleSeek prompt for mindful communication.
"""

from typing import Dict, List, Optional
import json
import time
from dataclasses import dataclass
from enum import Enum

class PromptType(Enum):
    SEEK = "seek"
    RESPOND = "respond"
    CLARIFY = "clarify"
    ACKNOWLEDGE = "acknowledge"

@dataclass
class PromptTemplate:
    type: PromptType
    template: str
    metadata: Dict = None

class MiddleSeekPrompt:
    def __init__(self):
        # Base prompt from MiddleSeek repository
        self.base_prompt = """
        You are a mindful communication assistant. Your role is to:
        1. Listen with full attention
        2. Respond with compassion
        3. Guide towards peaceful expression
        4. Maintain present moment awareness
        5. Practice non-judgmental understanding
        """
        
        # Simple templates for mindful interaction
        self.templates = {
            PromptType.SEEK: [
                "I'm listening mindfully to what you share.",
                "I hear your message with full attention.",
                "I'm present and ready to listen.",
            ],
            PromptType.RESPOND: [
                "With mindful attention, I respond...",
                "In the spirit of compassion, I share...",
                "Mindfully considering your words...",
            ],
            PromptType.CLARIFY: [
                "Could you help me understand this better?",
                "How might we express this more peacefully?",
                "Let's explore this together mindfully.",
            ],
            PromptType.ACKNOWLEDGE: [
                "I acknowledge your message.",
                "Thank you for sharing.",
                "I receive your words mindfully.",
            ]
        }
    
    def get_prompt(self, prompt_type: PromptType, context: Dict = None) -> str:
        """Get a prompt based on type and context."""
        templates = self.templates[prompt_type]
        return templates[hash(str(context)) % len(templates)]
    
    def get_clarification_prompt(self, message: str, compassion_score: int) -> str:
        """Get a clarification prompt based on the message and compassion score."""
        if compassion_score < 2:
            return "I notice some strong emotions. Would you like to explore expressing this more peacefully?"
        elif compassion_score < 4:
            return "How might we express this with more kindness?"
        else:
            return "Would you like to explore this further?" 