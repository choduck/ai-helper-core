from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 기본 설정 가져오기
DEFAULT_MODEL = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o")
DEFAULT_TEMPERATURE = float(os.getenv("OPENAI_DEFAULT_TEMPERATURE", "0.7"))
DEFAULT_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "4096")) if os.getenv("OPENAI_MAX_TOKENS") else None
DEFAULT_STREAM = os.getenv("OPENAI_STREAM", "False").lower() == "true"

class ChatMessage(BaseModel):
    role: str = Field(..., description="메시지 역할 (system, user, assistant)")
    content: str = Field(..., description="메시지 내용")

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="대화 메시지 리스트")
    model: Optional[str] = Field(DEFAULT_MODEL, description=f"사용할 모델 (기본값: {DEFAULT_MODEL})")
    temperature: Optional[float] = Field(DEFAULT_TEMPERATURE, description="응답 온도 (높을수록 창의적)")
    max_tokens: Optional[int] = Field(DEFAULT_MAX_TOKENS, description="최대 토큰 수")
    stream: Optional[bool] = Field(DEFAULT_STREAM, description="스트리밍 여부")

class ChatUsage(BaseModel):
    prompt_tokens: int = Field(..., description="입력 메시지 토큰 수")
    completion_tokens: int = Field(..., description="응답 메시지 토큰 수")
    total_tokens: int = Field(..., description="총 사용 토큰 수")
    estimated_cost: float = Field(..., description="예상 비용 (USD)")

class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None

class ChatResponse(BaseModel):
    id: str = Field(..., description="응답 식별자")
    object: str = Field("chat.completion", description="응답 객체 타입")
    created: int = Field(..., description="응답 생성 시간 (유닉스 타임스탬프)")
    model: str = Field(..., description="사용된 모델")
    choices: List[ChatChoice] = Field(..., description="응답 선택지 목록")
    usage: ChatUsage = Field(..., description="토큰 사용량 정보")

class SourceDocument(BaseModel):
    id: str = Field(..., description="문서 ID")
    title: str = Field(..., description="문서 제목")
    content: str = Field(..., description="관련 문서 내용")
    relevance_score: float = Field(..., description="관련성 점수")
    metadata: Dict[str, Any] = Field({}, description="문서 메타데이터")

class ChatWithContextResponse(ChatResponse):
    sources: List[SourceDocument] = Field(..., description="참조된 소스 문서 목록") 