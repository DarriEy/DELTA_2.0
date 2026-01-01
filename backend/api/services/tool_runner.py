from typing import List, Dict, Any, Optional
try:
    from fastapi import BackgroundTasks
except ImportError:  # pragma: no cover - optional dependency for tests
    class BackgroundTasks:  # type: ignore[no-redef]
        pass
from sqlalchemy.orm import Session

from utils.db import get_session_local
from .job_service import get_job_service


def run_tools(
    db: Optional[Session],
    background_tasks: Optional[BackgroundTasks],
    function_calls: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []

    for call in function_calls:
        name = call.get("name")
        args = call.get("args", {}) or {}

        if name == "run_model":
            if not db:
                results.append(
                    {"name": name, "result": "Database required for modeling jobs. Please try again when the system is fully online."}
                )
                continue

            if not background_tasks:
                results.append(
                    {"name": name, "result": "Background tasks not available to start job."}
                )
                continue

            session_factory = get_session_local()
            if not session_factory:
                results.append(
                    {"name": name, "result": "Database session not available for job creation."}
                )
                continue

            try:
                job = get_job_service().create_modeling_job(
                    db,
                    {"model": args.get("model"), "job_type": "SIMULATION"},
                    background_tasks,
                    session_factory,
                )
                results.append(
                    {
                        "name": name,
                        "result": (
                            "Model run initiated successfully. "
                            f"Job ID: {job.id}. You can check status later."
                        ),
                    }
                )
            except Exception as exc:
                results.append({"name": name, "result": f"Failed to start model run: {exc}"})
        else:
            results.append({"name": name or "unknown", "result": f"Unknown tool: {name}"})

    return results
