"""
Research Data Collection Module for DhammaShell
Manages research session data collection and persistence
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ResearchDataCollector:
    def __init__(self, data_dir: str = "research_data"):
        """
        Initialize the research data collector

        Args:
            data_dir: Directory to store research data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.current_session = None

    def start_session(self) -> str:
        """
        Start a new research session

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
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
        Record an interaction in the current session

        Args:
            user_input: User's input text
            system_response: System's response text
            analysis: Analysis results from EmpathyAnalyzer
        """
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")

        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "system_response": system_response,
            "analysis": analysis,
        }

        self.current_session["interactions"].append(interaction)

    def save_session(self) -> Path:
        """
        Save the current session to disk

        Returns:
            Path to the saved session file
        """
        if not self.current_session:
            raise ValueError("No active session to save.")

        session_id = self.current_session["session_id"]
        filepath = self.data_dir / f"session_{session_id}.json"

        with open(filepath, "w") as f:
            json.dump(self.current_session, f, indent=2)

        return filepath

    def load_session(self, session_id: str) -> Dict:
        """
        Load a session from disk

        Args:
            session_id: ID of the session to load

        Returns:
            Session data
        """
        filepath = self.data_dir / f"session_{session_id}.json"

        if not filepath.exists():
            raise ValueError(f"Session {session_id} not found.")

        with open(filepath, "r") as f:
            return json.load(f)

    def list_sessions(self) -> List[str]:
        """
        List all available session IDs

        Returns:
            List of session IDs
        """
        sessions = []
        for filepath in self.data_dir.glob("session_*.json"):
            session_id = filepath.stem.replace("session_", "")
            sessions.append(session_id)
        return sorted(sessions)

    def get_session_summary(self, session_id: str) -> Dict:
        """
        Get a summary of a session

        Args:
            session_id: ID of the session

        Returns:
            Session summary
        """
        session_data = self.load_session(session_id)

        return {
            "session_id": session_data["session_id"],
            "start_time": session_data["start_time"],
            "total_interactions": len(session_data["interactions"]),
            "last_interaction": (
                session_data["interactions"][-1]["timestamp"]
                if session_data["interactions"]
                else None
            ),
        }
