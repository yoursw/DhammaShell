#!/usr/bin/env python3

import sys
import time
import logging
from typing import Optional, List, Dict
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
from .empathy_research.pre_post_test import EmpathyTest, TestType

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
        self._empathy_test = None
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
    def empathy_test(self) -> Optional[EmpathyTest]:
        """Get or initialize empathy test if research mode is enabled."""
        if self.research_mode and self._empathy_test is None:
            self._empathy_test = EmpathyTest()
        return self._empathy_test

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

    def start_empathy_test(self, test_type: TestType) -> Dict:
        """
        Start a pre or post empathy test

        Args:
            test_type: Type of test (pre or post)

        Returns:
            Test configuration including questions
        """
        if not self.research_mode:
            raise ValueError("Research mode must be enabled to start empathy test")

        test_config = self.empathy_test.start_test(test_type)

        # Update LLM availability status
        if self.middleseek.is_available():
            self.empathy_test.current_test["llm_available"] = True

        return test_config

    def record_test_response(self, question_id: str, response: str) -> None:
        """
        Record a response to a test question

        Args:
            question_id: ID of the question being answered
            response: User's response
        """
        if not self.research_mode or not self.empathy_test:
            raise ValueError("Research mode must be enabled to record test responses")

        self.empathy_test.record_response(question_id, response)

        # If LLM is available and this is an open-ended question, ask follow-up
        if (self.middleseek.is_available() and
            self.empathy_test.current_test["llm_available"] and
            question_id in ["empathy_4", "empathy_5", "empathy_6"]):

            # Get the follow-up prompt for this question
            question = next(
                q for q in self.empathy_test.EXTENDED_QUESTIONS
                if q["id"] == question_id
            )
            follow_up = question["follow_up_prompt"]

            # Get user's response to follow-up
            console.print(f"\n[Follow-up] {follow_up}")
            follow_up_response = self.session.prompt(
                HTML("<prompt>[You] ➜ </prompt>"), style=self.style
            )

            # Record the follow-up interaction
            self.empathy_test.record_follow_up(question_id, follow_up, follow_up_response)

    def complete_empathy_test(self) -> Dict:
        """
        Complete the current empathy test and get analysis

        Returns:
            Analysis results including scores and insights
        """
        if not self.research_mode or not self.empathy_test:
            raise ValueError("Research mode must be enabled to complete empathy test")

        # Save test results
        test_file = self.empathy_test.save_test()

        # Get analysis
        analysis = self.empathy_test.analyze_responses()

        return analysis


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
