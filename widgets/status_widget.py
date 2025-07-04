#!/usr/bin/env python3
"""
StatusWidget
============

Polls and returns status relevant data from API endpoint:
    • /api/versions

"""

from datetime import datetime, timezone
from dateutil import parser

from widgets.base_widget import APIWidget


def uptime(timestamp: str) -> str:
    try:
        source_time = parser.parse(timestamp)
        if source_time.tzinfo is None:
            source_time = source_time.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - source_time

        days = delta.days
        hours = (delta.seconds // 3600) % 24
        minutes = (delta.seconds // 60) % 60
        seconds = delta.seconds % 60

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")

        return " ".join(parts)
    except Exception:
        return "N/A"


def date_to_human_utc(timestamp: str) -> str:
    try:
        dt = parser.isoparse(timestamp)
        return dt.strftime("%b %-d, %Y %H:%M UTC")
    except (ValueError, TypeError):
        return "N/A"


class StatusWidget(APIWidget):
    """Poll `/api/status` once every 10 s and show a quick summary."""

    interval = 10

    def __init__(self, title: str, *, api_base: str, api_password: str, **kwargs):
        super().__init__(
            title,
            endpoints=f"{api_base}/api/status",
            api_password=api_password,
            **kwargs,
        )

    # ------------------------------------------------------------------ #
    # APIWidget hooks
    # ------------------------------------------------------------------ #
    def extract_data(self, responses):
        payload = responses[self.endpoints[0]]
        return {
            "status": "Running" if payload.get("serviceStatus") == "running" else "Not Running",
            "docker": "Available" if payload.get("dockerAvailable") else "Not Available",
            "autostart": "Enabled" if payload.get("autoStart") else "Not Enabled",
            "uptime": uptime(payload.get("uptime")),
            "image_updates": payload.get("imageUpdates", {}).get("available", "N/A"),
            "last_checked": date_to_human_utc(
                payload.get("imageUpdates", {}).get("lastChecked", "N/A")
            ),
        }

    def render_content(self, data):
        if "error" in data:
            return f"[bold red]{data['error']}[/bold red]"
        return (
            f"Service Status : {data.get('status', 'Loading...')}\n"
            f"Docker Status  : {data.get('docker', 'Loading...')}\n"
            f"Auto-start     : {data.get('autostart', 'Loading...')}\n"
            f"Uptime         : {data.get('uptime', 'Loading...')}\n"
            f"Image Updates  : {data.get('image_updates', 'Loading...')}\n"
            f"Last Checked   : {data.get('last_checked', 'Loading...')}"
        )

