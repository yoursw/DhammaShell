"""
Configuration management for DhammaShell.
Handles API key storage and retrieval.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from rich.prompt import Prompt, Confirm
from rich.console import Console
from pydantic import BaseModel, Field
import logging
from logging.handlers import RotatingFileHandler

console = Console()

class LoggingConfig(BaseModel):
    """Configuration for logging settings."""
    level: str = Field(default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    max_bytes: int = Field(default=10_000_000, description="Maximum size of log file in bytes")
    backup_count: int = Field(default=5, description="Number of backup log files to keep")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )

class Config:
    """Configuration settings for DhammaShell."""
    def __init__(self):
        """Initialize configuration."""
        self.config_dir = Path.home() / ".dhammashell"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        self._config = self._load_config()
        self._setup_logging()

    def _load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Failed to load config: {str(e)}")
                return {}
        return {}

    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save config: {str(e)}")
            raise

    def _setup_logging(self):
        """Set up logging with the current configuration."""
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

        # Get logging config from file or use defaults
        log_config = self._config.get("logging", {
            "level": "INFO",
            "max_bytes": 10_000_000,
            "backup_count": 5,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        })

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_config["level"])

        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Add file handler with rotation
        file_handler = RotatingFileHandler(
            "logs/dhammashell.log",
            maxBytes=log_config["max_bytes"],
            backupCount=log_config["backup_count"]
        )
        file_handler.setFormatter(logging.Formatter(log_config["format"]))
        root_logger.addHandler(file_handler)

        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_config["format"]))
        root_logger.addHandler(console_handler)

    @property
    def api_key(self) -> Optional[str]:
        """Get the API key."""
        return self._config.get("api_key")

    @api_key.setter
    def api_key(self, value: Optional[str]):
        """Set the API key."""
        if value is None:
            if "api_key" in self._config:
                del self._config["api_key"]
        else:
            self._config["api_key"] = value
        self._save_config()

    def get_research_mode(self) -> bool:
        """Get the research mode setting."""
        return self._config.get("research_mode", False)

    def set_research_mode(self, enabled: bool):
        """Set the research mode setting."""
        self._config["research_mode"] = enabled
        self._save_config()
        status = "enabled" if enabled else "disabled"
        console.print(f"[green]Research mode {status}[/green]")

    def get_logging_config(self) -> LoggingConfig:
        """Get the current logging configuration."""
        return LoggingConfig(**self._config.get("logging", {}))

    def set_logging_config(self, config: LoggingConfig):
        """Set the logging configuration."""
        self._config["logging"] = config.dict()
        self._save_config()
        self._setup_logging()
        console.print("[green]Logging configuration updated[/green]")

    def get_all_settings(self) -> dict:
        """Get all configuration settings."""
        return {
            "api_key": "****" if "api_key" in self._config else None,
            "research_mode": self.get_research_mode(),
            "logging": self.get_logging_config().dict()
        }

    def configure_interactive(self):
        """Interactively configure all settings."""
        console.print("\n[bold cyan]DhammaShell Configuration[/bold cyan]")
        console.print("===========================\n")

        # API Key
        if "api_key" in self._config:
            if Confirm.ask("Do you want to update the API key?"):
                self.api_key = None
                self.api_key = Prompt.ask("Enter your OpenRouter API key")
        else:
            console.print("[yellow]No API key configured[/yellow]")
            self.api_key = Prompt.ask("Enter your OpenRouter API key")

        # Research Mode
        current_research = self.get_research_mode()
        if Confirm.ask(f"Research mode is currently {'enabled' if current_research else 'disabled'}. Do you want to change it?"):
            self.set_research_mode(not current_research)

        # Logging Configuration
        if Confirm.ask("Do you want to configure logging settings?"):
            log_config = self.get_logging_config()

            # Log Level
            level = Prompt.ask(
                "Enter logging level",
                choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                default=log_config.level
            )

            # Max Bytes
            max_bytes = int(Prompt.ask(
                "Enter maximum log file size in bytes",
                default=str(log_config.max_bytes)
            ))

            # Backup Count
            backup_count = int(Prompt.ask(
                "Enter number of backup log files",
                default=str(log_config.backup_count)
            ))

            # Format
            format_str = Prompt.ask(
                "Enter log message format",
                default=log_config.format
            )

            new_config = LoggingConfig(
                level=level,
                max_bytes=max_bytes,
                backup_count=backup_count,
                format=format_str
            )
            self.set_logging_config(new_config)

        console.print("\n[green]Configuration completed![/green]")
        self.display_settings()

    def display_settings(self):
        """Display current configuration settings."""
        settings = self.get_all_settings()
        console.print("\n[bold cyan]Current Configuration:[/bold cyan]")
        console.print("===========================")
        console.print(f"API Key: {'Configured' if settings['api_key'] else 'Not configured'}")
        console.print(f"Research Mode: {'Enabled' if settings['research_mode'] else 'Disabled'}")
        console.print("\n[bold]Logging Configuration:[/bold]")
        for key, value in settings['logging'].items():
            console.print(f"  {key}: {value}")

# Global configuration instance
config = Config()
