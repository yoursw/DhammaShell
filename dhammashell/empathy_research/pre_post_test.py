"""
Pre/Post Test Module for DhammaShell Empathy Research
Handles assessment of user empathy levels before and after interaction
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path


class TestType(Enum):
    """Type of empathy assessment test"""
    PRE = "pre"
    POST = "post"


class EmpathyTest:
    """Manages pre and post empathy assessment tests"""

    # Core empathy assessment questions
    CORE_QUESTIONS = [
        {
            "id": "empathy_1",
            "question": "How well do you understand others' emotions?",
            "scale": "1-5",
            "description": "1 = Not at all, 5 = Very well"
        },
        {
            "id": "empathy_2",
            "question": "How often do you feel moved by others' experiences?",
            "scale": "1-5",
            "description": "1 = Rarely, 5 = Very often"
        },
        {
            "id": "empathy_3",
            "question": "How comfortable are you discussing emotional topics?",
            "scale": "1-5",
            "description": "1 = Very uncomfortable, 5 = Very comfortable"
        }
    ]

    # Extended questions for deeper assessment
    EXTENDED_QUESTIONS = [
        {
            "id": "empathy_4",
            "question": "Can you describe a time when you felt deeply connected to someone else's emotional experience?",
            "type": "open_ended",
            "follow_up_prompt": "Tell me more about how this experience affected your understanding of empathy."
        },
        {
            "id": "empathy_5",
            "question": "How do you typically respond when someone shares their emotional struggles with you?",
            "type": "open_ended",
            "follow_up_prompt": "What do you think makes your response effective or ineffective in these situations?"
        },
        {
            "id": "empathy_6",
            "question": "What does empathy mean to you in your daily life?",
            "type": "open_ended",
            "follow_up_prompt": "How has your understanding of empathy evolved over time?"
        }
    ]

    def __init__(self, data_dir: str = "research_data"):
        """
        Initialize the empathy test system

        Args:
            data_dir: Directory to store test results
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.current_test = None

    def start_test(self, test_type: TestType, user_id: Optional[str] = None) -> Dict:
        """
        Start a new empathy assessment test

        Args:
            test_type: Type of test (pre or post)
            user_id: Optional user identifier

        Returns:
            Test configuration including questions
        """
        test_id = f"{test_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.current_test = {
            "test_id": test_id,
            "user_id": user_id,
            "test_type": test_type.value,
            "start_time": datetime.now().isoformat(),
            "questions": self.CORE_QUESTIONS.copy() + self.EXTENDED_QUESTIONS.copy(),
            "responses": [],
            "follow_ups": [],
            "llm_available": False  # Will be updated when LLM status is known
        }

        return {
            "test_id": test_id,
            "questions": self.current_test["questions"]
        }

    def record_response(self, question_id: str, response: str) -> None:
        """
        Record a response to a test question

        Args:
            question_id: ID of the question being answered
            response: User's response
        """
        if not self.current_test:
            raise ValueError("No active test. Call start_test() first.")

        self.current_test["responses"].append({
            "question_id": question_id,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })

    def record_follow_up(self, question_id: str, follow_up: str, response: str) -> None:
        """
        Record a follow-up question and response

        Args:
            question_id: ID of the original question
            follow_up: The follow-up question asked
            response: User's response to the follow-up
        """
        if not self.current_test:
            raise ValueError("No active test. Call start_test() first.")

        self.current_test["follow_ups"].append({
            "question_id": question_id,
            "follow_up": follow_up,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })

    def save_test(self) -> Path:
        """
        Save the completed test results

        Returns:
            Path to the saved test file
        """
        if not self.current_test:
            raise ValueError("No active test to save.")

        test_file = self.data_dir / f"{self.current_test['test_id']}.json"

        with open(test_file, 'w') as f:
            json.dump(self.current_test, f, indent=2)

        return test_file

    def analyze_responses(self) -> Dict:
        """
        Analyze the test responses

        Returns:
            Analysis results including scores and insights
        """
        if not self.current_test or not self.current_test["responses"]:
            raise ValueError("No test responses to analyze.")

        analysis = {
            "test_id": self.current_test["test_id"],
            "test_type": self.current_test["test_type"],
            "timestamp": datetime.now().isoformat(),
            "scores": {},
            "insights": [],
            "follow_up_analysis": []
        }

        # Calculate scores for numeric responses
        numeric_responses = [
            r for r in self.current_test["responses"]
            if r["question_id"] in ["empathy_1", "empathy_2", "empathy_3"]
        ]

        if numeric_responses:
            scores = [int(r["response"]) for r in numeric_responses]
            analysis["scores"]["average"] = sum(scores) / len(scores)
            analysis["scores"]["min"] = min(scores)
            analysis["scores"]["max"] = max(scores)

        # Add insights for open-ended responses
        open_ended_responses = [
            r for r in self.current_test["responses"]
            if r["question_id"] in ["empathy_4", "empathy_5", "empathy_6"]
        ]

        for response in open_ended_responses:
            insight = {
                "question_id": response["question_id"],
                "response": response["response"]
            }

            # Add follow-up analysis if available
            follow_ups = [
                f for f in self.current_test["follow_ups"]
                if f["question_id"] == response["question_id"]
            ]
            if follow_ups:
                insight["follow_ups"] = follow_ups

            analysis["insights"].append(insight)

        return analysis
