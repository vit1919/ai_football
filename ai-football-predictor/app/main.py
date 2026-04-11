
import uvicorn
from fastapi import FastAPI
from pathlib import Path
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.api.routes.today_mathes import router as today_matches_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
   

app = FastAPI(title="AI Football Predictor", lifespan=lifespan)
app.include_router(today_matches_router)


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