/*
 * @File: init.js
 * @Date: 2025-08-01
 * @Author: SGM
 * @Brief: 초기화 스크립트
 * @section MODIFYINFO 수정정보
 */

$(document).ready(function() {
  // 모든 클래스가 로드되었는지 확인
  if (typeof ImageGeneratorController === 'undefined') {
    console.error('ImageGeneratorController가 로드되지 않았습니다.');
    return;
  }
  
  // 메인 컨트롤러 인스턴스 생성
  window.imageGenerator = new ImageGeneratorController();
  
  // API 설정 관리자 초기화
  if (typeof ApiConfigManager !== 'undefined') {
    ApiConfigManager.init();
    console.log('API Config Manager 초기화 완료');
  } else {
    console.warn('ApiConfigManager가 로드되지 않았습니다.');
  }
  
  // 이벤트 리스너 설정
  setupEventListeners();
  
  // 애플리케이션 초기화
  initializeApp();
  
  console.log('AI Image Generator 모듈화 초기화 완료');
});

/**
 * 이벤트 리스너 설정
 */
function setupEventListeners() {
  // 이미지 생성 버튼
  $(SELECTORS.GENERATOR_BTN).on('click', function() {
    window.imageGenerator.generateImage();
  });
  
  // 엔터키로 생성
  $(SELECTORS.PROMPT_INPUT).on('keypress', function(e) {
    if (e.which === 13) { // Enter key
      window.imageGenerator.generateImage();
    }
  });
  
  // 설정 변경 시 상태 관리자 업데이트 (선택사항)
  $(SELECTORS.MODEL_TYPE_SELECT + ', ' + SELECTORS.INDEX_TYPE_SELECT).on('change', function() {
    if (window.appState) {
      const settings = window.imageGenerator.uiManager.getCurrentSettings();
      window.appState.updateSettings(settings);
    }
  });
}

/**
 * 애플리케이션 초기화
 */
async function initializeApp() {
  // 서버 설정 로드
  if (window.appState && window.imageGenerator.apiClient) {
    await window.appState.loadConfig();
  }
  
  // 개발 편의를 위한 초기값 설정
  $(SELECTORS.MODEL_TYPE_SELECT).val('l14');
  $(SELECTORS.SEARCH_NUM_INPUT).val(4);
}

