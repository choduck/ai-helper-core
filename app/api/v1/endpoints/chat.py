from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from app.services.chat import ChatService
from app.services.auth import get_current_user, User


router = APIRouter()

@router.post("/completions", response_model=ChatResponse)
async def create_chat_completion(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    대화 메시지를 받아 AI의 응답을 반환합니다.
    """
    try:
        chat_service = ChatService()
        response = await chat_service.generate_completion(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            user_id=current_user.user_id,
            org_id=current_user.org_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def create_chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    """
    대화 메시지를 받아 AI의 응답을 스트리밍으로 반환합니다.
    """
    try:
        chat_service = ChatService()
        return StreamingResponse(
            chat_service.generate_stream(
                messages=request.messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                user_id=current_user.user_id,
                org_id=current_user.org_id
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/with-context", response_model=ChatResponse)
async def create_chat_with_context(
    request: ChatRequest, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    대화 메시지와 함께 관련 문서 컨텍스트를 찾아 AI 응답을 생성합니다. (RAG)
    """
    try:
        chat_service = ChatService()
        response = await chat_service.generate_with_context(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            user_id=current_user.user_id,
            org_id=current_user.org_id,
            background_tasks=background_tasks
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 