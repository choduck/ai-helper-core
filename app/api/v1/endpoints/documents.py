from typing import Any, List, Optional
import os
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Query
from pydantic import BaseModel

from app.schemas.document import (
    DocumentCreate, DocumentResponse, DocumentSearchQuery, 
    DocumentSearchResponse, DocumentListResponse
)
from app.services.document import DocumentService
from app.services.auth import get_current_user, User

router = APIRouter()

@router.post("/documents", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    지식 베이스용 문서를 업로드합니다.
    """
    try:
        # 파일 확장자 검증
        file_ext = os.path.splitext(file.filename)[1].lower()
        supported_formats = [".pdf", ".docx", ".txt", ".md", ".html"]
        
        if not any(file_ext.endswith(fmt) for fmt in supported_formats):
            raise HTTPException(
                status_code=400, 
                detail=f"지원되지 않는 파일 형식입니다. 지원: {', '.join(supported_formats)}"
            )
        
        # 임시 파일로 저장
        temp_file_path = f"temp_{uuid4()}{file_ext}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 문서 생성 요청 준비
        doc_create = DocumentCreate(
            title=title,
            description=description,
            category=category,
            file_path=temp_file_path,
            file_type=file_ext[1:],
            file_name=file.filename
        )
        
        # 문서 서비스 호출
        doc_service = DocumentService()
        result = await doc_service.create_document(
            doc_create=doc_create,
            user_id=current_user.user_id,
            org_id=current_user.org_id,
            background_tasks=background_tasks
        )
        
        return result
    
    except Exception as e:
        # 에러 발생시 임시 파일 정리 시도
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    지식 베이스 문서 목록을 반환합니다.
    """
    try:
        doc_service = DocumentService()
        return await doc_service.get_documents(
            org_id=current_user.org_id,
            skip=skip,
            limit=limit,
            category=category
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(
    query: DocumentSearchQuery,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    벡터 DB를 사용하여 질문과 가장 관련 있는 문서 청크를 검색합니다.
    """
    try:
        doc_service = DocumentService()
        return await doc_service.search_documents(
            query=query.query,
            org_id=current_user.org_id,
            filters=query.filters,
            limit=query.limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=DocumentSearchResponse)
async def query_documents(
    query: DocumentSearchQuery,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    질문에 대한 RAG 기반 응답을 생성합니다.
    """
    try:
        doc_service = DocumentService()
        return await doc_service.query_documents(
            query=query.query,
            org_id=current_user.org_id,
            filters=query.filters
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}", response_model=dict)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    지식 베이스 문서를 삭제합니다.
    """
    try:
        doc_service = DocumentService()
        success = await doc_service.delete_document(
            document_id=document_id,
            org_id=current_user.org_id,
            user_id=current_user.user_id
        )
        if success:
            return {"status": "success", "message": "문서가 삭제되었습니다."}
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 