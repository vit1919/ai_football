import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db
from schemas.llm_schema import AIPredictionResponse, LLMModelRead, LLMStatsResponse, LLMVsUserStatsResponse
from services.ai_prediction_service import generate_ai_prediction
from services.llm_stats_service import get_llm_stats, get_llm_vs_user_stats
from services.match_service import get_match_by_id
from app.core.config import settings
from app.core.constants import AVAILABLE_LLM_MODELS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/models", response_model=list[LLMModelRead])
async def list_models() -> list[LLMModelRead]:
    return [LLMModelRead(**m) for m in AVAILABLE_LLM_MODELS]


@router.post("/generate/{match_id}", response_model=AIPredictionResponse)
async def generate_for_match(
    match_id: int,
    model: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    match = await get_match_by_id(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.completed:
        raise HTTPException(status_code=400, detail="Match already completed")

    try:
        prediction = await generate_ai_prediction(db, match, model)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error("LLM prediction failed for match %s: %s", match_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail="LLM prediction failed")

    return AIPredictionResponse(
        match_id=prediction.match_id,
        model_name=prediction.model_name or settings.llm_default_model,
        score_home=prediction.score_home,
        score_away=prediction.score_away,
        predicted_result=prediction.predicted_result.value,
        confidence=prediction.confidence,
    )


@router.get("/stats", response_model=LLMStatsResponse)
async def llm_stats(db: AsyncSession = Depends(get_db)):
    return await get_llm_stats(db)


@router.get("/stats/vs-user", response_model=LLMVsUserStatsResponse)
async def llm_vs_user_stats(db: AsyncSession = Depends(get_db)):
    return await get_llm_vs_user_stats(db)
