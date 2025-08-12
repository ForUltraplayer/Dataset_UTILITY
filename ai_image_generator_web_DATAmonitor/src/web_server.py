# -*- coding: utf-8 -*-

"""
@File: web_server.py
@Date: 2025-08-01
@Author: SGM
@Brief: AI 이미지 생성 웹 서버
@section MODIFYINFO 수정정보
"""


import uvicorn
import httpx
import logging
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from common.settings import SERVICE_PORT, HOST, API_TIMEOUT_SECONDS, PREDEFINED_ENDPOINTS
import common.settings as settings
from services.api_manager import api_manager
from config.app_config import app_config

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")



@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    메인화면 접속
    :return: index.html
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """
    서버 상태 확인 (헬스체크)
    개발 시 서버가 정상 동작하는지 빠르게 확인용
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "AI Image Generator Web Server"
    }


@app.get("/api-status")
async def api_status_check():
    """
    외부 API 연결 상태 확인
    개발 시 외부 API 서버 연결 상태를 미리 확인할 수 있음
    """
    try:
        # 간단한 연결 테스트 (실제 API 호출 없이 연결만 확인)
        async with httpx.AsyncClient(timeout=API_TIMEOUT_SECONDS) as client:
            test_url = settings.EXTERNAL_API_URL.split('/api/')[0] if '/api/' in settings.EXTERNAL_API_URL else settings.EXTERNAL_API_URL
            response = await client.get(test_url, timeout=API_TIMEOUT_SECONDS)
            
        return {
            "status": "connected",
            "api_url": settings.EXTERNAL_API_URL,
            "connection_test": "success",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as exc:
        logger.warning(f"API 연결 테스트 실패: {exc}")
        return {
            "status": "disconnected",
            "api_url": settings.EXTERNAL_API_URL,
            "connection_test": "failed",
            "error": str(exc),
            "timestamp": datetime.now().isoformat(),
            "note": "외부 API 서버가 실행되지 않았거나 네트워크 문제일 수 있습니다."
        }


@app.get("/config")
async def get_frontend_config():
    """
    프론트엔드에서 필요한 설정 정보 반환
    """
    try:
        config_data = app_config.get_config_for_frontend()
        available_apis = api_manager.get_available_apis()
        
        return JSONResponse(status_code=200, content={
            "config": config_data,
            "apis": available_apis
        })
    except Exception as exc:
        logger.error(f"설정 로드 오류: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "설정을 로드할 수 없습니다.", "error_type": "config_error"}
        )


@app.post("/create")
async def create_item(request: Request):
    """
    이미지 생성 요청 처리 (기본 API 사용)
    """
    return await _create_with_api(request, api_name=None)


@app.post("/create/{api_name}")
async def create_with_specific_api(api_name: str, request: Request):
    """
    특정 API로 이미지 생성 요청 처리
    
    Args:
        api_name: 사용할 API 이름 (예: 'imagen', 'dalle')
    """
    return await _create_with_api(request, api_name=api_name)


@app.get("/api-endpoints")
async def get_api_endpoints():
    """
    사용 가능한 API 엔드포인트 목록 반환
    """
    return {
        "current_url": settings.EXTERNAL_API_URL,
        "predefined_endpoints": PREDEFINED_ENDPOINTS,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/change-api-url")
async def change_api_url(request: Request):
    """
    API URL 동적 변경
    """
    try:
        data = await request.json()
        new_url = data.get("url")
        
        if not new_url:
            return JSONResponse(
                status_code=400,
                content={"detail": "URL이 제공되지 않았습니다.", "error_type": "validation_error"}
            )
        
        # URL 형식 간단 검증
        if not (new_url.startswith("http://") or new_url.startswith("https://")):
            return JSONResponse(
                status_code=400,
                content={"detail": "올바른 URL 형식이 아닙니다. http:// 또는 https://로 시작해야 합니다.", "error_type": "validation_error"}
            )
        
        # 설정 변경
        old_url = settings.EXTERNAL_API_URL
        settings.EXTERNAL_API_URL = new_url
        
        logger.info(f"API URL 변경: {old_url} -> {new_url}")
        
        return {
            "status": "success",
            "old_url": old_url,
            "new_url": new_url,
            "timestamp": datetime.now().isoformat(),
            "message": "API URL이 성공적으로 변경되었습니다."
        }
        
    except Exception as exc:
        logger.error(f"API URL 변경 오류: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "API URL 변경 중 오류가 발생했습니다.",
                "error_type": "internal_error"
            }
        )


async def _create_with_api(request: Request, api_name: str = None):
    """
    API를 사용한 이미지 생성 공통 로직
    """
    try:
        raw_data = await request.json()
        logger.info(f"이미지 생성 요청 받음: {raw_data.get('prompt', 'N/A')[:50]}... (API: {api_name or 'default'})")
        logger.info(f"요청 데이터 전체: {raw_data}")  # 디버깅용 로그 추가
        
        # 데이터 검증 및 정리
        validated_data = app_config.validate_request_data(raw_data)
        logger.info(f"검증된 데이터: {validated_data}")  # 디버깅용 로그 추가
        
        # API 설정 검증
        if not api_manager.validate_settings(validated_data, api_name):
            return JSONResponse(
                status_code=400,
                content={
                    "detail": "유효하지 않은 설정값입니다.",
                    "error_type": "validation_error"
                }
            )
        
        # 이미지 생성 요청
        response_data = await api_manager.generate_image(validated_data, api_name)
        logger.info(f"이미지 생성 성공 (API: {api_name or 'default'})")
        
        return JSONResponse(status_code=200, content=response_data)
        
    except ValueError as exc:
        # 입력 데이터 검증 오류
        logger.warning(f"입력 검증 오류: {exc}")
        return JSONResponse(
            status_code=400,
            content={
                "detail": str(exc),
                "error_type": "validation_error"
            }
        )
    except httpx.HTTPStatusError as exc:
        error_msg = f"외부 API 오류: {exc.response.status_code}"
        logger.error(f"{error_msg} - {exc.response.text}")
        return JSONResponse(
            status_code=exc.response.status_code, 
            content={
                "detail": error_msg,
                "error_type": "api_error",
                "status_code": exc.response.status_code
            }
        )
    except httpx.RequestError as exc:
        error_msg = f"API 연결 오류: {exc.__class__.__name__}"
        logger.error(f"{error_msg}: {exc}")
        return JSONResponse(
            status_code=502, 
            content={
                "detail": "외부 API 서버에 연결할 수 없습니다. 네트워크 연결을 확인하세요.",
                "error_type": "connection_error",
                "technical_detail": str(exc)
            }
        )
    except Exception as exc:
        error_msg = f"예상치 못한 오류: {exc.__class__.__name__}"
        logger.error(f"{error_msg}: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "서버 내부 오류가 발생했습니다.",
                "error_type": "internal_error"
            }
        )


if __name__ == '__main__':
    logger.info(f"AI Image Generator 웹 서버를 시작합니다...")
    logger.info(f"서버 주소: http://{HOST}:{SERVICE_PORT}")
    logger.info(f"외부 API: {settings.EXTERNAL_API_URL}")
    logger.info(f"헬스체크: http://localhost:{SERVICE_PORT}/health")
    logger.info(f"API 상태 확인: http://localhost:{SERVICE_PORT}/api-status")
    
    uvicorn.run("web_server:app", host=HOST, port=SERVICE_PORT)