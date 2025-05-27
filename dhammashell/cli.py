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
from .empathy_research.pre_post_test import TestType
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
        report_file = report_generator.generate_report(session_data)

        # Read the generated report
        with open(report_file) as f:
            report_data = json.load(f)

        if output_format == "text":
            # Format as text
            click.echo("\nDhammaShell Research Report")
            click.echo("=" * 50)

            # Session Info
            click.echo("\nSession Information:")
            click.echo(f"Session ID: {report_data['session_id']}")
            click.echo(f"Start Time: {report_data['start_time']}")
            click.echo(f"End Time: {report_data['end_time']}")

            # Metrics Summary
            if report_data["metrics_summary"]:
                click.echo("\nMetrics Summary:")
                for metric, stats in report_data["metrics_summary"].items():
                    click.echo(f"\n{metric}:")
                    for stat, value in stats.items():
                        click.echo(f"  {stat}: {value:.2f}")

            # Interaction Analysis
            if report_data["interaction_analysis"]:
                click.echo("\nInteraction Analysis:")
                for key, value in report_data["interaction_analysis"].items():
                    click.echo(f"  {key}: {value}")

            # Empathy Test Analysis
            if "empathy_test_analysis" in report_data:
                click.echo("\nEmpathy Test Analysis:")
                test_analysis = report_data["empathy_test_analysis"]

                if "pre_test" in test_analysis:
                    click.echo("\nPre-Test Results:")
                    pre = test_analysis["pre_test"]
                    click.echo(f"  Average Score: {pre['average_score']:.2f}")
                    click.echo(f"  Min Score: {pre['min_score']:.2f}")
                    click.echo(f"  Max Score: {pre['max_score']:.2f}")

                if "post_test" in test_analysis:
                    click.echo("\nPost-Test Results:")
                    post = test_analysis["post_test"]
                    click.echo(f"  Average Score: {post['average_score']:.2f}")
                    click.echo(f"  Min Score: {post['min_score']:.2f}")
                    click.echo(f"  Max Score: {post['max_score']:.2f}")

                if "comparison" in test_analysis:
                    click.echo("\nComparison:")
                    comp = test_analysis["comparison"]
                    click.echo(f"  Score Change: {comp['score_change']:.2f}")
                    click.echo(f"  Percent Change: {comp['percent_change']:.1f}%")
                    click.echo(f"  Improvement: {'Yes' if comp['improvement'] else 'No'}")
        else:
            # Output as JSON
            click.echo(json.dumps(report_data, indent=2))

        click.echo(f"\nReport saved to: {report_file}")
        if not no_visualizations:
            click.echo("Visualizations generated in research_reports directory")

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
        report_file = report_generator.generate_report(
            collector.load_session(research_session_id)
        )

        # Read and display the report
        with open(report_file) as f:
            report_data = json.load(f)

        if output_format == "text":
            click.echo("\nResearch Report:")
            click.echo("=" * 50)
            click.echo(json.dumps(report_data, indent=2))
        else:
            click.echo(json.dumps(report_data, indent=2))

        click.echo(f"\nResearch data updated successfully!")
        click.echo(f"Session ID: {research_session_id}")
        click.echo(f"Data saved to: {filepath}")
        click.echo(f"Report saved to: {report_file}")

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


@cli.command()
@click.option('--type', type=click.Choice(['pre', 'post']), required=True, help='Type of empathy test')
def start_empathy_test(type: str):
    """Start a pre or post empathy assessment test"""
    shell = DhammaShell()

    if not shell.research_mode:
        click.echo("Error: Research mode must be enabled to start empathy test")
        return

    test_type = TestType.PRE if type == 'pre' else TestType.POST
    test_config = shell.start_empathy_test(test_type)

    click.echo(f"\nStarting {type} empathy test...")
    click.echo("Please answer the following questions:\n")

    for question in test_config["questions"]:
        click.echo(f"\n{question['question']}")
        if 'scale' in question:
            click.echo(f"Scale: {question['scale']}")
            click.echo(f"Description: {question['description']}")

        response = click.prompt("Your response", type=str)
        shell.record_test_response(question["id"], response)

        # Follow-up questions are handled automatically in record_test_response
        # if LLM is available

    # Complete the test and get analysis
    analysis = shell.complete_empathy_test()

    click.echo("\nTest completed! Here's your analysis:")

    # Display scores
    if "scores" in analysis:
        click.echo("\nScores:")
        for metric, value in analysis["scores"].items():
            click.echo(f"{metric}: {value:.2f}")

    # Display insights
    if "insights" in analysis:
        click.echo("\nInsights:")
        for insight in analysis["insights"]:
            click.echo(f"\nQuestion: {insight['question_id']}")
            click.echo(f"Response: {insight['response']}")

            # Display follow-ups if available
            if "follow_ups" in insight:
                click.echo("\nFollow-up Discussion:")
                for follow_up in insight["follow_ups"]:
                    click.echo(f"Q: {follow_up['follow_up']}")
                    click.echo(f"A: {follow_up['response']}")
                    if "llm_analysis" in follow_up:
                        click.echo(f"Analysis: {follow_up['llm_analysis']}")

            # Display LLM analysis if available
            if "llm_analysis" in insight:
                click.echo(f"\nAnalysis: {insight['llm_analysis']}")

    # Save test results
    test_file = shell.empathy_test.save_test()
    click.echo(f"\nTest results saved to: {test_file}")
    return


@cli.command()
@click.option('--test-id', required=True, help='ID of the test to analyze')
def analyze_test(test_id: str):
    """Analyze a completed empathy test"""
    shell = DhammaShell()

    if not shell.research_mode:
        click.echo("Error: Research mode must be enabled to analyze tests")
        return

    test_file = Path("research_data") / f"{test_id}.json"
    if not test_file.exists():
        click.echo(f"Error: Test file {test_file} not found")
        return

    with open(test_file) as f:
        test_data = json.load(f)

    click.echo(f"\nAnalyzing {test_data['test_type']} test from {test_data['start_time']}")

    # Calculate and display scores
    if "scores" in test_data:
        click.echo("\nScores:")
        for metric, value in test_data["scores"].items():
            click.echo(f"{metric}: {value:.2f}")

    # Display insights and follow-ups
    if "insights" in test_data:
        click.echo("\nInsights:")
        for insight in test_data["insights"]:
            click.echo(f"\nQuestion: {insight['question_id']}")
            click.echo(f"Response: {insight['response']}")

            # Display follow-ups if available
            if "follow_ups" in insight:
                click.echo("\nFollow-up Discussion:")
                for follow_up in insight["follow_ups"]:
                    click.echo(f"Q: {follow_up['follow_up']}")
                    click.echo(f"A: {follow_up['response']}")
                    if "llm_analysis" in follow_up:
                        click.echo(f"Analysis: {follow_up['llm_analysis']}")

            # Display LLM analysis if available
            if "llm_analysis" in insight:
                click.echo(f"\nAnalysis: {insight['llm_analysis']}")


def main():
    """Entry point for the CLI"""
    cli()


if __name__ == "__main__":
    main()
