#!/usr/bin/env python3

import sys
import time
import logging
from typing import Optional, Dict, Tuple
from pathlib import Path
from datetime import timedelta

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from textblob import TextBlob
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
import click

from .middleseek.core import MiddleSeekCore, MiddleSeek
from .middleseek.alignment import SystemHealth, AlignmentAuditor
from .config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = typer.Typer()
console = Console()


class DhammaShell:
    """Main class for DharmaShell functionality."""

    def __init__(self, calm_mode: bool = False):
        """Initialize DharmaShell."""
        self.api_key = config.api_key
        if not self.api_key:
            raise ValueError("API key is required. Please configure it first.")

        self.calm_mode = calm_mode
        self.core = MiddleSeekCore(self.api_key)
        self.health = SystemHealth()
        self.alignment_auditor = AlignmentAuditor(self.core.chat_history)
        self.session = PromptSession()
        self.style = Style.from_dict(
            {
                "prompt": "ansicyan",
                "input": "ansigreen",
            }
        )
        self.config = Config()
        self.conversation_context = []

    @property
    def research_mode(self) -> bool:
        """Get research mode from config."""
        return self.config.get_research_mode()

    def analyze_compassion(self, text: str) -> tuple[int, str]:
        """Analyze compassion level in text."""
        try:
            # Use TextBlob for sentiment analysis
            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity

            # Map sentiment to compassion score (0-5)
            if sentiment < -0.5:
                score = 1
                feedback = "Consider expressing this more compassionately."
            elif sentiment < 0:
                score = 2
                feedback = "Try to maintain a more peaceful tone."
            elif sentiment < 0.5:
                score = 3
                feedback = "Good balance of expression."
            else:
                score = 4
                feedback = "Very compassionate expression."

            return score, feedback
        except Exception as e:
            logger.error(f"Failed to analyze compassion: {str(e)}")
            return 3, "Unable to analyze compassion level."

    def display_compassion_check(self, score: int, feedback: str) -> None:
        """Display compassion check results."""
        color = {
            1: "red",
            2: "yellow",
            3: "green",
            4: "blue",
        }.get(score, "white")

        console.print(f"\n[Compassion Check] ", end="")
        console.print(f"[{color}]Score: {score}/5 - {feedback}[/{color}]\n")

    def handle_message(self, user_input: str) -> None:
        """Handle a message using MiddleSeek protocol."""
        if not user_input.strip():
            return

        try:
            # Create seek message
            seek_msg = self.core.create_seek_message(user_input)

            # Analyze compassion
            score, feedback = self.analyze_compassion(user_input)
            self.display_compassion_check(score, feedback)

            # If score is low, request clarification
            if score < 3:
                clarify_msg = self.core.request_clarification(seek_msg, score)
                console.print(f"\n[System] {clarify_msg.content}\n")

                confirm = Prompt.ask("Send anyway?", choices=["Y", "N"], default="N")
                if confirm.upper() != "Y":
                    return

            # Acknowledge the message
            ack_msg = self.core.acknowledge(seek_msg)
            console.print(f"\n[System] {ack_msg.content}\n")

            # Generate and send response
            if self.calm_mode:
                time.sleep(1)

            # Add conversation context to the API call
            response_content = self.core.generate_response(
                seek_msg,
                score,
                context=self.conversation_context
            )

            # Update conversation context
            self.conversation_context.append({
                "role": "user",
                "content": user_input
            })
            self.conversation_context.append({
                "role": "assistant",
                "content": response_content
            })

            # Keep only last 10 messages for context
            if len(self.conversation_context) > 10:
                self.conversation_context = self.conversation_context[-10:]

            response_msg = self.core.create_response(
                response_content, {"compassion_score": score}
            )
            console.print(f"\n[System] {response_msg.content}\n")

        except Exception as e:
            logger.error(f"Failed to handle message: {str(e)}")
            console.print(f"[red]Error: {str(e)}[/red]")

    def chat_loop(self):
        """Start an interactive chat session."""
        console.print("\n🌀 DhammaShell v1.0 - Type mindfully\n")
        if self.research_mode:
            console.print("[yellow]Research data collection is enabled[/yellow]\n")

        try:
            while True:
                try:
                    # Get user input with custom prompt
                    user_input = self.session.prompt(
                        HTML("<prompt>[You] ➜ </prompt>"), style=self.style
                    )

                    if user_input.lower() in ["exit", "quit", "q"]:
                        break

                    # Handle message with MiddleSeek protocol
                    self.handle_message(user_input)

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Error in chat loop: {str(e)}")
                    console.print(f"[red]Error: {str(e)}[/red]")
        finally:
            # Ensure research data is saved even if there's an error
            if self.research_mode:
                try:
                    self.core.save_session()
                except Exception as e:
                    logger.error(f"Failed to save research data: {str(e)}")

    def get_alignment_report(self, time_window: Optional[timedelta] = None) -> str:
        """Get a human-readable alignment report."""
        return self.alignment_auditor.generate_alignment_report(time_window)

    def get_alignment_metrics(self, time_window: Optional[timedelta] = None) -> Dict:
        """Get alignment metrics as a dictionary."""
        return self.alignment_auditor.analyze_alignment(time_window).to_dict()

    def check_health(self) -> Tuple[bool, str]:
        """Check system health."""
        return self.health.check_health()


@app.command()
def chat(calm: bool = typer.Option(False, "--calm", help="Enable zen mode")):
    """Start the mindful chat interface."""
    try:
        ds = DhammaShell(calm_mode=calm)
        ds.chat_loop()
    except Exception as e:
        logger.error(f"Failed to start chat: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@app.command()
def check(text: str = typer.Argument(..., help="Text to analyze for compassion")):
    """Check if a message is kind."""
    try:
        ds = DhammaShell()
        score, feedback = ds.analyze_compassion(text)
        ds.display_compassion_check(score, feedback)
    except Exception as e:
        logger.error(f"Failed to check compassion: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@app.command()
def config(
    clear: bool = typer.Option(False, "--clear", help="Clear stored API key"),
    research: Optional[bool] = typer.Option(
        None, "--research", help="Enable/disable research mode"
    ),
):
    """Configure DhammaShell settings."""
    try:
        ds = DhammaShell()
        if clear:
            ds.config.clear_api_key()
        elif research is not None:
            ds.config.set_research_mode(research)
        else:
            ds.config.get_api_key()
    except Exception as e:
        logger.error(f"Failed to configure: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@app.command()
def export(calm: bool = typer.Option(False, "--calm", help="Enable zen mode")):
    """Export the current conversation."""
    try:
        ds = DhammaShell(calm_mode=calm)
        console.print(ds.core.export_conversation())
    except Exception as e:
        logger.error(f"Failed to export conversation: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


def main():
    try:
        app()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
