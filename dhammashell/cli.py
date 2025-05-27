"""
DhammaShell Command Line Interface
"""

import click
from pathlib import Path
from typing import Optional
import json
from datetime import datetime
from .empathy_research import EmpathyAnalyzer, ResearchDataCollector, EmpathyMetrics, ResearchReport, AuditReport

@click.group()
def cli():
    """DhammaShell - A mindful terminal chat tool"""
    pass

@cli.command(name='research-report')
@click.option('--session-id', help='Session ID to analyze')
@click.option('--output-format', type=click.Choice(['text', 'json']), default='text', help='Output format')
@click.option('--no-visualizations', is_flag=True, help='Disable visualization generation')
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
            include_visualizations=not no_visualizations
        )
        
        if output_format == 'text':
            click.echo(report)
        else:
            # Save JSON report to file
            output_file = Path(f"research_report_{session_data['session_id']}.json")
            output_file.write_text(report)
            click.echo(f"JSON report saved to {output_file}")
            
    except Exception as e:
        click.echo(f"Error generating research report: {str(e)}", err=True)

@cli.command()
def chat():
    """Start an interactive chat session"""
    # ... existing chat implementation ...

@cli.command(name='audit')
@click.option('--session-id', help='Session ID to audit')
@click.option('--confidence', default=0.99999, help='Required confidence level (default: 99.999%)')
@click.option('--sigma', default=6, help='Required sigma level (default: 6)')
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
            session_data=session_data,
            confidence_level=confidence,
            sigma_level=sigma
        )
        
        click.echo(report)
        
    except Exception as e:
        click.echo(f"Error generating audit report: {str(e)}", err=True)

def main():
    """Entry point for the CLI"""
    cli()

if __name__ == '__main__':
    main() 