"""
Research Data Collection Component for DhammaShell
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class ResearchDataCollector:
    def __init__(self, data_dir: str = "research_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = None

    def start_session(self, session_id: Optional[str] = None) -> str:
        """
        Start a new research data collection session

        Args:
            session_id: Optional custom session ID

        Returns:
            The session ID
        """
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.current_session = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "interactions": [],
        }

        return session_id

    def record_interaction(
        self, user_input: str, system_response: str, analysis: Dict
    ) -> None:
        """
        Record an interaction with its analysis

        Args:
            user_input: The user's input
            system_response: The system's response
            analysis: The empathy analysis results
        """
        if self.current_session is None:
            self.start_session()

        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "system_response": system_response,
            "analysis": analysis,
        }

        self.current_session["interactions"].append(interaction)

    def save_session(self) -> str:
        """
        Save the current session to disk

        Returns:
            Path to the saved session file
        """
        if self.current_session is None:
            raise ValueError("No active session to save")

        session_id = self.current_session["session_id"]
        filename = f"session_{session_id}.json"
        filepath = self.data_dir / filename

        with open(filepath, "w") as f:
            json.dump(self.current_session, f, indent=2)

        return str(filepath)

    def load_session(self, session_id: str) -> Dict:
        """
        Load a previous session

        Args:
            session_id: The session ID to load

        Returns:
            The loaded session data
        """
        filename = f"session_{session_id}.json"
        filepath = self.data_dir / filename

        with open(filepath, "r") as f:
            return json.load(f)

    def get_available_sessions(self) -> List[str]:
        """
        Get list of available session IDs

        Returns:
            List of session IDs
        """
        return [
            f.stem.replace("session_", "") for f in self.data_dir.glob("session_*.json")
        ]
