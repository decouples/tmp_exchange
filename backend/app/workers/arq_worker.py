"""Arq worker entry point.

Run:
    uv run arq app.workers.arq_worker.WorkerSettings
"""
from __future__ import annotations

from arq.connections import RedisSettings

from app.core.config import settings
from app.core.logging import setup_logging
from app.workers.queues import DEFAULT
from app.workers.tasks.merge_task import merge_results
from app.workers.tasks.ocr_task import run_ocr
from app.workers.tasks.pdf_split_task import split_pdf


async def startup(ctx: dict) -> None:
    setup_logging()


async def shutdown(ctx: dict) -> None:
    pass


class WorkerSettings:
    functions = [run_ocr, split_pdf, merge_results]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    queue_name = DEFAULT
    max_jobs = 4
    job_timeout = settings.vlm_timeout_s * 2
    max_tries = 3
    keep_result = 3600
