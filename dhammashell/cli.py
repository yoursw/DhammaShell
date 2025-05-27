"""
DhammaShell Command Line Interface
"""

import click
from pathlib import Path
from typing import Optional
import json
from datetime import datetime
from .empathy_research import (
    EmpathyAnalyzer,
    ResearchDataCollector,
    EmpathyMetrics,
    ResearchReport,
)
from .main import DhammaShell
from .alignment import AlignmentReporter, AlignmentMetric
from .middleseek import MessageType


@click.group()
def cli():
    """DhammaShell - A mindful terminal chat tool"""
    pass


@cli.command(name="research-report")
@click.option("--session-id", help="Session ID to analyze")
@click.option(
    "--output-format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
@click.option(
    "--no-visualizations", is_flag=True, help="Disable visualization generation"
)
def research_report(session_id, output_format, no_visualizations):
    """Generate a research report from session data"""
    try:
        collector = ResearchDataCollector()

        if session_id:
            session_data = collector.load_session(session_id)
        else:
            # Get the most recent session
            sessions = collector.list_sessions()
            if not sessions:
                click.echo("No research sessions found.")
                return
            session_data = collector.load_session(sessions[-1])

        report_generator = ResearchReport()
        report = report_generator.generate_report(
            session_data,
            output_format=output_format,
            include_visualizations=not no_visualizations,
        )

        if output_format == "text":
            click.echo(report)
        else:
            # Save JSON report to file
            output_file = Path(f"research_report_{session_data['session_id']}.json")
            output_file.write_text(report)
            click.echo(f"JSON report saved to {output_file}")

    except Exception as e:
        click.echo(f"Error generating research report: {str(e)}", err=True)


@cli.command()
@click.option("--calm", is_flag=True, help="Enable zen mode with delays")
def chat(calm: bool):
    """Start an interactive chat session"""
    try:
        ds = DhammaShell(calm_mode=calm)
        ds.chat_loop()
    except Exception as e:
        click.echo(f"Error in chat session: {str(e)}", err=True)


@cli.command(name="update-research")
@click.option("--session-id", help="Chat session ID to analyze")
@click.option(
    "--output-format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def update_research(session_id: Optional[str], output_format: str):
    """Update research data from chat history"""
    try:
        # Initialize components
        ds = DhammaShell()
        analyzer = EmpathyAnalyzer()
        collector = ResearchDataCollector()

        # Get chat history
        if session_id:
            chat_history = ds.middleseek.get_conversation_history(session_id)
        else:
            chat_history = ds.middleseek.get_latest_conversation()

        if not chat_history:
            click.echo("No chat history found")
            return

        # Start a new research session
        research_session_id = collector.start_session()

        # Process each interaction
        for interaction in chat_history:
            # Analyze the interaction
            analysis = analyzer.analyze_interaction(
                user_input=interaction["user_input"],
                system_response=interaction["system_response"],
            )

            # Record the interaction
            collector.record_interaction(
                user_input=interaction["user_input"],
                system_response=interaction["system_response"],
                analysis=analysis,
            )

        # Save the research session
        filepath = collector.save_session()

        # Generate report
        report_generator = ResearchReport()
        report = report_generator.generate_report(
            collector.load_session(research_session_id), output_format=output_format
        )

        if output_format == "text":
            click.echo(report)
        else:
            # Save JSON report to file
            output_file = Path(f"research_report_{research_session_id}.json")
            output_file.write_text(report)
            click.echo(f"JSON report saved to {output_file}")

        click.echo(f"\nResearch data updated successfully!")
        click.echo(f"Session ID: {research_session_id}")
        click.echo(f"Data saved to: {filepath}")

    except Exception as e:
        click.echo(f"Error updating research data: {str(e)}", err=True)


@cli.group()
def config():
    """Configure DhammaShell settings."""
    pass


@config.command()
@click.option("--clear", is_flag=True, help="Clear stored API key")
@click.option("--research", type=bool, help="Enable/disable research mode")
@click.option("--alignment", type=bool, help="Enable/disable AI alignment reporting")
@click.option("--alignment-dir", type=str, help="Directory for alignment reports")
@click.option("--auto-save", type=bool, help="Enable/disable automatic report saving")
@click.option("--risk-threshold", type=float, help="Threshold for high risk level (0-1)")
def set(clear: bool, research: Optional[bool], alignment: Optional[bool],
        alignment_dir: Optional[str], auto_save: Optional[bool],
        risk_threshold: Optional[float]):
    """Set configuration values."""
    try:
        ds = DhammaShell()
        if clear:
            ds.config.clear_api_key()
        elif research is not None:
            ds.config.set_research_mode(research)
        elif any([alignment is not None, alignment_dir is not None,
                 auto_save is not None, risk_threshold is not None]):
            ds.config.set_alignment_settings(
                enabled=alignment,
                report_dir=alignment_dir,
                auto_save=auto_save,
                risk_threshold=risk_threshold
            )
        else:
            ds.config.get_api_key()
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


@config.command()
def show():
    """Show current configuration settings."""
    try:
        ds = DhammaShell()
        settings = ds.config.get_all_settings()

        click.echo("\nDhammaShell Configuration:")
        click.echo("-------------------------")

        # API Key status
        api_status = "Configured" if settings["api_key"] else "Not configured"
        click.echo(f"API Key: {api_status}")

        # Research mode
        research_status = "Enabled" if settings["research_enabled"] else "Disabled"
        click.echo(f"Research Mode: {research_status}")

        # Alignment settings
        click.echo("\nAlignment Settings:")
        click.echo("-----------------")
        alignment = settings["alignment"]
        click.echo(f"Enabled: {alignment['enabled']}")
        click.echo(f"Report Directory: {alignment['report_dir']}")
        click.echo(f"Auto Save: {alignment['auto_save']}")
        click.echo(f"Risk Threshold: {alignment['risk_threshold']}")

        click.echo("-------------------------\n")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


@cli.command(name="alignment-audit")
@click.argument("text", required=False)
@click.option("--session-id", help="Session ID to analyze")
@click.option("--output-format", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.option("--save-report", is_flag=True, help="Save the alignment report to file")
def alignment_audit(text: Optional[str], session_id: Optional[str], output_format: str, save_report: bool):
    """Analyze alignment metrics for text or conversation session."""
    try:
        ds = DhammaShell()
        reporter = AlignmentReporter()

        if text:
            # Analyze single text input
            compassion_score, _ = ds.analyze_compassion(text)
            reporter.add_metric(
                "compassion_alignment",
                compassion_score / 4.0,  # Normalize to 0-1
                confidence=0.8,
                context={"text": text}
            )

            # Analyze text length
            text_length = len(text.split())
            ideal_length = 50  # Example target length
            length_alignment = 1.0 - min(abs(text_length - ideal_length) / ideal_length, 1.0)
            reporter.add_metric(
                "response_length_alignment",
                length_alignment,
                confidence=0.9,
                context={"text_length": text_length}
            )

            # Set risk level based on compassion score
            if compassion_score <= 2:
                reporter.set_risk_level("high")
                reporter.add_recommendation(
                    "Consider improving compassion in the text"
                )
            elif compassion_score == 3:
                reporter.set_risk_level("medium")
            else:
                reporter.set_risk_level("low")

            reporter.save_report(
                summary=f"Alignment analysis for text: {text[:50]}..."
            )

        elif session_id:
            # Analyze conversation session
            chat_history = ds.middleseek.get_conversation_history(session_id)
            if not chat_history:
                click.echo("No conversation history found for the given session ID")
                return

            # Analyze each interaction
            for interaction in chat_history:
                user_input = interaction["user_input"]
                system_response = interaction["system_response"]

                # Analyze compassion alignment
                compassion_score, _ = ds.analyze_compassion(system_response)
                reporter.add_metric(
                    "compassion_alignment",
                    compassion_score / 4.0,
                    confidence=0.8,
                    context={
                        "user_input": user_input,
                        "system_response": system_response
                    }
                )

                # Analyze response length
                response_length = len(system_response.split())
                ideal_length = 50
                length_alignment = 1.0 - min(abs(response_length - ideal_length) / ideal_length, 1.0)
                reporter.add_metric(
                    "response_length_alignment",
                    length_alignment,
                    confidence=0.9,
                    context={"response_length": response_length}
                )

            # Set overall risk level based on average compassion score
            avg_compassion = sum(m.value for m in reporter.current_report.metrics
                               if m.metric_name == "compassion_alignment") / len(reporter.current_report.metrics)

            if avg_compassion <= 0.5:  # Normalized score of 2 or less
                reporter.set_risk_level("high")
                reporter.add_recommendation(
                    "Overall compassion level is low. Consider improving response quality."
                )
            elif avg_compassion <= 0.75:  # Normalized score of 3
                reporter.set_risk_level("medium")
            else:
                reporter.set_risk_level("low")

            reporter.save_report(
                summary=f"Alignment analysis for session {session_id}"
            )

        else:
            click.echo("Please provide either text to analyze or a session ID")
            return

        # Display or save the report
        if output_format == "text":
            reporter.display_report()
        else:
            # Save JSON report
            if save_report:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = Path(f"alignment_report_{timestamp}.json")
                with open(output_file, 'w') as f:
                    json.dump(reporter.current_report.dict(), f, indent=2, default=str)
                click.echo(f"Alignment report saved to {output_file}")
            else:
                click.echo(json.dumps(reporter.current_report.dict(), indent=2, default=str))

    except Exception as e:
        click.echo(f"Error in alignment audit: {str(e)}", err=True)
        raise click.Abort()


@cli.group()
def audit():
    """Audit and analyze conversation data."""
    pass


@audit.command()
@click.option('--session-id', help='Session ID to analyze (defaults to latest)')
@click.option('--format', type=click.Choice(['text', 'json']), default='text', help='Output format')
@click.option('--save/--no-save', default=True, help='Save report to file')
def alignment(session_id, format, save):
    """Analyze alignment metrics for a conversation session."""
    try:
        # Initialize DhammaShell and reporter
        ds = DhammaShell()
        reporter = AlignmentReporter()

        # Get conversation history
        history = ds.middleseek.history

        if not history:
            click.echo("No conversation history found")
            return

        # Analyze each message
        metrics = []
        for msg in history:
            if msg.type == MessageType.RESPOND:
                # Analyze compassion alignment
                compassion_score = reporter.analyze_compassion(msg.content)
                metrics.append(AlignmentMetric(
                    metric_name="compassion_alignment",
                    value=compassion_score,
                    confidence=0.8,
                    context={"message": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content}
                ))

                # Analyze response length
                length_score = reporter.analyze_response_length(msg.content)
                metrics.append(AlignmentMetric(
                    metric_name="response_length_alignment",
                    value=length_score,
                    confidence=0.9,
                    context={"word_count": len(msg.content.split())}
                ))

        # Generate report
        report = reporter.generate_report(metrics)

        # Save report if requested
        if save:
            reporter.save_report(report)
            click.echo(f"Report saved to {reporter.report_dir}")

        # Display report
        if format == 'json':
            click.echo(json.dumps(report.dict(), indent=2))
        else:
            click.echo("\nAlignment Analysis Report")
            click.echo("=" * 50)
            click.echo(f"Total Messages Analyzed: {len(metrics) // 2}")  # Divide by 2 because each message has 2 metrics
            click.echo(f"Average Compassion Score: {report.average_compassion:.2f}")
            click.echo(f"Average Length Score: {report.average_length:.2f}")
            click.echo(f"Risk Level: {report.risk_level}")
            click.echo("\nRecommendations:")
            for rec in report.recommendations:
                click.echo(f"- {rec}")
    except Exception as e:
        click.echo(f"Error in alignment audit: {str(e)}", err=True)
        raise click.Abort()


def main():
    """Entry point for the CLI"""
    cli()


if __name__ == "__main__":
    main()
