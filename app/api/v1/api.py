from fastapi import APIRouter

from app.api.v1.endpoints import chat, documents, speech, prompts, models

api_router = APIRouter()

# 각 엔드포인트 라우터 등록
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(documents.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(speech.router, prefix="/speech", tags=["speech"])
api_router.include_router(prompts.router, prefix="/prompt-templates", tags=["prompts"])
api_router.include_router(models.router, prefix="/models", tags=["models"]) 