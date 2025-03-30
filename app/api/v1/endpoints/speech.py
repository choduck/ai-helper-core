from typing import Any, Optional
import os
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import openai

from app.services.auth import get_current_user, User
from app.core.config import settings

router = APIRouter()

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    음성 파일을 텍스트로 변환합니다.
    """
    try:
        # 임시 파일 생성
        with NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp:
            content = await file.read()
            temp.write(content)
            temp_path = temp.name
        
        try:
            # OpenAI 클라이언트 초기화
            client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            # 파일 업로드 및 트랜스크립션 요청
            with open(temp_path, "rb") as audio_file:
                transcription = await client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    language=language
                )
            
            # 응답 반환
            return {
                "text": transcription.text,
                "language": language or "auto"
            }
        
        finally:
            # 임시 파일 삭제
            os.unlink(temp_path)
    
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API 오류: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"음성 처리 오류: {str(e)}")

@router.post("/synthesize")
async def synthesize_speech(
    text: str = Form(...),
    voice: str = Form("alloy"),
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    """
    텍스트를 음성으로 변환합니다.
    """
    try:
        # API 키 확인
        if not settings.ELEVENLABS_API_KEY:
            raise HTTPException(status_code=500, detail="ElevenLabs API 키가 설정되지 않았습니다.")
        
        # 간단한 구현 (실제로는 ElevenLabs API 사용)
        # 이 예제에서는 OpenAI의 TTS API 사용
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = await client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # 응답을 스트리밍 형태로 반환
        def iterfile():
            yield response.content
        
        return StreamingResponse(
            iterfile(), 
            media_type="audio/mpeg",
            headers={"Content-Disposition": f'attachment; filename="speech.mp3"'}
        )
        
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API 오류: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"음성 합성 오류: {str(e)}") 