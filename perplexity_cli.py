#!/usr/bin/env python3
"""
Perplexity CLI - Interactive command-line interface for Perplexity search.
"""

import sys
from typing import Optional

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

from api import PerplexityAPI
from config import Config
from session import Session


console = Console()


def count_tokens(text: str) -> int:
    """Estimate token count for text."""
    if TIKTOKEN_AVAILABLE:
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception:
            pass
    # Fallback: rough estimate of 4 chars per token
    return len(text) // 4


def get_messages_token_count(messages: list) -> int:
    """Get total token count for messages."""
    return sum(count_tokens(msg.get("content", "")) for msg in messages)


class PerplexityCLI:
    """Main CLI application."""

    COMMANDS = {
        "/new": "Start new conversation",
        "/save": "Save current session",
        "/load": "Load previous session",
        "/clear": "Clear conversation history",
        "/model": "Switch model",
        "/system": "Set system prompt",
        "/sessions": "List saved sessions",
        "/help": "Show available commands",
        "/exit": "Exit the CLI",
    }

    def __init__(self):
        """Initialize the CLI."""
        self.config = Config()
        self.session = Session(self.config.session_dir)
        self.api: Optional[PerplexityAPI] = None

    def initialize_api(self) -> bool:
        """Initialize the API client."""
        try:
            self.api = PerplexityAPI(self.config.api_key)
            return True
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print("[yellow]Set PPLX_API_KEY environment variable to continue.[/yellow]")
            return False

    def show_welcome(self) -> None:
        """Display welcome message."""
        console.print(Panel.fit(
            "[bold blue]Perplexity CLI[/bold blue]\n"
            "Interactive search with real-time AI responses\n\n"
            f"[dim]Model: {self.config.model}[/dim]\n"
            "[dim]Type /help for available commands[/dim]",
            border_style="blue"
        ))

    def show_help(self) -> None:
        """Display available commands."""
        console.print("\n[bold]Available Commands:[/bold]")
        for cmd, desc in self.COMMANDS.items():
            console.print(f"  [cyan]{cmd}[/cyan] - {desc}")
        console.print()

    def handle_command(self, command: str) -> bool:
        """
        Handle a slash command.

        Returns:
            False if should exit, True otherwise.
        """
        cmd = command.lower().strip()

        if cmd == "/exit":
            if self.config.auto_save and self.session.messages:
                filename = self.session.save()
                console.print(f"[green]Session auto-saved to {filename}[/green]")
            console.print("[dim]Goodbye![/dim]")
            return False

        elif cmd == "/help":
            self.show_help()

        elif cmd == "/new":
            self.session.clear()
            console.print("[green]Started new conversation.[/green]")

        elif cmd == "/clear":
            self.session.clear()
            console.print("[green]Conversation history cleared.[/green]")

        elif cmd == "/save":
            name = inquirer.text(
                message="Session name (leave empty for timestamp):",
            ).execute()
            filename = self.session.save(name if name else None)
            console.print(f"[green]Session saved to {filename}[/green]")

        elif cmd == "/load":
            sessions = self.session.list_sessions()
            if not sessions:
                console.print("[yellow]No saved sessions found.[/yellow]")
            else:
                choices = [
                    Choice(
                        value=s["filename"],
                        name=f"{s['filename']} ({s['message_count']} messages) - {s['preview']}"
                    )
                    for s in sessions
                ]
                selected = inquirer.select(
                    message="Select session to load:",
                    choices=choices,
                ).execute()
                if self.session.load(selected):
                    console.print(f"[green]Loaded session: {selected}[/green]")
                else:
                    console.print(f"[red]Failed to load session: {selected}[/red]")

        elif cmd == "/sessions":
            sessions = self.session.list_sessions()
            if not sessions:
                console.print("[yellow]No saved sessions found.[/yellow]")
            else:
                console.print("\n[bold]Saved Sessions:[/bold]")
                for s in sessions:
                    console.print(
                        f"  [cyan]{s['filename']}[/cyan] - "
                        f"{s['message_count']} messages - "
                        f"[dim]{s['preview']}[/dim]"
                    )
                console.print()

        elif cmd == "/model":
            choices = [
                Choice(value=m, name=m)
                for m in PerplexityAPI.AVAILABLE_MODELS
            ]
            selected = inquirer.select(
                message="Select model:",
                choices=choices,
                default=self.config.model,
            ).execute()
            self.config.model = selected
            self.session.model = selected
            console.print(f"[green]Model switched to {selected}[/green]")

        elif cmd == "/system":
            prompt = inquirer.text(
                message="Enter system prompt:",
                default=self.config.system_prompt,
            ).execute()
            self.config.system_prompt = prompt
            console.print("[green]System prompt updated.[/green]")

        else:
            console.print(f"[yellow]Unknown command: {cmd}[/yellow]")
            console.print("[dim]Type /help for available commands.[/dim]")

        return True

    def summarize_if_needed(self) -> None:
        """Summarize conversation if approaching token limit."""
        messages = self.session.get_messages()
        token_count = get_messages_token_count(messages)

        if token_count > self.config.input_token_limit and len(messages) > 4:
            console.print("[dim]Summarizing conversation to manage context...[/dim]")
            
            # Keep last 2 exchanges, summarize the rest
            to_summarize = messages[:-4]
            to_keep = messages[-4:]
            
            summary_text = "\n".join(
                f"{m['role']}: {m['content']}" for m in to_summarize
            )
            
            try:
                summary = self.api.summarize(summary_text, self.config.model)
                
                # Replace messages with summary + recent
                self.session.clear()
                self.session.add_message("system", f"Previous conversation summary: {summary}")
                for msg in to_keep:
                    self.session.add_message(msg["role"], msg["content"])
                    
                console.print("[dim]Context summarized successfully.[/dim]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not summarize: {e}[/yellow]")

    def chat(self, user_input: str) -> None:
        """Process a chat message."""
        self.summarize_if_needed()

        # Build messages with system prompt
        messages = [{"role": "system", "content": self.config.system_prompt}]
        messages.extend(self.session.get_messages())
        messages.append({"role": "user", "content": user_input})

        # Add user message to session
        self.session.add_message("user", user_input)

        try:
            console.print()
            full_response = ""
            
            with Live(console=console, refresh_per_second=10) as live:
                for chunk in self.api.chat(messages, model=self.config.model, stream=True):
                    full_response += chunk
                    live.update(Markdown(full_response))

            # Add assistant response to session
            self.session.add_message("assistant", full_response)
            console.print()

        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")

    def run(self) -> int:
        """Run the main CLI loop."""
        if not self.initialize_api():
            return 1

        self.show_welcome()

        try:
            while True:
                try:
                    user_input = inquirer.text(
                        message="",
                        qmark="❯",
                        amark="❯",
                    ).execute()

                    if not user_input:
                        continue

                    user_input = user_input.strip()

                    if user_input.startswith("/"):
                        if not self.handle_command(user_input):
                            break
                    else:
                        self.chat(user_input)

                except KeyboardInterrupt:
                    console.print("\n[dim]Use /exit to quit.[/dim]")

        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/dim]")

        return 0


def main():
    """Main entry point."""
    cli = PerplexityCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
