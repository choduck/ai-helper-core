from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str = Field(..., description="메시지 역할 (system, user, assistant)")
    content: str = Field(..., description="메시지 내용")

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="대화 메시지 리스트")
    model: Optional[str] = Field(None, description="사용할 모델 (기본값: GPT-3.5)")
    temperature: Optional[float] = Field(0.7, description="응답 온도 (높을수록 창의적)")
    max_tokens: Optional[int] = Field(None, description="최대 토큰 수")
    stream: Optional[bool] = Field(False, description="스트리밍 여부")

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