from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .jobs.sync_matches import sync_matches_job
from .jobs.score_predictions import score_predictions_job

scheduler = AsyncIOScheduler()

scheduler.add_job(
    sync_matches_job,
    "interval",
    minutes=30,
    id="sync_matches",
    replace_existing=True,
)

scheduler.add_job(
    score_predictions_job,
    "interval",
    minutes=10,
    id="score_predictions",
    replace_existing=True,
)