from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Body, Path, Query
from pydantic import BaseModel, Field

from app.services.auth import get_current_user, verify_admin, User

router = APIRouter()

# 스키마 정의
class PromptVariable(BaseModel):
    name: str = Field(..., description="변수 이름")
    description: str = Field(..., description="변수 설명")
    default_value: Optional[str] = Field(None, description="기본값")

class PromptTemplateBase(BaseModel):
    title: str = Field(..., description="프롬프트 템플릿 제목")
    description: str = Field(..., description="프롬프트 템플릿 설명")
    content: str = Field(..., description="프롬프트 내용 (변수는 {{variable_name}} 형식으로 포함)")
    variables: List[PromptVariable] = Field(default=[], description="템플릿에 사용된 변수 목록")
    is_public: bool = Field(default=False, description="공개 여부")

class PromptTemplateCreate(PromptTemplateBase):
    pass

class PromptTemplateUpdate(BaseModel):
    title: Optional[str] = Field(None, description="프롬프트 템플릿 제목")
    description: Optional[str] = Field(None, description="프롬프트 템플릿 설명")
    content: Optional[str] = Field(None, description="프롬프트 내용")
    variables: Optional[List[PromptVariable]] = Field(None, description="템플릿에 사용된 변수 목록")
    is_public: Optional[bool] = Field(None, description="공개 여부")

class PromptTemplate(PromptTemplateBase):
    id: int = Field(..., description="템플릿 ID")
    org_id: int = Field(..., description="조직 ID")
    created_by: int = Field(..., description="생성자 ID")
    created_at: str = Field(..., description="생성 시간")
    updated_at: str = Field(..., description="수정 시간")

@router.post("", response_model=PromptTemplate)
async def create_prompt_template(
    template: PromptTemplateCreate = Body(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    새 프롬프트 템플릿을 생성합니다.
    """
    # 실제 구현에서는 데이터베이스에 저장
    # 현재는 샘플 응답 반환
    return {
        "id": 1,
        "title": template.title,
        "description": template.description,
        "content": template.content,
        "variables": template.variables,
        "is_public": template.is_public,
        "org_id": current_user.org_id,
        "created_by": current_user.user_id,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }

@router.get("", response_model=List[PromptTemplate])
async def list_prompt_templates(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    프롬프트 템플릿 목록을 반환합니다.
    """
    # 실제 구현에서는 데이터베이스에서 조회
    # 현재는 샘플 데이터 반환
    return []

@router.get("/{template_id}", response_model=PromptTemplate)
async def get_prompt_template(
    template_id: int = Path(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    특정 프롬프트 템플릿을 조회합니다.
    """
    # 실제 구현에서는 데이터베이스에서 조회
    # 현재는 샘플 데이터 반환
    return {
        "id": template_id,
        "title": "샘플 템플릿",
        "description": "샘플 템플릿 설명",
        "content": "안녕하세요, {{name}}님! {{content}}에 대해 설명해 드리겠습니다.",
        "variables": [
            {"name": "name", "description": "사용자 이름", "default_value": "사용자"},
            {"name": "content", "description": "설명할 내용", "default_value": "AI"}
        ],
        "is_public": True,
        "org_id": current_user.org_id,
        "created_by": current_user.user_id,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }

@router.put("/{template_id}", response_model=PromptTemplate)
async def update_prompt_template(
    template_id: int = Path(...),
    update_data: PromptTemplateUpdate = Body(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    프롬프트 템플릿을 수정합니다.
    """
    # 실제 구현에서는 데이터베이스에서 업데이트
    # 현재는 샘플 데이터 반환
    return {
        "id": template_id,
        "title": update_data.title or "기존 제목",
        "description": update_data.description or "기존 설명",
        "content": update_data.content or "기존 내용",
        "variables": update_data.variables or [],
        "is_public": update_data.is_public or False,
        "org_id": current_user.org_id,
        "created_by": current_user.user_id,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }

@router.delete("/{template_id}")
async def delete_prompt_template(
    template_id: int = Path(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    프롬프트 템플릿을 삭제합니다.
    """
    # 실제 구현에서는 데이터베이스에서 삭제
    return {"status": "success", "message": f"템플릿 {template_id}가 삭제되었습니다."} 