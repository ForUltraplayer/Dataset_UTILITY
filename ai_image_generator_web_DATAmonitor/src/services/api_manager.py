# -*- coding: utf-8 -*-

"""
@File: api_manager.py
@Date: 2025-08-05
@Author: SGM
@Brief: API 관리자 - 여러 이미지 생성 API를 통합 관리
@section MODIFYINFO 수정정보

"""

import logging
from typing import Dict, Any, Optional
from .image_api_service import call_image_generation_api

logger = logging.getLogger(__name__)

class ApiManager:
    """
    이미지 생성 API들을 통합 관리하는 클래스
    
    현재는 Imagen API만 지원하지만, 나중에 DALL-E, Midjourney 등을 
    쉽게 추가할 수 있도록 설계됨
    """
    
    def __init__(self):
        self.apis = {
            'imagen': {
                'name': 'Imagen API',
                'description': '구글 Imagen 기반 이미지 생성',
                'supported_settings': {
                    'model_type': ['b32', 'b16', 'l14', 'l14_336'],
                    'index_type': ['l2', 'cos'],
                    'search_num': {'min': 1, 'max': 10}
                },
                'handler': self._call_imagen_api
            }
            # 추후 추가될 API들:
            # 'dalle': {...},
            # 'midjourney': {...}
        }
        self.default_api = 'imagen'
        logger.info(f"API 관리자 초기화 완료: {list(self.apis.keys())}")
    
    async def generate_image(self, data: Dict[str, Any], api_name: Optional[str] = None) -> Dict[str, Any]:
        """
        이미지 생성 요청 처리
        
        Args:
            data: 이미지 생성 요청 데이터
            api_name: 사용할 API 이름 (None이면 기본 API 사용)
            
        Returns:
            Dict: API 응답 데이터
            
        Raises:
            ValueError: 지원하지 않는 API인 경우
            Exception: API 호출 실패 시
        """
        if api_name is None:
            api_name = self.default_api
        
        if api_name not in self.apis:
            available_apis = list(self.apis.keys())
            raise ValueError(f"지원하지 않는 API: {api_name}. 사용 가능한 API: {available_apis}")
        
        api_info = self.apis[api_name]
        logger.info(f"이미지 생성 요청 - API: {api_info['name']}")
        
        try:
            # API별 핸들러 호출
            result = await api_info['handler'](data)
            logger.info(f"이미지 생성 성공 - API: {api_name}")
            return result
            
        except Exception as exc:
            logger.error(f"이미지 생성 실패 - API: {api_name}, 오류: {exc}")
            raise
    
    async def _call_imagen_api(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Imagen API 호출 (기존 로직 재사용)
        """
        return await call_image_generation_api(data)
    
    def get_available_apis(self) -> Dict[str, Dict[str, Any]]:
        """
        사용 가능한 API 목록과 각 API의 정보 반환
        
        Returns:
            Dict: API 이름을 키로 하는 API 정보 딕셔너리
        """
        return {
            name: {
                'name': info['name'],
                'description': info['description'],
                'supported_settings': info['supported_settings']
            }
            for name, info in self.apis.items()
        }
    
    def validate_settings(self, settings: Dict[str, Any], api_name: Optional[str] = None) -> bool:
        """
        API별 설정값 검증
        
        Args:
            settings: 검증할 설정값들
            api_name: 대상 API 이름
            
        Returns:
            bool: 설정값이 유효한지 여부
        """
        if api_name is None:
            api_name = self.default_api
            
        if api_name not in self.apis:
            return False
        
        supported = self.apis[api_name]['supported_settings']
        
        # model_type 검증
        if 'model_type' in settings:
            if settings['model_type'] not in supported['model_type']:
                logger.warning(f"지원하지 않는 model_type: {settings['model_type']}")
                return False
        
        # index_type 검증
        if 'index_type' in settings:
            if settings['index_type'] not in supported['index_type']:
                logger.warning(f"지원하지 않는 index_type: {settings['index_type']}")
                return False
        
        # search_num 검증
        if 'search_num' in settings:
            num = settings['search_num']
            if not (supported['search_num']['min'] <= num <= supported['search_num']['max']):
                logger.warning(f"search_num 범위 초과: {num}")
                return False
        
        return True
    
    def set_default_api(self, api_name: str) -> None:
        """
        기본 사용 API 설정
        
        Args:
            api_name: 기본으로 사용할 API 이름
        """
        if api_name in self.apis:
            self.default_api = api_name
            logger.info(f"기본 API 변경: {api_name}")
        else:
            raise ValueError(f"존재하지 않는 API: {api_name}")

# 전역 API 관리자 인스턴스
api_manager = ApiManager()