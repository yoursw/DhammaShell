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

    @property
    def research_mode(self) -> bool:
        """Get research mode from config."""
        return self.config.get_research_mode()

    @property
    def middleseek(self) -> MiddleSeekProtocol:
        """Lazy initialization of MiddleSeekProtocol."""
        if self._middleseek is None:
            try:
                api_key = self.config.get_api_key()
                if not api_key:
                    raise ValueError(
                        "OpenRouter API key is required. Run 'ds config' to set it up."
                    )
                self._middleseek = MiddleSeekProtocol(api_key=api_key)
            except Exception as e:
                logger.error(f"Failed to initialize MiddleSeek protocol: {str(e)}")
                raise
        return self._middleseek

    @property
    def empathy_analyzer(self) -> EmpathyAnalyzer:
        """Lazy initialization of EmpathyAnalyzer."""
        if self._empathy_analyzer is None:
            self._empathy_analyzer = EmpathyAnalyzer()
        return self._empathy_analyzer

    @property
    def research_collector(self) -> Optional[ResearchDataCollector]:
        """Lazy initialization of ResearchDataCollector.

        Returns:
            ResearchDataCollector if research_mode is enabled, None otherwise
        """
        if not self.research_mode:
            return None

        if self._research_collector is None:
            self._research_collector = ResearchDataCollector()
            # Start a new research session
            self._research_collector.start_session()
        return self._research_collector

    def analyze_compassion(self, text: str) -> tuple[int, str]:
        """Analyze text for compassion level and provide feedback.

        Args:
            text: The text to analyze

        Returns:
            Tuple of (compassion_score, feedback)

        Raises:
            ValueError: If text is empty or invalid
        """
        if not text or not isinstance(text, str) or len(text.strip()) == 0:
            raise ValueError("Invalid text for analysis")

        try:
            blob = TextBlob(text.strip())

            # Simple sentiment analysis
            sentiment = blob.sentiment.polarity

            # Check for negative words
            negative_words = ["hate", "stupid", "idiot", "dumb", "ugly", "terrible"]
            negative_count = sum(
                1 for word in text.lower().split() if word in negative_words
            )

            # Calculate compassion score (0-5)
            base_score = 3
            score = base_score + int(sentiment * 2) - negative_count
            score = max(0, min(5, score))

            # Generate feedback
            if score < 3:
                feedback = "💡 Try rephrasing with more kindness and understanding."
            elif score < 4:
                feedback = "💡 Good, but could be more compassionate."
            else:
                feedback = "💡 Excellent compassionate communication!"

            return score, feedback
        except Exception as e:
            logger.error(f"Failed to analyze compassion: {str(e)}")
            raise

    def display_compassion_check(self, score: int, feedback: str):
        """Display the compassion check with hearts.

        Args:
            score: The compassion score (0-5)
            feedback: The feedback message
        """
        try:
            hearts = "❤️" * score + "🤍" * (5 - score)
            console.print(f"\n⚠️ Compassion Check: {score}/5 hearts")
            console.print(f"{hearts}")
            console.print(f"{feedback}\n")
        except Exception as e:
            logger.error(f"Failed to display compassion check: {str(e)}")
            raise

    def handle_message(self, user_input: str) -> None:
        """Handle a message using MiddleSeek protocol.

        Args:
            user_input: The user's input message

        Raises:
            ValueError: If user_input is empty or invalid
        """
        if (
            not user_input
            or not isinstance(user_input, str)
            or len(user_input.strip()) == 0
        ):
            raise ValueError("Invalid user input")

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

            response_content = self.middleseek.generate_response(seek_msg, score)
            response_msg = self.middleseek.create_response(
                response_content, {"compassion_score": score}
            )
            console.print(f"\n[System] {response_msg.content}\n")

            # Analyze and record interaction for research if enabled
            if self.research_mode and self.research_collector:
                analysis = self.empathy_analyzer.analyze_interaction(
                    user_input=user_input, system_response=response_content
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
