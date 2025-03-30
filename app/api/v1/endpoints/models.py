from typing import Any, List, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.services.auth import get_current_user, User
from app.core.config import settings

router = APIRouter()

class ModelInfo(BaseModel):
    id: str = Field(..., description="모델 ID")
    name: str = Field(..., description="모델 이름")
    description: str = Field(..., description="모델 설명")
    max_tokens: int = Field(..., description="최대 토큰 수")
    pricing: Dict[str, float] = Field(..., description="가격 정보 (USD/1K 토큰)")
    capabilities: List[str] = Field(..., description="모델 기능")

@router.get("", response_model=List[ModelInfo])
async def list_models(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    사용 가능한 모델 목록을 반환합니다.
    """
    # 현재는 샘플 데이터 반환
    available_models = [
        {
            "id": "gpt-4",
            "name": "GPT-4",
            "description": "OpenAI의 가장 강력한 LLM 모델",
            "max_tokens": 8192,
            "pricing": {
                "prompt": 0.03,
                "completion": 0.06
            },
            "capabilities": ["chat", "reasoning", "coding", "creative"]
        },
        {
            "id": "gpt-4-32k",
            "name": "GPT-4 (32K)",
            "description": "확장된 컨텍스트 윈도우를 가진 GPT-4",
            "max_tokens": 32768,
            "pricing": {
                "prompt": 0.06,
                "completion": 0.12
            },
            "capabilities": ["chat", "reasoning", "coding", "creative", "long_context"]
        },
        {
            "id": "gpt-3.5-turbo",
            "name": "GPT-3.5 Turbo",
            "description": "성능과 속도에 최적화된 효율적인 모델",
            "max_tokens": 4096,
            "pricing": {
                "prompt": 0.0015,
                "completion": 0.002
            },
            "capabilities": ["chat", "coding", "creative"]
        },
        {
            "id": "gpt-3.5-turbo-16k",
            "name": "GPT-3.5 Turbo (16K)",
            "description": "확장된 컨텍스트 윈도우를 가진 GPT-3.5 Turbo",
            "max_tokens": 16384,
            "pricing": {
                "prompt": 0.003,
                "completion": 0.004
            },
            "capabilities": ["chat", "coding", "creative", "long_context"]
        }
    ]
    
    # 기본 모델 설정
    default_model = settings.DEFAULT_MODEL
    
    # 기본 모델을 목록 맨 앞에 배치
    reordered_models = []
    for model in available_models:
        if model["id"] == default_model:
            reordered_models.insert(0, model)
        else:
            reordered_models.append(model)
    
    return reordered_models

@router.get("/default", response_model=ModelInfo)
async def get_default_model(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    기본 모델 정보를 반환합니다.
    """
    default_model = settings.DEFAULT_MODEL
    
    # 사용 가능한 모델 중 기본 모델 찾기
    model_info = {
        "gpt-4": {
            "id": "gpt-4",
            "name": "GPT-4",
            "description": "OpenAI의 가장 강력한 LLM 모델",
            "max_tokens": 8192,
            "pricing": {
                "prompt": 0.03,
                "completion": 0.06
            },
            "capabilities": ["chat", "reasoning", "coding", "creative"]
        },
        "gpt-3.5-turbo": {
            "id": "gpt-3.5-turbo",
            "name": "GPT-3.5 Turbo",
            "description": "성능과 속도에 최적화된 효율적인 모델",
            "max_tokens": 4096,
            "pricing": {
                "prompt": 0.0015,
                "completion": 0.002
            },
            "capabilities": ["chat", "coding", "creative"]
        }
    }
    
    # 모델 정보 반환
    return model_info.get(default_model, model_info["gpt-3.5-turbo"]) 