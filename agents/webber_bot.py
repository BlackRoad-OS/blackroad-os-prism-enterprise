"""Webber: Web Editor Bot for HTML, CSS, JS, JSON, and config files.

- Formats and validates web files.
- Performs bulk edits (e.g., accessibility, footer, search/replace).
- Can be triggered on PRs, issues, or CLI.
- Posts status/errors to Slack (via NotificationBot) and updates AGENT_WORKBOARD.md.
"""

from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Optional

from agents.notification_bot import NotificationBot


@dataclass
class WebberBot:
    """Edit and validate web files, notifying on actions."""

    root_dir: str = field(default_factory=lambda: os.getcwd())
    notification_bot: Optional[NotificationBot] = None

    def _run_prettier(self, file_path: str) -> bool:
        """Run prettier on ``file_path`` and raise on failure."""
        try:
            subprocess.run(["prettier", "--write", file_path], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise RuntimeError(f"Prettier failed for {file_path}: {exc}") from exc
        return True

    def format_html(self, file_path: str) -> bool:
        """Format an HTML file using Prettier."""
        return self._run_prettier(file_path)

    def format_css(self, file_path: str) -> bool:
        """Format a CSS file using Prettier."""
        return self._run_prettier(file_path)

    def format_js(self, file_path: str) -> bool:
        """Format a JavaScript file using Prettier."""
        return self._run_prettier(file_path)

    def validate_json(self, file_path: str) -> bool:
        """Validate a JSON file, raising on failure."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)
        except Exception as exc:  # pylint: disable=broad-except
            raise ValueError(f"JSON validation failed for {file_path}: {exc}") from exc
        return True

    def bulk_edit_html(self, search: str, replace: str) -> None:
        """Replace ``search`` with ``replace`` in all HTML files under ``root_dir``."""
        for dirpath, _, filenames in os.walk(self.root_dir):
            for fname in filenames:
                if fname.endswith(".html"):
                    path = os.path.join(dirpath, fname)
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    new_content = content.replace(search, replace)
                    if new_content != content:
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        self.notify(f"Edited {path}")

    def update_config(self, config_path: str, updates: dict) -> None:
        """Update a JSON config file with provided ``updates``."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data.update(updates)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.notify(f"Updated config {config_path}")
        except Exception as exc:  # pylint: disable=broad-except
            self.notify(f"Failed to update config {config_path}: {exc}")

    def notify(self, message: str) -> None:
        """Send a notification via NotificationBot if configured."""
        if self.notification_bot:
            self.notification_bot.send(message)
        print(message)

    def _suffix_handlers(self) -> dict[str, Callable[[str], bool]]:
        """Return mapping of file suffixes to handler methods."""
        return {
            ".html": self.format_html,
            ".css": self.format_css,
            ".js": self.format_js,
            ".json": self.validate_json,
        }

    def run_on_pr(self, files: list[str]) -> None:
        """Process ``files`` based on their extension."""
        handlers = self._suffix_handlers()
        for file_path in files:
            handler = None
            for suffix, suffix_handler in handlers.items():
                if file_path.endswith(suffix):
                    handler = suffix_handler
                    break

            if handler is None:
                continue

            try:
                result = handler(file_path)
            except Exception as exc:  # pylint: disable=broad-except
                self.notify(f"Error processing {file_path}: {exc}")
                continue

            if result is False:
                self.notify(f"Processing failed for {file_path}")
                continue

            self.notify(f"Processed {file_path} successfully")


if __name__ == "__main__":
    webber = WebberBot(notification_bot=NotificationBot())
    print("WebberBot is ready to edit web files and send notifications.")
