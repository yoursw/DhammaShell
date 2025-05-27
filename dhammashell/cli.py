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
    AuditReport,
)
from .main import DhammaShell


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


@cli.command(name="audit")
@click.option("--session-id", help="Session ID to audit")
@click.option(
    "--confidence", default=0.99999, help="Required confidence level (default: 99.999%)"
)
@click.option("--sigma", default=6, help="Required sigma level (default: 6)")
def audit(session_id: Optional[str], confidence: float, sigma: int):
    """Generate compliance audit report"""
    try:
        # Initialize components
        data_collector = ResearchDataCollector()
        audit_report = AuditReport()

        # Get session data
        if session_id:
            session_data = data_collector.load_session(session_id)
        else:
            # Get the most recent session
            sessions = data_collector.list_sessions()
            if not sessions:
                click.echo("No sessions found")
                return
            session_data = data_collector.load_session(sessions[-1])

        if not session_data:
            click.echo("No session data found")
            return

        # Generate audit report
        report = audit_report.generate_audit_report(
            session_data=session_data, confidence_level=confidence, sigma_level=sigma
        )

        click.echo(report)

    except Exception as e:
        click.echo(f"Error generating audit report: {str(e)}", err=True)


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
def set(clear: bool, research: Optional[bool]):
    """Set configuration values."""
    try:
        ds = DhammaShell()
        if clear:
            ds.config.clear_api_key()
        elif research is not None:
            ds.config.set_research_mode(research)
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
        research_status = "Enabled" if settings["research_mode"] else "Disabled"
        click.echo(f"Research Mode: {research_status}")

        click.echo("-------------------------\n")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


def main():
    """Entry point for the CLI"""
    cli()


if __name__ == "__main__":
    main()
