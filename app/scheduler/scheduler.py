from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .jobs.generate_ai_predictions import generate_ai_predictions_job
from .jobs.score_predictions import score_predictions_job
from .jobs.sync_matches import sync_matches_job
from .jobs.sync_standings import sync_standings_job

scheduler = AsyncIOScheduler()

scheduler.add_job(
    sync_matches_job,
    "interval",
    minutes=30,
    id="sync_matches",
    replace_existing=True,
    max_instances=1,
)

scheduler.add_job(
    score_predictions_job,
    "interval",
    minutes=10,
    id="score_predictions",
    replace_existing=True,
    max_instances=1,
)

scheduler.add_job(
    generate_ai_predictions_job,
    "interval",
    minutes=10,
    id="generate_ai_predictions",
    replace_existing=True,
    max_instances=1,
)

scheduler.add_job(
    sync_standings_job,
    "interval",
    minutes=30,
    id="sync_standings",
    replace_existing=True,
    max_instances=1,
)
