import base64
import ctypes
import json
import re
import time
from datetime import datetime, timezone

import keyboard
import requests

TOGGL_TOKEN = "3df767905680c056caf8d4fe5d3a550f"
CONTEXTS = {
    "ctrl+alt+b": {"desktop": 4, "workspace_id": 21240307, "project_id": 218671644, "description": "Betong"},
    "ctrl+alt+c": {"desktop": 5, "workspace_id": 21240307, "project_id": 218672926, "description": "C7 Projects"},
    "ctrl+alt+p": {"desktop": 2, "workspace_id": 21240307, "project_id": 218672928, "description": "Processledare"},
    "ctrl+alt+l": {"desktop": 3, "workspace_id": 21240307, "project_id": 218672929, "description": "Leveranskoordinator"},
}
def msgbox(text, title="Toggl Timer"):
    ctypes.windll.user32.MessageBoxW(0, text, title, 0)


def build_auth_header(token: str) -> str:
    raw = f"{token}:api_token".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def toggl_request(method: str, url: str, token: str, body=None):
    headers = {
        "Authorization": build_auth_header(token),
        "Content-Type": "application/json",
    }

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=body if body is not None else None,
        timeout=30,
    )
    return response

def start_timer(token: str, workspace_id: int, project_id: int, description: str) -> bool:
    start_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "created_with": "Python",
        "description": description,
        "workspace_id": workspace_id,
        "project_id": project_id,
        "start": start_iso,
        "duration": -1,
    }
    start_url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/time_entries"
    response = toggl_request("POST", start_url, token, payload)

    if 200 <= response.status_code < 300:
        return True

    msgbox(f"Kunde inte starta timer:\n{response.text}")
    return False
