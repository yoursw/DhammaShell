"""
Empathy Analysis Component for DhammaShell
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from textblob import TextBlob

class EmpathyAnalyzer:
    def __init__(self):
        self.metrics = {}
        self.interaction_history = []
        
    def analyze_interaction(self, 
                          user_input: str, 
                          system_response: str, 
                          context: Optional[Dict] = None) -> Dict:
        """
        Analyze a single interaction for empathy metrics
        
        Args:
            user_input: The user's input text
            system_response: The system's response text
            context: Optional context information
            
        Returns:
            Dict containing empathy metrics and analysis
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "system_response": system_response,
            "metrics": {
                "emotional_recognition": self._analyze_emotional_recognition(user_input),
                "compassion_score": self._calculate_compassion_score(system_response),
                "mindfulness_level": self._assess_mindfulness(system_response)
            }
        }
        
        self.interaction_history.append(analysis)
        return analysis
    
    def _analyze_emotional_recognition(self, text: str) -> float:
        """
        Analyze the emotional content of the input text using TextBlob sentiment analysis
        """
        blob = TextBlob(text)
        # Get sentiment polarity (-1.0 to 1.0)
        sentiment = blob.sentiment.polarity
        
        # Convert to 0-1 scale and ensure positive values for both positive and negative emotions
        emotional_intensity = abs(sentiment)
        
        # Add bonus for emotional keywords with increased weight
        emotional_keywords = [
            'happy', 'sad', 'angry', 'anxious', 'grateful', 'overwhelmed',
            'upset', 'worried', 'frustrated', 'excited', 'joy', 'pain',
            'hurt', 'scared', 'afraid', 'terrified', 'depressed'
        ]
        keyword_bonus = sum(1 for word in emotional_keywords if word.lower() in text.lower()) * 0.15
        
        # Add bonus for emotional phrases
        emotional_phrases = [
            'i feel', 'i am', 'makes me', "i'm feeling", 'i feel like',
            'i am feeling', 'i feel so', 'i feel very'
        ]
        phrase_bonus = sum(1 for phrase in emotional_phrases if phrase.lower() in text.lower()) * 0.2
        
        # Cap the final score at 1.0
        return min(emotional_intensity + keyword_bonus + phrase_bonus, 1.0)
    
    def _calculate_compassion_score(self, response: str) -> float:
        """
        Calculate compassion score based on response content
        """
        # Keywords indicating compassion with increased weight
        compassion_keywords = [
            'understand', 'feel', 'hear', 'support', 'help',
            'care', 'concern', 'empathy', 'compassion', 'kindness',
            'sorry', 'apologize', 'wish', 'hope', 'pray',
            'comfort', 'console', 'assist', 'guide', 'nurture',
            'pain', 'alone', 'journey', 'together', 'share'
        ]
        
        # Phrases indicating compassion with increased weight
        compassion_phrases = [
            'i understand', 'i hear you', 'i feel', 'let me help',
            'i care', 'i support', 'i empathize', "i'm here",
            'i understand how', 'i can see', 'i recognize',
            'i appreciate', 'i acknowledge', 'i validate',
            "i'm here to help", 'i want to support',
            'you are not alone', 'i hear your pain',
            'i understand your pain', 'i feel your pain',
            'we are in this together', 'i am here for you',
            'i want you to know', 'i want to help you'
        ]
        
        # Calculate base score from keywords with increased weight
        keyword_score = sum(1 for word in compassion_keywords 
                          if word.lower() in response.lower()) * 0.2
        
        # Add bonus for phrases with increased weight
        phrase_score = sum(1 for phrase in compassion_phrases 
                         if phrase.lower() in response.lower()) * 0.3
        
        # Add bonus for longer, more detailed compassionate responses
        length_bonus = min(len(response.split()) * 0.015, 0.25)
        
        # Add bonus for responses that acknowledge pain or loneliness
        pain_bonus = 0.2 if any(word in response.lower() for word in ['pain', 'alone', 'lonely', 'hurt']) else 0
        
        # Cap the final score at 1.0
        return min(keyword_score + phrase_score + length_bonus + pain_bonus, 1.0)
    
    def _assess_mindfulness(self, text: str) -> float:
        """
        Assess the mindfulness level in the response
        """
        # Keywords indicating mindfulness with increased weight
        mindfulness_keywords = [
            'breathe', 'present', 'moment', 'aware', 'observe',
            'notice', 'focus', 'calm', 'peace', 'mindful',
            'meditate', 'centered', 'grounded', 'still', 'quiet',
            'accept', 'let go', 'release', 'flow', 'balance'
        ]
        
        # Phrases indicating mindfulness with increased weight
        mindfulness_phrases = [
            'take a moment', "let's breathe", 'be present',
            'notice how', 'observe your', 'focus on',
            'in this moment', 'right now', 'pay attention',
            'be aware of', 'stay present', 'mindful of',
            'take a breath', 'center yourself', 'ground yourself'
        ]
        
        # Calculate base score from keywords with increased weight
        keyword_score = sum(1 for word in mindfulness_keywords 
                          if word.lower() in text.lower()) * 0.15
        
        # Add bonus for phrases with increased weight
        phrase_score = sum(1 for phrase in mindfulness_phrases 
                         if phrase.lower() in text.lower()) * 0.25
        
        # Add bonus for longer, more detailed mindful responses
        length_bonus = min(len(text.split()) * 0.01, 0.2)
        
        # Cap the final score at 1.0
        return min(keyword_score + phrase_score + length_bonus, 1.0)
    
    def get_research_data(self) -> Dict:
        """
        Get formatted research data for analysis
        """
        return {
            "interaction_history": self.interaction_history,
            "aggregate_metrics": self._calculate_aggregate_metrics()
        }
    
    def _calculate_aggregate_metrics(self) -> Dict:
        """
        Calculate aggregate metrics from interaction history
        """
        if not self.interaction_history:
            return {
                "total_interactions": 0,
                "average_compassion": 0.0,
                "average_mindfulness": 0.0
            }
            
        total_interactions = len(self.interaction_history)
        total_compassion = sum(interaction["metrics"]["compassion_score"] 
                             for interaction in self.interaction_history)
        total_mindfulness = sum(interaction["metrics"]["mindfulness_level"] 
                              for interaction in self.interaction_history)
        
        return {
            "total_interactions": total_interactions,
            "average_compassion": total_compassion / total_interactions,
            "average_mindfulness": total_mindfulness / total_interactions
        } 