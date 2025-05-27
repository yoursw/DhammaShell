"""
Command-line interface for DharmaShell.
"""

import click
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from .config import config
from .middleseek.core import MiddleSeekCore, MiddleSeek
from .middleseek.alignment import SystemHealth, AlignmentAuditor

@click.group()
def cli():
    """DharmaShell CLI - A mindful AI assistant."""
    pass

@cli.command()
@click.option('--api-key', help='OpenRouter API key')
@click.option('--interactive', is_flag=True, help='Configure settings interactively')
def configure(api_key: Optional[str] = None, interactive: bool = False):
    """Configure DharmaShell settings."""
    if interactive:
        config.configure_interactive()
    elif api_key:
        config.api_key = api_key
        click.echo("API key configured successfully.")
    else:
        config.display_settings()

@cli.command()
@click.argument('message')
@click.option('--compassion', default=3, help='Compassion score (0-5)')
def chat(message: str, compassion: int):
    """Chat with DharmaShell."""
    try:
        if not config.api_key:
            click.echo("Error: API key not configured. Please run 'ds configure' first.")
            return
        core = MiddleSeekCore(config.api_key)
        response = core.generate_response(message, compassion)
        click.echo(response)
    except Exception as e:
        click.echo(f"Error: {str(e)}")

@cli.group()
def audit():
    """Audit system health and alignment."""
    pass

@audit.command()
@click.option('--time-window', type=int, help='Time window in hours for analysis')
def alignment(time_window: Optional[int] = None):
    """Analyze AI alignment metrics."""
    try:
        if not config.api_key:
            click.echo("Error: API key not configured. Please run 'ds configure' first.")
            return
        core = MiddleSeekCore(config.api_key)
        window = timedelta(hours=time_window) if time_window else None
        report = core.get_alignment_report(window)
        click.echo(report)
    except Exception as e:
        click.echo(f"Error: {str(e)}")

@audit.command()
def health():
    """Check system health."""
    try:
        health = SystemHealth()
        is_healthy, message = health.check_health()
        click.echo(f"System Health: {'Healthy' if is_healthy else 'Unhealthy'}")
        click.echo(f"Status: {message}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")

def main():
    """Main entry point for the CLI."""
    cli()

if __name__ == '__main__':
    main()
