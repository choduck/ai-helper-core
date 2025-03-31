import json
import time
import asyncio
import os
import logging
import traceback
from typing import Dict, List, Any, Optional, AsyncGenerator

from fastapi import BackgroundTasks, HTTPException
import openai
import tiktoken

from app.core.config import settings
from app.schemas.chat import ChatMessage, ChatResponse, ChatChoice, ChatUsage
from app.services.backend_client import backend_client
from app.services.document import DocumentService

# 디버깅을 위한 로거 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("C:/workspace2/ai-helper/ai-helper-core/openai_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("openai_debug")

class ChatService:
    """
    OpenAI API를 사용한 채팅 서비스
    """
    
    def __init__(self):
        # API 키 로깅 (마스킹 처리)
        api_key = settings.OPENAI_API_KEY
        if api_key:
            masked_key = f"{api_key[:8]}{'*' * (len(api_key) - 12)}{api_key[-4:]}"
            logger.info(f"OpenAI API 키 설정됨: {masked_key}")
            
            # API 키 형식 검증
            if not api_key.startswith(("sk-", "sk-proj-")):
                logger.error(f"API 키 형식이 유효하지 않습니다. 'sk-' 또는 'sk-proj-'로 시작해야 합니다.")
        else:
            logger.error("OpenAI API 키가 설정되지 않았습니다!")
        
        # 베이스 URL 확인
        base_url = os.getenv("OPENAI_API_BASE")
        if base_url:
            logger.info(f"OpenAI API Base URL: {base_url}")
            self.openai_client = openai.AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=base_url
            )
        else:
            logger.info("기본 OpenAI API URL 사용")
            self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
        # 환경 변수 디버깅
        logger.debug(f"OPENAI_API_KEY 설정 여부: {bool(settings.OPENAI_API_KEY)}")
        logger.debug(f"DEFAULT_MODEL: {settings.DEFAULT_MODEL}")
        
        self.doc_service = DocumentService()
        
    def _get_encoding(self, model: str) -> tiktoken.Encoding:
        """
        모델에 맞는 토큰 인코딩을 가져옵니다.
        """
        try:
            if "gpt-4" in model:
                return tiktoken.encoding_for_model("gpt-4o")
            elif "gpt-3.5" in model:
                return tiktoken.encoding_for_model("gpt-3.5-turbo")
            else:
                return tiktoken.get_encoding("cl100k_base")  # 기본 인코딩
        except Exception:
            return tiktoken.get_encoding("cl100k_base")  # 오류 시 기본 인코딩
    
    def _count_tokens(self, text: str, model: str) -> int:
        """
        텍스트의 토큰 수를 계산합니다.
        """
        encoding = self._get_encoding(model)
        return len(encoding.encode(text))
    
    def _count_message_tokens(self, messages: List[ChatMessage], model: str) -> int:
        """
        메시지 리스트의 토큰 수를 계산합니다.
        """
        encoding = self._get_encoding(model)
        tokens_per_message = 3  # 메시지당 기본 토큰 수
        tokens_per_name = 1     # 이름당 추가 토큰 수
        
        total_tokens = 0
        for message in messages:
            total_tokens += tokens_per_message
            total_tokens += len(encoding.encode(message.content))
            total_tokens += len(encoding.encode(message.role))
            
        total_tokens += 3  # 마지막 assistant 메시지를 위한 추가 토큰
        return total_tokens
    
    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """
        토큰 사용량에 따른 비용을 계산합니다.
        """
        # 모델별 가격 정보 (USD 기준, 1K 토큰당)
        prices = {
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "gpt-4-32k": {"prompt": 0.06, "completion": 0.12},
            "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
            "gpt-3.5-turbo-16k": {"prompt": 0.003, "completion": 0.004},
        }
        
        # 기본 가격 설정
        default_price = {"prompt": 0.0015, "completion": 0.002}
        
        # 모델에 맞는 가격 선택
        for price_model, price in prices.items():
            if price_model in model:
                model_price = price
                break
        else:
            model_price = default_price
        
        # 비용 계산 (달러 단위)
        prompt_cost = (prompt_tokens / 1000) * model_price["prompt"]
        completion_cost = (completion_tokens / 1000) * model_price["completion"]
        
        return prompt_cost + completion_cost
    
    async def _log_usage(
        self, 
        user_id: int, 
        org_id: int, 
        model: str, 
        prompt_tokens: int, 
        completion_tokens: int,
        request_id: str,
        token: Optional[str] = None
    ) -> None:
        """
        API 사용량을 로깅합니다.
        """
        cost = self._calculate_cost(model, prompt_tokens, completion_tokens)
        
        try:
            # 사용량 데이터를 백엔드에 기록
            if token:
                await backend_client.log_api_usage(
                    user_id=user_id,
                    org_id=org_id,
                    token=token,
                    api_type="chat",
                    tokens_used=prompt_tokens + completion_tokens,
                    estimated_cost=cost,
                    metadata={
                        "model": model,
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "request_id": request_id
                    }
                )
        except Exception as e:
            # 로깅 실패는 사용자 응답에 영향을 주지 않도록 처리
            print(f"Usage logging error: {str(e)}")
    
    async def generate_completion(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user_id: Optional[int] = None,
        org_id: Optional[int] = None,
        token: Optional[str] = None
    ) -> ChatResponse:
        """
        채팅 응답을 생성합니다.
        """
        # 기본값 설정
        # model = model or settings.DEFAULT_MODEL
        # temperature = temperature or settings.TEMPERATURE
        # max_tokens = max_tokens or settings.MAX_TOKENS

        model = "gpt-4o" or settings.DEFAULT_MODEL
        temperature = 0.7 or settings.TEMPERATURE
        max_tokens = 2048 or settings.MAX_TOKENS
 

        # 디버깅 정보 기록
        logger.info(f"채팅 완성 생성 요청: 모델={model}, 온도={temperature}, 최대 토큰={max_tokens}")
        logger.debug(f"메시지 개수: {len(messages)}")
        
        try:
            # API 요청 준비 로깅
            formatted_messages = [{"role": m.role, "content": m.content} for m in messages]
            if len(formatted_messages) > 0:
                logger.debug(f"첫 번째 메시지 역할: {formatted_messages[0]['role']}")
                logger.debug(f"마지막 메시지 역할: {formatted_messages[-1]['role']}")
            
            logger.info("OpenAI API 호출 시작...")
            
            # OpenAI API 호출
            api_start_time = time.time()
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                n=1,
                stream=False
            )
            api_end_time = time.time()
            
            # API 응답 시간 로깅
            logger.info(f"OpenAI API 호출 완료: {(api_end_time - api_start_time):.2f}초 소요")
            
            # 응답 파싱
            completion = response.choices[0].message
            chat_message = ChatMessage(role=completion.role, content=completion.content)
            
            # 응답 내용 요약 로깅 (너무 길면 잘라서)
            content_preview = completion.content[:100] + "..." if len(completion.content) > 100 else completion.content
            logger.debug(f"응답 내용 (요약): {content_preview}")
            
            # 사용량 정보
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            cost = self._calculate_cost(model, prompt_tokens, completion_tokens)
            
            # 토큰 사용량 로깅
            logger.info(f"토큰 사용량: model={model}, 프롬프트={prompt_tokens}, 완성={completion_tokens}, 총={total_tokens}, 비용=${cost:.6f}")
            
            # 사용량 로깅 (백그라운드로 처리)
            if user_id and org_id:
                asyncio.create_task(self._log_usage(
                    user_id=user_id,
                    org_id=org_id,
                    model=model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    request_id=response.id,
                    token=token
                ))
            
            # 응답 객체 생성
            return ChatResponse(
                id=response.id,
                object="chat.completion",
                created=int(time.time()),
                model=model,
                choices=[
                    ChatChoice(
                        index=0,
                        message=chat_message,
                        finish_reason=response.choices[0].finish_reason
                    )
                ],
                usage=ChatUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    estimated_cost=cost
                )
            )
            
        except openai.APIError as e:
            # OpenAI API 오류 상세 로깅
            logger.error(f"OpenAI API 오류: {str(e)}")
            logger.error(f"상세 오류 추적: {traceback.format_exc()}")
            
            # 오류 분석
            error_message = str(e)
            if "Unauthorized" in error_message:
                logger.error("API 키가 유효하지 않거나 만료되었습니다.")
            elif "rate limit" in error_message.lower():
                logger.error("API 요청 한도에 도달했습니다.")
            elif "timeout" in error_message.lower():
                logger.error("API 요청 시간이 초과되었습니다.")
            
            raise HTTPException(status_code=500, detail=f"OpenAI API 오류: {str(e)}")
        except Exception as e:
            # 일반 오류 로깅
            logger.error(f"채팅 완성 생성 중 일반 오류: {str(e)}")
            logger.error(f"상세 오류 추적: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    
    async def generate_stream(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user_id: Optional[int] = None,
        org_id: Optional[int] = None,
        token: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        채팅 응답을 스트리밍으로 생성합니다.
        """
        # 기본값 설정
        model = model or settings.DEFAULT_MODEL
        temperature = temperature or settings.TEMPERATURE
        max_tokens = max_tokens or settings.MAX_TOKENS
        
        try:
            # 토큰 사용량 추적
            prompt_tokens = self._count_message_tokens(messages, model)
            completion_tokens = 0
            
            # OpenAI API 스트림 호출
            stream = await self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                temperature=temperature,
                max_tokens=max_tokens,
                n=1,
                stream=True
            )
            
            request_id = f"chatcmpl-{int(time.time())}"
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    delta_content = chunk.choices[0].delta.content
                    completion_tokens += self._count_tokens(delta_content, model)
                    
                    # SSE 형식으로 응답
                    yield f"data: {json.dumps({'content': delta_content})}\n\n"
            
            # 스트림 종료
            yield f"data: [DONE]\n\n"
            
            # 사용량 로깅 (백그라운드로 처리)
            if user_id and org_id:
                asyncio.create_task(self._log_usage(
                    user_id=user_id,
                    org_id=org_id,
                    model=model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    request_id=request_id,
                    token=token
                ))
                
        except openai.APIError as e:
            yield f"data: {json.dumps({'error': f'OpenAI API 오류: {str(e)}'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': f'내부 서버 오류: {str(e)}'})}\n\n"
    
    async def generate_with_context(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user_id: Optional[int] = None,
        org_id: Optional[int] = None,
        token: Optional[str] = None,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> ChatResponse:
        """
        관련 문서 컨텍스트를 포함한 채팅 응답을 생성합니다. (RAG)
        """
        # 기본값 설정
        model = model or settings.DEFAULT_MODEL
        temperature = temperature or settings.TEMPERATURE
        max_tokens = max_tokens or settings.MAX_TOKENS
        
        # 마지막 사용자 메시지 추출
        last_user_message = None
        for message in reversed(messages):
            if message.role == "user":
                last_user_message = message.content
                break
        
        if not last_user_message:
            return await self.generate_completion(
                messages, model, temperature, max_tokens, user_id, org_id, token
            )
        
        try:
            # 관련 문서 검색
            if org_id:
                search_result = await self.doc_service.search_documents(
                    query=last_user_message,
                    org_id=org_id,
                    limit=5
                )
                
                # 컨텍스트 구성
                context = ""
                for result in search_result.results:
                    context += f"--- {result.document_title} ---\n{result.content}\n\n"
                
                if context:
                    # 시스템 메시지 추가 또는 업데이트
                    system_message = f"""다음 정보를 참고하여 질문에 답변하세요:

{context}

위 정보에 답이 없는 경우, 알고 있는 정보를 기반으로 답변하세요. 
참고한 문서 제목을 응답 끝에 출처로 명시하세요."""
                    
                    # 메시지 목록 업데이트
                    updated_messages = []
                    has_system = False
                    
                    for message in messages:
                        if message.role == "system":
                            updated_messages.append(ChatMessage(
                                role="system",
                                content=system_message
                            ))
                            has_system = True
                        else:
                            updated_messages.append(message)
                    
                    if not has_system:
                        updated_messages.insert(0, ChatMessage(
                            role="system",
                            content=system_message
                        ))
                    
                    # 업데이트된 메시지로 응답 생성
                    return await self.generate_completion(
                        updated_messages, model, temperature, max_tokens, user_id, org_id, token
                    )
            
            # 컨텍스트 없이 기본 응답 생성
            return await self.generate_completion(
                messages, model, temperature, max_tokens, user_id, org_id, token
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"컨텍스트 검색 오류: {str(e)}") 