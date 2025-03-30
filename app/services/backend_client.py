import json
from typing import Dict, Any, Optional, List, Union

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.services.auth import User

class BackendClient:
    """
    ai-helper-back과 통신하기 위한 HTTP 클라이언트
    """
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or "http://localhost:8080/api"  # 기본 백엔드 API URL
        self.client = httpx.AsyncClient(timeout=30.0)  # 30초 타임아웃

    async def close(self):
        """
        클라이언트 연결을 종료합니다.
        """
        await self.client.aclose()

    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        token: Optional[str] = None, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        HTTP 요청을 수행하고 응답을 반환합니다.
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=headers
            )
            
            # 상태 코드 확인
            response.raise_for_status()
            
            # JSON 응답 파싱
            if response.text:
                return response.json()
            return None
            
        except httpx.HTTPStatusError as e:
            # HTTP 오류 처리
            error_detail = "알 수 없는 오류"
            try:
                error_json = e.response.json()
                error_detail = error_json.get("message", str(e))
            except:
                error_detail = str(e)
                
            status_code = e.response.status_code
            raise HTTPException(status_code=status_code, detail=error_detail)
            
        except httpx.RequestError as e:
            # 네트워크 오류 처리
            raise HTTPException(status_code=503, detail=f"백엔드 서버 연결 오류: {str(e)}")
            
        except Exception as e:
            # 기타 예외 처리
            raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")

    # GET 요청
    async def get(
        self, 
        endpoint: str, 
        token: Optional[str] = None, 
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        return await self._request("GET", endpoint, token, params=params)

    # POST 요청
    async def post(
        self, 
        endpoint: str, 
        token: Optional[str] = None, 
        json_data: Optional[Dict[str, Any]] = None
    ) -> Any:
        return await self._request("POST", endpoint, token, json_data=json_data)

    # PUT 요청
    async def put(
        self, 
        endpoint: str, 
        token: Optional[str] = None, 
        json_data: Optional[Dict[str, Any]] = None
    ) -> Any:
        return await self._request("PUT", endpoint, token, json_data=json_data)

    # DELETE 요청
    async def delete(
        self, 
        endpoint: str, 
        token: Optional[str] = None, 
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        return await self._request("DELETE", endpoint, token, params=params)

    # 사용자 관련 API
    async def get_user_data(self, user_id: int, token: str) -> Dict[str, Any]:
        """
        사용자 정보를 가져옵니다.
        """
        return await self.get(f"users/{user_id}", token)

    async def get_organization_data(self, org_id: int, token: str) -> Dict[str, Any]:
        """
        조직 정보를 가져옵니다.
        """
        return await self.get(f"organizations/{org_id}", token)

    # 사용량 로깅 API
    async def log_api_usage(
        self, 
        user_id: int,
        org_id: int,
        token: str,
        api_type: str,
        tokens_used: int,
        estimated_cost: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        API 사용량을 로깅합니다.
        """
        data = {
            "userId": user_id,
            "orgId": org_id,
            "apiType": api_type,
            "tokensUsed": tokens_used,
            "estimatedCost": estimated_cost,
            "metadata": metadata or {}
        }
        return await self.post("usage/log", token, json_data=data)

# 싱글턴 인스턴스
backend_client = BackendClient() 