# -*- coding: utf-8 -*-

"""
@File: image_api_service.py
@Date: 2025-08-01
@Author: SGM
@Brief: 외부 이미지 API 서비스
@section MODIFYINFO 수정정보
"""

import httpx
import logging
from common.settings import API_TIMEOUT_SECONDS
import common.settings as settings

logger = logging.getLogger(__name__)

async def call_image_generation_api(data: dict):
    """
    외부 이미지 생성 API 호출
    
    Args:
        data (dict): API 요청 데이터
        
    Returns:
        dict: API 응답 데이터
        
    Raises:
        httpx.HTTPStatusError: HTTP 에러 발생 시
        httpx.RequestError: 네트워크 연결 오류 시
    """
    timeout_config = httpx.Timeout(API_TIMEOUT_SECONDS, connect=10.0)  # 설정 파일에서 타임아웃 시간 가져옴
    
    logger.info(f"외부 API 호출 시작: {settings.EXTERNAL_API_URL}")
    logger.info(f"외부 API로 전송할 데이터: {data}")
    logger.info(f"search_num 전달 확인: {data.get('search_num', 'NOT_FOUND')}")
    
    async with httpx.AsyncClient(timeout=timeout_config) as client:
        try:
            response = await client.post(settings.EXTERNAL_API_URL, json=data)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"API 호출 성공: 응답 크기 {len(str(result))} 문자")
            
            # vectorResult 배열 크기 확인
            if 'vectorResult' in result:
                vector_count = len(result['vectorResult']) if result['vectorResult'] else 0
                logger.info(f"요청한 이미지 개수: {data.get('search_num', 'N/A')}")
                logger.info(f"실제 응답받은 이미지 개수: {vector_count}")
                
                if vector_count != data.get('search_num', 0):
                    logger.warning(f"이미지 개수 불일치! 요청: {data.get('search_num')}, 응답: {vector_count}")
                    
                    # 응답에 제한 정보 추가 (프론트엔드에서 사용자에게 알림)
                    result['_server_limitation'] = {
                        'requested': data.get('search_num', 0),
                        'actual': vector_count,
                        'message': f"외부 API 서버에서 최대 {vector_count}개까지만 반환합니다."
                    }
                    
                # 응답 구조 상세 분석
                if result['vectorResult']:
                    logger.info(f"첫 번째 이미지 구조: {list(result['vectorResult'][0].keys()) if result['vectorResult'][0] else 'N/A'}")
            else:
                logger.warning("응답에 vectorResult가 없습니다")
                logger.info(f"전체 응답 구조: {list(result.keys())}")
                
            return result
            
        except httpx.TimeoutException as exc:
            logger.error(f"API 타임아웃: {exc}")
            raise httpx.RequestError(f"API 응답 시간 초과 ({API_TIMEOUT_SECONDS}초)") from exc
