# -*- coding: utf-8 -*-

"""
@File: app_config.py
@Date: 2025-08-05
@Author: SGM
@Brief: 애플리케이션 전반의 설정을 통합 관리
@section MODIFYINFO 수정정보
"""

import logging
from typing import Dict, Any
from common.settings import (
    SERVICE_PORT, HOST, EXTERNAL_API_URL, 
    DEBUG_MODE, API_TIMEOUT_SECONDS
)

logger = logging.getLogger(__name__)

class AppConfig:
    """
    애플리케이션 전반의 설정을 통합 관리하는 클래스
    
    - 서버 설정
    - API 설정  
    - UI 설정
    - 프론트엔드에서 필요한 설정 제공
    """
    
    def __init__(self):
        self.server_config = self._load_server_config()
        self.api_config = self._load_api_config()
        self.ui_config = self._load_ui_config()
        logger.info("애플리케이션 설정 로드 완료")
    
    def _load_server_config(self) -> Dict[str, Any]:
        """서버 관련 설정"""
        return {
            'host': HOST,
            'port': SERVICE_PORT,
            'debug': DEBUG_MODE
        }
    
    def _load_api_config(self) -> Dict[str, Any]:
        """API 관련 설정"""
        return {
            'imagen': {
                'url': EXTERNAL_API_URL,
                'timeout': API_TIMEOUT_SECONDS,
                'name': 'Imagen API',
                'description': '구글 Imagen 기반 이미지 생성'
            }
            # 추후 추가될 API 설정들
        }
    
    def _load_ui_config(self) -> Dict[str, Any]:
        """UI 관련 설정"""
        return {
            'default_settings': {
                'model_type': 'l14',
                'index_type': 'cos',
                'search_num': 4
            },
            'limits': {
                'max_search_num': 10,
                'min_search_num': 1,
                'max_prompt_length': 500
            },
            'theme': {
                'primary_color': '#646464',
                'success_color': '#28a745',
                'error_color': '#dc3545'
            }
        }
    
    def get_config_for_frontend(self) -> Dict[str, Any]:
        """
        프론트엔드에서 사용할 설정만 반환
        (보안상 중요한 정보는 제외)
        
        Returns:
            Dict: 프론트엔드용 설정 데이터
        """
        return {
            'apis': {
                name: {
                    'name': config['name'],
                    'description': config['description']
                    # URL이나 timeout 같은 민감한 정보는 제외
                }
                for name, config in self.api_config.items()
            },
            'ui': self.ui_config,
            'server': {
                'debug': self.server_config['debug']
                # host, port 같은 서버 정보는 제외
            }
        }
    
    def get_api_config(self, api_name: str) -> Dict[str, Any]:
        """
        특정 API의 설정 반환
        
        Args:
            api_name: API 이름
            
        Returns:
            Dict: API 설정 데이터
            
        Raises:
            KeyError: 존재하지 않는 API인 경우
        """
        if api_name not in self.api_config:
            available_apis = list(self.api_config.keys())
            raise KeyError(f"API '{api_name}' 설정을 찾을 수 없습니다. 사용 가능한 API: {available_apis}")
        
        return self.api_config[api_name]
    
    def update_api_config(self, api_name: str, config: Dict[str, Any]) -> None:
        """
        API 설정 업데이트 (런타임에서 설정 변경 시 사용)
        
        Args:
            api_name: API 이름
            config: 새로운 설정 데이터
        """
        if api_name in self.api_config:
            self.api_config[api_name].update(config)
            logger.info(f"API '{api_name}' 설정 업데이트됨")
        else:
            self.api_config[api_name] = config
            logger.info(f"새로운 API '{api_name}' 설정 추가됨")
    
    def validate_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        요청 데이터 검증 및 정리
        
        Args:
            data: 클라이언트에서 온 요청 데이터
            
        Returns:
            Dict: 검증된 데이터
            
        Raises:
            ValueError: 유효하지 않은 데이터인 경우
        """
        validated = {}
        
        # 필수 필드 검증
        if not data.get('prompt'):
            raise ValueError("프롬프트는 필수입니다")
        
        prompt = data['prompt'].strip()
        if len(prompt) > self.ui_config['limits']['max_prompt_length']:
            raise ValueError(f"프롬프트가 너무 깁니다 (최대 {self.ui_config['limits']['max_prompt_length']}자)")
        
        validated['prompt'] = prompt
        
        # 선택적 필드 검증 및 기본값 설정 (JavaScript camelCase -> Python snake_case 변환)
        validated['model_type'] = data.get('modelType', data.get('model_type', self.ui_config['default_settings']['model_type']))
        validated['index_type'] = data.get('indexType', data.get('index_type', self.ui_config['default_settings']['index_type']))
        
        # search_num 검증 (JavaScript camelCase 지원)
        search_num = data.get('searchNum', data.get('search_num', self.ui_config['default_settings']['search_num']))
        try:
            search_num = int(search_num)
            if not (self.ui_config['limits']['min_search_num'] <= search_num <= self.ui_config['limits']['max_search_num']):
                raise ValueError(f"Search Num은 {self.ui_config['limits']['min_search_num']}~{self.ui_config['limits']['max_search_num']} 사이여야 합니다")
            
            # 디버깅용 로그 추가
            logger.info(f"search_num 검증 통과: {search_num} (타입: {type(search_num)})")
        except (ValueError, TypeError) as e:
            logger.error(f"search_num 검증 실패: {search_num} (타입: {type(search_num)}), 오류: {e}")
            raise ValueError("Search Num은 숫자여야 합니다")
        
        validated['search_num'] = search_num
        validated['querySend'] = data.get('querySend', True)
        
        # *** 중요 수정: 외부 API는 camelCase를 기대함 ***
        # 내부적으로는 snake_case 사용하지만, 외부 API 전송 시에는 원본 형태 유지
        validated['searchNum'] = search_num  # 외부 API용 camelCase 버전 추가
        validated['modelType'] = validated['model_type']  # 외부 API용
        validated['indexType'] = validated['index_type']  # 외부 API용
        
        return validated

# 전역 설정 관리자 인스턴스
app_config = AppConfig()