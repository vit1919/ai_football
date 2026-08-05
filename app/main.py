import logging
import uvicorn
from fastapi import FastAPI
from pathlib import Path
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.api.routes.matches import router as today_matches_router
from app.api.routes.auth import router as auth
from app.api.routes.predictions import router as predictions_router
from app.api.routes.teams import router as teams
from app.api.routes.leaderboard import router as leaderboard_router
from app.api.routes.llm import router as llm_router
from app.api.routes.standings import router as standings_router
from app.scheduler.scheduler import scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    scheduler.start()
    logger.info("Scheduler started")

    yield

    scheduler.shutdown()

    logger.info("Scheduler stopped")
   

app = FastAPI(title="AI Football Predictor", lifespan=lifespan)
app.include_router(today_matches_router)
app.include_router(auth)
app.include_router(predictions_router)
app.include_router(teams)
app.include_router(leaderboard_router)
app.include_router(llm_router)
app.include_router(standings_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Сервер запущен"}



if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        app_dir=str(project_root),
    )