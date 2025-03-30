import os
import uuid
from typing import List, Dict, Any, Optional

from fastapi import BackgroundTasks, HTTPException
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings
from app.schemas.document import (
    DocumentCreate, DocumentResponse, DocumentSearchResponse, 
    DocumentSearchResult, ChunkProcessResult
)

class DocumentService:
    """
    문서 저장 및 검색 서비스
    """
    
    def __init__(self):
        self.embedding_model = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # ChromaDB 클라이언트 초기화
        if settings.CHROMA_DB_HOST and settings.CHROMA_DB_PORT:
            # 클라이언트 모드
            self.chroma_client = chromadb.HttpClient(
                host=settings.CHROMA_DB_HOST,
                port=settings.CHROMA_DB_PORT
            )
        else:
            # 로컬 모드
            os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_DIR,
                settings=ChromaSettings(
                    anonymized_telemetry=False
                )
            )
    
    async def create_document(
        self,
        doc_create: DocumentCreate,
        user_id: int,
        org_id: int,
        background_tasks: BackgroundTasks
    ) -> DocumentResponse:
        """
        문서를 생성하고 비동기로 인덱싱합니다.
        """
        try:
            # 문서 ID 생성
            doc_id = str(uuid.uuid4())
            
            # 여기서는 간단히 구현하고, 실제로는 DB에 문서 메타데이터 저장
            # 예: await db.documents.insert(...)
            
            # 임시 응답 생성 (실제로는 DB에서 가져옴)
            doc_response = DocumentResponse(
                id=doc_id,
                title=doc_create.title,
                description=doc_create.description,
                category=doc_create.category,
                file_name=doc_create.file_name,
                file_type=doc_create.file_type,
                chunk_count=0,  # 아직 처리 전
                created_at=None,  # 실제 구현에서는 현재 시간
                updated_at=None,  # 실제 구현에서는 현재 시간
                is_indexed=False,
                uploaded_by=user_id,
                org_id=org_id
            )
            
            # 백그라운드 태스크로 문서 처리 (인덱싱) 시작
            # background_tasks.add_task(
            #     self._process_document,
            #     doc_id=doc_id,
            #     file_path=doc_create.file_path,
            #     org_id=org_id,
            #     metadata={
            #         "title": doc_create.title,
            #         "description": doc_create.description,
            #         "category": doc_create.category,
            #         "file_name": doc_create.file_name,
            #         "file_type": doc_create.file_type,
            #     }
            # )
            
            return doc_response
            
        except Exception as e:
            # 임시 파일 정리
            if os.path.exists(doc_create.file_path):
                try:
                    os.remove(doc_create.file_path)
                except:
                    pass
            
            raise HTTPException(status_code=500, detail=f"문서 생성 오류: {str(e)}")
    
    async def get_documents(
        self,
        org_id: int,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        문서 목록을 반환합니다.
        """
        # 실제 구현에서는 DB에서 문서 목록 조회
        # 샘플 데이터 반환
        return {
            "total": 0,
            "items": []
        }
    
    async def search_documents(
        self,
        query: str,
        org_id: int,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 5
    ) -> DocumentSearchResponse:
        """
        문서를 검색합니다.
        """
        # 컬렉션 이름 (조직별 컬렉션)
        collection_name = f"org_{org_id}"
        
        try:
            # 컬렉션 존재 여부 확인 및 생성
            try:
                collection = self.chroma_client.get_collection(name=collection_name)
            except:
                # 컬렉션이 없으면 빈 검색 결과 반환
                return DocumentSearchResponse(
                    results=[],
                    query=query,
                    total=0
                )
            
            # 랭체인 Chroma 래퍼 생성
            langchain_chroma = Chroma(
                client=self.chroma_client,
                collection_name=collection_name,
                embedding_function=self.embedding_model
            )
            
            # 필터 구성
            filter_dict = {}
            if filters and filters.get("category"):
                filter_dict["category"] = filters.get("category")
            
            # 유사성 검색 수행
            docs_with_scores = langchain_chroma.similarity_search_with_score(
                query=query,
                k=limit,
                filter=filter_dict if filter_dict else None
            )
            
            # 검색 결과 변환
            results = []
            for doc, score in docs_with_scores:
                results.append(
                    DocumentSearchResult(
                        id=doc.metadata.get("chunk_id", ""),
                        document_id=doc.metadata.get("document_id", ""),
                        document_title=doc.metadata.get("title", ""),
                        content=doc.page_content,
                        score=float(score),
                        metadata=doc.metadata
                    )
                )
            
            return DocumentSearchResponse(
                results=results,
                query=query,
                total=len(results)
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"문서 검색 오류: {str(e)}")
    
    async def delete_document(
        self,
        document_id: str,
        org_id: int,
        user_id: int
    ) -> bool:
        """
        문서를 삭제합니다.
        """
        try:
            # 실제 구현에서는 DB에서 문서 삭제 및 Chroma에서 청크 삭제
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"문서 삭제 오류: {str(e)}")
    
    # 백그라운드 처리를 위한 비동기 메서드
    async def _process_document(
        self,
        doc_id: str,
        file_path: str,
        org_id: int,
        metadata: Dict[str, Any]
    ) -> ChunkProcessResult:
        """
        문서를 처리하고 인덱싱합니다. (백그라운드 작업)
        """
        # 여기서는 간단히 구현
        # 실제 구현에서는 문서 유형에 따라 텍스트 추출 및 청킹 수행
        # 그 후 임베딩 생성 및 Chroma DB에 저장
        
        try:
            # 파일 처리 완료 후 임시 파일 삭제
            if os.path.exists(file_path):
                os.remove(file_path)
                
            return ChunkProcessResult(
                document_id=doc_id,
                chunk_count=0,
                status="success"
            )
            
        except Exception as e:
            # 오류 발생 시 상태 업데이트
            return ChunkProcessResult(
                document_id=doc_id,
                chunk_count=0,
                status="error",
                error=str(e)
            ) 