from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class DocumentBase(BaseModel):
    title: str = Field(..., description="문서 제목")
    description: Optional[str] = Field(None, description="문서 설명")
    category: Optional[str] = Field(None, description="문서 카테고리")

class DocumentCreate(DocumentBase):
    file_path: str = Field(..., description="임시 파일 경로")
    file_type: str = Field(..., description="파일 타입 (pdf, docx, txt, md, html)")
    file_name: str = Field(..., description="원본 파일명")

class DocumentChunk(BaseModel):
    id: str = Field(..., description="청크 ID")
    document_id: str = Field(..., description="소속 문서 ID")
    content: str = Field(..., description="청크 내용")
    metadata: Dict[str, Any] = Field({}, description="청크 메타데이터")

class DocumentResponse(DocumentBase):
    id: str = Field(..., description="문서 ID")
    file_name: str = Field(..., description="파일명")
    file_type: str = Field(..., description="파일 타입")
    chunk_count: int = Field(..., description="문서 청크 수")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")
    is_indexed: bool = Field(..., description="색인 완료 여부")
    uploaded_by: int = Field(..., description="업로더 ID")
    org_id: int = Field(..., description="조직 ID")
    
    class Config:
        orm_mode = True

class DocumentListResponse(BaseModel):
    total: int = Field(..., description="총 문서 수")
    items: List[DocumentResponse] = Field(..., description="문서 목록")

class DocumentFilter(BaseModel):
    category: Optional[str] = Field(None, description="카테고리 필터")
    date_from: Optional[datetime] = Field(None, description="시작 날짜")
    date_to: Optional[datetime] = Field(None, description="종료 날짜")

class DocumentSearchQuery(BaseModel):
    query: str = Field(..., description="검색 쿼리")
    filters: Optional[DocumentFilter] = Field(None, description="필터")
    limit: Optional[int] = Field(5, description="반환할 결과 수")

class DocumentSearchResult(BaseModel):
    id: str = Field(..., description="청크 ID")
    document_id: str = Field(..., description="문서 ID")
    document_title: str = Field(..., description="문서 제목")
    content: str = Field(..., description="청크 내용")
    score: float = Field(..., description="검색 점수")
    metadata: Dict[str, Any] = Field({}, description="메타데이터")

class DocumentSearchResponse(BaseModel):
    results: List[DocumentSearchResult] = Field(..., description="검색 결과")
    query: str = Field(..., description="검색 쿼리")
    total: int = Field(..., description="총 결과 수")
    answer: Optional[str] = Field(None, description="AI 생성 응답 (query 엔드포인트에서만 사용)")
    
class ChunkProcessResult(BaseModel):
    document_id: str
    chunk_count: int
    status: str
    error: Optional[str] = None 