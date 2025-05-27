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
        self.config_dir = Path.home() / ".dhammashell"
        self.config_file = self.config_dir / "config.json"
        self.api_key: Optional[str] = None

    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key')
            except (json.JSONDecodeError, IOError) as e:
                console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")
                self.api_key = None

    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump({'api_key': self.api_key}, f)
        except IOError as e:
            console.print(f"[red]Error: Could not save config: {e}[/red]")

    def get_api_key(self) -> Optional[str]:
        """Get the API key, prompting for it if not set."""
        # First try to load from config
        self._load_config()
        
        if not self.api_key:
            console.print("\n[bold cyan]DhammaShell Configuration[/bold cyan]")
            console.print("To use MiddleSeek protocol, you need an OpenRouter API key.")
            console.print("Get your key at: [link=https://openrouter.ai/keys]https://openrouter.ai/keys[/link]")
            
            api_key = Prompt.ask(
                "\nEnter your OpenRouter API key",
                password=True
            )
            
            if api_key:
                self.api_key = api_key
                self._save_config()
                console.print("[green]API key saved successfully![/green]")
            else:
                console.print("[yellow]No API key provided. Some features may be limited.[/yellow]")
        
        return self.api_key

    def clear_api_key(self) -> None:
        """Clear the stored API key."""
        self.api_key = None
        if self.config_file.exists():
            try:
                self.config_file.unlink()
                console.print("[green]API key cleared successfully![/green]")
            except IOError as e:
                console.print(f"[red]Error clearing API key: {e}[/red]") 