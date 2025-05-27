#!/usr/bin/env python3

import sys
import time
import logging
from typing import Optional
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from textblob import TextBlob
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

from .middleseek import MiddleSeekProtocol, MessageType, MiddleSeekMessage
from .config import Config
from .empathy_research import EmpathyAnalyzer, ResearchDataCollector
from .alignment import AlignmentReporter, AlignmentMetric

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = typer.Typer()
console = Console()


class DhammaShell:
    def __init__(self, calm_mode: bool = False):
        """Initialize DhammaShell.

        Args:
            calm_mode: Whether to enable zen mode with delays
        """
        self.calm_mode = calm_mode
        self.session = PromptSession()
        self.style = Style.from_dict(
            {
                "prompt": "ansicyan",
                "input": "ansigreen",
            }
        )
        self.config = Config()
        self._middleseek = None
        self._empathy_analyzer = None
        self._research_collector = None
        self._alignment_reporter = None
        self.conversation_context = []

    @property
    def research_mode(self) -> bool:
        """Get research mode from config."""
        return self.config.get_research_mode()

    @property
    def middleseek(self) -> MiddleSeekProtocol:
        """Get or initialize MiddleSeek protocol."""
        if self._middleseek is None:
            api_key = self.config.get_api_key()
            self._middleseek = MiddleSeekProtocol(api_key)
        return self._middleseek

    @property
    def empathy_analyzer(self) -> EmpathyAnalyzer:
        """Get or initialize empathy analyzer."""
        if self._empathy_analyzer is None:
            self._empathy_analyzer = EmpathyAnalyzer()
        return self._empathy_analyzer

    @property
    def research_collector(self) -> Optional[ResearchDataCollector]:
        """Get or initialize research collector if research mode is enabled."""
        if self.research_mode and self._research_collector is None:
            self._research_collector = ResearchDataCollector()
            self._research_collector.start_session()
        return self._research_collector

    @property
    def alignment_reporter(self) -> Optional[AlignmentReporter]:
        """Get or initialize alignment reporter if enabled."""
        if self.config.alignment.enabled and self._alignment_reporter is None:
            self._alignment_reporter = AlignmentReporter(
                report_dir=self.config.alignment.report_dir
            )
        return self._alignment_reporter

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

    def analyze_alignment(self, user_input: str, response: str) -> None:
        """Analyze and record alignment metrics for the interaction.

        Args:
            user_input: The user's input message
            response: The system's response
        """
        if not self.alignment_reporter:
            return

        try:
            # Analyze compassion alignment
            compassion_score, _ = self.analyze_compassion(response)
            self.alignment_reporter.add_metric(
                "compassion_alignment",
                compassion_score / 4.0,  # Normalize to 0-1
                confidence=0.8,
                context={"user_input": user_input}
            )

            # Analyze response length alignment
            response_length = len(response.split())
            ideal_length = 50  # Example target length
            length_alignment = 1.0 - min(abs(response_length - ideal_length) / ideal_length, 1.0)
            self.alignment_reporter.add_metric(
                "response_length_alignment",
                length_alignment,
                confidence=0.9,
                context={"response_length": response_length}
            )

            # Set risk level based on compassion score
            if compassion_score <= 2:
                self.alignment_reporter.set_risk_level("high")
                self.alignment_reporter.add_recommendation(
                    "Consider improving compassion in responses"
                )
            elif compassion_score == 3:
                self.alignment_reporter.set_risk_level("medium")
            else:
                self.alignment_reporter.set_risk_level("low")

            # Save report if auto-save is enabled
            if self.config.alignment.auto_save:
                self.alignment_reporter.save_report(
                    summary=f"Alignment analysis for interaction: {user_input[:50]}..."
                )

        except Exception as e:
            logger.error(f"Failed to analyze alignment: {str(e)}")

    def handle_message(self, user_input: str) -> None:
        """Handle a message using MiddleSeek protocol."""
        if not user_input.strip():
            return

        try:
            # Create seek message
            seek_msg = self.middleseek.create_seek_message(user_input)

            # Analyze compassion
            score, feedback = self.analyze_compassion(user_input)
            self.display_compassion_check(score, feedback)

            # If score is low, request clarification
            if score < 3:
                clarify_msg = self.middleseek.request_clarification(seek_msg, score)
                console.print(f"\n[System] {clarify_msg.content}\n")

                confirm = Prompt.ask("Send anyway?", choices=["Y", "N"], default="N")
                if confirm.upper() != "Y":
                    return

            # Acknowledge the message
            ack_msg = self.middleseek.acknowledge(seek_msg)
            console.print(f"\n[System] {ack_msg.content}\n")

            # Generate and send response
            if self.calm_mode:
                time.sleep(1)

            # Add conversation context to the API call
            response_content = self.middleseek.generate_response(
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

            response_msg = self.middleseek.create_response(
                response_content, {"compassion_score": score}
            )
            console.print(f"\n[System] {response_msg.content}\n")

            # Analyze alignment
            self.analyze_alignment(user_input, response_content)

            # Analyze and record interaction for research if enabled
            if self.research_mode and self.research_collector:
                analysis = self.empathy_analyzer.analyze_interaction(
                    user_input=user_input,
                    system_response=response_content,
                    context=self.conversation_context
                )
                self.research_collector.record_interaction(
                    user_input=user_input,
                    system_response=response_content,
                    analysis=analysis,
                )

        except Exception as e:
            logger.error(f"Failed to handle message: {str(e)}")
            console.print(f"[red]Error: {str(e)}[/red]")

    def chat_loop(self):
        """Main chat loop."""
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
                        # Save research data before exiting if enabled
                        if self.research_mode and self.research_collector:
                            self.research_collector.save_session()
                            console.print("\n[yellow]Research data saved.[/yellow]")
                        break

                    # Handle message with MiddleSeek protocol
                    self.handle_message(user_input)

                except KeyboardInterrupt:
                    # Save research data before exiting if enabled
                    if self.research_mode and self.research_collector:
                        self.research_collector.save_session()
                        console.print(
                            "\n[yellow]Chat session ended. Research data saved.[/yellow]"
                        )
                    break
                except Exception as e:
                    logger.error(f"Error in chat loop: {str(e)}")
                    console.print(f"[red]Error: {str(e)}[/red]")
        finally:
            # Ensure research data is saved even if there's an error
            if self.research_mode and self.research_collector:
                try:
                    self.research_collector.save_session()
                except Exception as e:
                    logger.error(f"Failed to save research data: {str(e)}")


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
    alignment: Optional[bool] = typer.Option(
        None, "--alignment", help="Enable/disable AI alignment reporting"
    ),
    alignment_dir: Optional[str] = typer.Option(
        None, "--alignment-dir", help="Directory for alignment reports"
    ),
    auto_save: Optional[bool] = typer.Option(
        None, "--auto-save", help="Enable/disable automatic report saving"
    ),
    risk_threshold: Optional[float] = typer.Option(
        None, "--risk-threshold", help="Threshold for high risk level (0-1)"
    ),
):
    """Configure DhammaShell settings."""
    config = Config()

    if clear:
        config.clear_api_key()

    if research is not None:
        config.set_research_mode(research)

    if alignment is not None or alignment_dir is not None or auto_save is not None or risk_threshold is not None:
        config.set_alignment_settings(
            enabled=alignment,
            report_dir=alignment_dir,
            auto_save=auto_save,
            risk_threshold=risk_threshold
        )

    settings = config.get_all_settings()
    console.print("\nCurrent settings:")
    for key, value in settings.items():
        console.print(f"{key}: {value}")


@app.command()
def export(calm: bool = typer.Option(False, "--calm", help="Enable zen mode")):
    """Export the current conversation."""
    try:
        ds = DhammaShell(calm_mode=calm)
        console.print(ds.middleseek.export_conversation())
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
