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
logger = logging.getLogger(__name__)

class LoggingConfig(BaseModel):
    """Configuration for logging settings."""
    level: str = Field(default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    max_bytes: int = Field(default=10_000_000, description="Maximum size of log file in bytes")
    backup_count: int = Field(default=5, description="Number of backup log files to keep")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )

class AlignmentConfig(BaseModel):
    """Configuration for AI alignment reporting."""
    enabled: bool = Field(default=True, description="Enable AI alignment reporting")
    report_dir: str = Field(default="alignment_reports", description="Directory for alignment reports")
    auto_save: bool = Field(default=True, description="Automatically save reports after each metric")
    risk_threshold: float = Field(default=0.7, description="Threshold for high risk level (0-1)")

class Config(BaseModel):
    """Configuration settings for DhammaShell."""
    api_key: Optional[str] = Field(default=None, description="API key for external services")
    research_enabled: bool = Field(default=False, description="Enable research data collection")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")
    alignment: AlignmentConfig = Field(default_factory=AlignmentConfig, description="AI alignment configuration")
    config_dir: Path = Field(default_factory=lambda: Path.home() / ".dhammashell")
    config_file: Path = Field(default_factory=lambda: Path.home() / ".dhammashell" / "config.json")

    def __init__(self, **data):
        super().__init__(**data)
        self.config_dir.mkdir(exist_ok=True)
        self._load_config()
        self._setup_logging()

    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config_data = json.load(f)
                    # Convert nested dicts back to Pydantic models
                    if "logging" in config_data:
                        self.logging = LoggingConfig(**config_data["logging"])
                    if "alignment" in config_data:
                        self.alignment = AlignmentConfig(**config_data["alignment"])
                    # Update other fields
                    for key, value in config_data.items():
                        if key not in ["logging", "alignment"] and hasattr(self, key):
                            setattr(self, key, value)
            except Exception as e:
                logger.error(f"Failed to load config: {str(e)}")

    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            # Convert Path objects to strings for JSON serialization
            config_dict = self.dict()
            config_dict["config_dir"] = str(config_dict["config_dir"])
            config_dict["config_file"] = str(config_dict["config_file"])

            with open(self.config_file, "w") as f:
                json.dump(config_dict, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")
            raise

    def _setup_logging(self) -> None:
        """Set up logging with the current configuration."""
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.logging.level)

        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Add file handler with rotation
        file_handler = RotatingFileHandler(
            "logs/dhammashell.log",
            maxBytes=self.logging.max_bytes,
            backupCount=self.logging.backup_count
        )
        file_handler.setFormatter(logging.Formatter(self.logging.format))
        root_logger.addHandler(file_handler)

        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(self.logging.format))
        root_logger.addHandler(console_handler)

    def get_api_key(self) -> Optional[str]:
        """Get the API key."""
        if self.api_key:
            return self.api_key

        api_key = Prompt.ask("Enter your API key")
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self._save_config()
        return api_key

    def clear_api_key(self) -> None:
        """Clear the stored API key."""
        if self.api_key:
            self.api_key = None
            self._save_config()
            console.print("[green]API key cleared[/green]")
        else:
            console.print("[yellow]No API key stored[/yellow]")

    def set_research_mode(self, enabled: bool) -> None:
        """Set the research mode setting."""
        self.research_enabled = enabled
        self._save_config()
        status = "enabled" if enabled else "disabled"
        console.print(f"[green]Research mode {status}[/green]")

    def get_research_mode(self) -> bool:
        """Get the current research mode setting.

        Returns:
            bool: True if research mode is enabled, False otherwise
        """
        return self.research_enabled

    def set_alignment_settings(self, enabled: Optional[bool] = None,
                             report_dir: Optional[str] = None,
                             auto_save: Optional[bool] = None,
                             risk_threshold: Optional[float] = None) -> None:
        """Set AI alignment configuration settings.

        Args:
            enabled: Whether alignment reporting is enabled
            report_dir: Directory for alignment reports
            auto_save: Whether to automatically save reports
            risk_threshold: Threshold for high risk level (0-1)
        """
        if enabled is not None:
            self.alignment.enabled = enabled
        if report_dir is not None:
            self.alignment.report_dir = report_dir
        if auto_save is not None:
            self.alignment.auto_save = auto_save
        if risk_threshold is not None:
            if not 0 <= risk_threshold <= 1:
                raise ValueError("Risk threshold must be between 0 and 1")
            self.alignment.risk_threshold = risk_threshold

        self._save_config()
        console.print("[green]Alignment settings updated[/green]")

    def get_all_settings(self) -> dict:
        """Get all configuration settings.

        Returns:
            dict: Current configuration settings
        """
        settings = self.dict()
        # Mask API key for display
        if settings.get("api_key"):
            settings["api_key"] = "****"
        return settings

# Global configuration instance
config = Config()
