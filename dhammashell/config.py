"""
Configuration management for DhammaShell.
Handles API key storage and retrieval.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from rich.prompt import Prompt
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

class Config(BaseModel):
    """Configuration settings for DhammaShell."""
    api_key: Optional[str] = Field(default=None, description="API key for external services")
    research_enabled: bool = Field(default=False, description="Enable research data collection")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            api_key=os.getenv("DHAMMASHELL_API_KEY"),
            research_enabled=os.getenv("DHAMMASHELL_RESEARCH_ENABLED", "false").lower() == "true",
            logging=LoggingConfig(
                level=os.getenv("DHAMMASHELL_LOG_LEVEL", "INFO"),
                max_bytes=int(os.getenv("DHAMMASHELL_LOG_MAX_BYTES", "10000000")),
                backup_count=int(os.getenv("DHAMMASHELL_LOG_BACKUP_COUNT", "5")),
                format=os.getenv(
                    "DHAMMASHELL_LOG_FORMAT",
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
        )

def setup_logging(config: LoggingConfig) -> None:
    """Set up logging with the given configuration."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(config.level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add file handler with rotation
    file_handler = RotatingFileHandler(
        "logs/dhammashell.log",
        maxBytes=config.max_bytes,
        backupCount=config.backup_count
    )
    file_handler.setFormatter(logging.Formatter(config.format))
    root_logger.addHandler(file_handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(config.format))
    root_logger.addHandler(console_handler)

# Global configuration instance
config = Config.load()

# Set up logging
setup_logging(config.logging)

class Config:
    def __init__(self):
        """Initialize configuration."""
        self.config_dir = Path.home() / ".dhammashell"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {str(e)}")
                return {}
        return {}

    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")
            raise

    def get_api_key(self) -> Optional[str]:
        """Get the OpenRouter API key."""
        if "api_key" in self._config:
            return self._config["api_key"]

        api_key = Prompt.ask("Enter your OpenRouter API key")
        if not api_key:
            raise ValueError("API key is required")

        self._config["api_key"] = api_key
        self._save_config()
        return api_key

    def clear_api_key(self):
        """Clear the stored API key."""
        if "api_key" in self._config:
            del self._config["api_key"]
            self._save_config()
            console.print("[green]API key cleared[/green]")
        else:
            console.print("[yellow]No API key stored[/yellow]")

    def get_research_mode(self) -> bool:
        """Get the research mode setting."""
        return self._config.get("research_mode", False)

    def set_research_mode(self, enabled: bool):
        """Set the research mode setting."""
        self._config["research_mode"] = enabled
        self._save_config()
        status = "enabled" if enabled else "disabled"
        console.print(f"[green]Research mode {status}[/green]")

    def get_all_settings(self) -> dict:
        """Get all configuration settings.

        Returns:
            dict: Current configuration settings
        """
        settings = {
            "api_key": "****" if "api_key" in self._config else None,
            "research_mode": self.get_research_mode(),
        }
        return settings
