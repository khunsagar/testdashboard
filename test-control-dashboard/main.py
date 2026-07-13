"""
Test Automation Control Plane — Dashboard (Phase 1, NiceGUI).

A thin UI over the backend's executions API: trigger a run, watch the
list update. No auth yet (matches backend Phase 2 auth being unimplemented).
Point BACKEND_URL at wherever the FastAPI backend is running.
"""

import os

import httpx
from nicegui import ui

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

columns = [
    {"name": "id", "label": "ID", "field": "id", "align": "left"},
    {"name": "branch", "label": "Branch", "field": "branch", "align": "left"},
    {"name": "test_type", "label": "Test Type", "field": "test_type", "align": "left"},
    {"name": "status", "label": "Status", "field": "status", "align": "left"},
    {"name": "result", "label": "Result", "field": "result", "align": "left"},
    {"name": "created_at", "label": "Created At", "field": "created_at", "align": "left"},
]


def fetch_executions() -> list[dict]:
    try:
        response = httpx.get(f"{BACKEND_URL}/api/v1/executions/", timeout=5)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        ui.notify(f"Failed to load executions: {exc}", type="negative")
        return []


def start_execution(branch: str, event: str, trigger_type: str) -> None:
    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/v1/executions/start",
            json={"branch": branch, "event": event, "trigger_type": trigger_type},
            timeout=5,
        )
        response.raise_for_status()
        ui.notify("Execution started", type="positive")
    except httpx.HTTPError as exc:
        ui.notify(f"Failed to start execution: {exc}", type="negative")


@ui.page("/")
def index() -> None:
    ui.label("Test Automation Control Plane").classes("text-2xl font-bold")

    with ui.card():
        ui.label("Start a new execution").classes("text-lg font-semibold")
        with ui.row():
            branch_input = ui.input("Branch", value="main")
            event_select = ui.select(["push", "pull_request", "schedule"], value="push", label="Event")
            trigger_select = ui.select(
                ["manual", "github_action", "schedule"], value="manual", label="Trigger Type"
            )
            start_button = ui.button("Start")

    with ui.card().classes("w-full"):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label("Executions").classes("text-lg font-semibold")
            refresh_button = ui.button("Refresh", icon="refresh")
        table = ui.table(columns=columns, rows=fetch_executions(), row_key="id").classes("w-full")

    def refresh_table() -> None:
        table.rows = fetch_executions()

    def on_start() -> None:
        start_execution(branch_input.value, event_select.value, trigger_select.value)
        refresh_table()

    start_button.on_click(on_start)
    refresh_button.on_click(refresh_table)
    ui.timer(5.0, refresh_table)


ui.run(title="Test Control Dashboard", port=8080)
