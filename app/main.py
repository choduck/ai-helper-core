from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.services.backend_client import backend_client

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="GPT for Team AI 백엔드 API",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 시 실행되는 이벤트 핸들러
    """
    # 필요한 시작 코드 추가
    pass

@app.on_event("shutdown")
async def shutdown_event():
    """
    애플리케이션 종료 시 실행되는 이벤트 핸들러
    """
    # 백엔드 클라이언트 연결 종료
    await backend_client.close()

@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": "0.1.0",
        "message": "AI 헬퍼 코어 서버가 실행 중입니다. /docs에서 API 문서를 확인하세요."
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"} 