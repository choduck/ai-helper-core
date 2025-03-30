from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings

# HTTP Bearer 보안 스키마 설정
security = HTTPBearer(auto_error=False)

# 인증 우회 모드 - True로 설정하면 모든 인증을 통과시킵니다
BYPASS_AUTH = True

class User(BaseModel):
    user_id: int
    username: str
    email: str
    org_id: Optional[int] = None
    role: str

# 기본 테스트 사용자 생성
DEFAULT_USER = User(
    user_id=1,
    username="test_user",
    email="test@example.com",
    org_id=1,
    role="ADMIN"
)

def decode_token(token: str) -> Dict[str, Any]:
    """
    JWT 토큰을 디코딩하여 페이로드를 반환합니다.
    """
    # 인증 우회 모드가 활성화된 경우 기본 페이로드 반환
    if BYPASS_AUTH:
        return {
            "user": {
                "id": DEFAULT_USER.user_id,
                "username": DEFAULT_USER.username,
                "email": DEFAULT_USER.email,
                "orgId": DEFAULT_USER.org_id,
                "role": DEFAULT_USER.role
            },
            "exp": (datetime.utcnow() + timedelta(days=1)).timestamp()
        }
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 정보",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> User:
    """
    현재 요청의 JWT 토큰에서 사용자 정보를 추출합니다.
    인증 우회 모드가 활성화된 경우 기본 사용자를 반환합니다.
    """
    # 인증 우회 모드가 활성화된 경우 기본 사용자 반환
    if BYPASS_AUTH:
        return DEFAULT_USER
    
    # 토큰이 없는 경우
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 정보가 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = decode_token(token)

    # 토큰 만료 검사
    expiration = datetime.fromtimestamp(payload.get("exp", 0))
    if datetime.utcnow() > expiration:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 정보가 만료되었습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 사용자 정보 추출
    user_data = payload.get("user", {})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자 정보를 찾을 수 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # User 객체 생성
    try:
        user = User(
            user_id=user_data.get("id"),
            username=user_data.get("username"),
            email=user_data.get("email"),
            org_id=user_data.get("orgId"),
            role=user_data.get("role")
        )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"사용자 정보 파싱 오류: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_admin(user: User = Depends(get_current_user)) -> User:
    """
    사용자가 관리자인지 확인합니다.
    인증 우회 모드가 활성화된 경우 항상 통과합니다.
    """
    if BYPASS_AUTH:
        return DEFAULT_USER
        
    if user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 작업을 실행할 권한이 없습니다"
        )
    return user 