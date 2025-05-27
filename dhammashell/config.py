"""
Configuration management for DhammaShell.
Handles API key storage and retrieval.
"""

import os
import json
from pathlib import Path
from typing import Optional
from rich.prompt import Prompt
from rich.console import Console

console = Console()

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
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {str(e)}")
                return {}
        return {}

    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")
            raise

    def get_api_key(self) -> Optional[str]:
        """Get the OpenRouter API key."""
        if 'api_key' in self._config:
            return self._config['api_key']

        api_key = Prompt.ask("Enter your OpenRouter API key")
        if not api_key:
            raise ValueError("API key is required")

        self._config['api_key'] = api_key
        self._save_config()
        return api_key

    def clear_api_key(self):
        """Clear the stored API key."""
        if 'api_key' in self._config:
            del self._config['api_key']
            self._save_config()
            console.print("[green]API key cleared[/green]")
        else:
            console.print("[yellow]No API key stored[/yellow]")

    def get_research_mode(self) -> bool:
        """Get the research mode setting."""
        return self._config.get('research_mode', False)

    def set_research_mode(self, enabled: bool):
        """Set the research mode setting."""
        self._config['research_mode'] = enabled
        self._save_config()
        status = "enabled" if enabled else "disabled"
        console.print(f"[green]Research mode {status}[/green]")

    def get_all_settings(self) -> dict:
        """Get all configuration settings.

        Returns:
            dict: Current configuration settings
        """
        settings = {
            'api_key': '****' if 'api_key' in self._config else None,
            'research_mode': self.get_research_mode()
        }
        return settings