/*
 * @File: imageGenerator.js
 * @Date: 2025-08-05
 * @Author: SGM
 * @Brief: 이미지 생성 메인 컨트롤러 모듈
 * @section MODIFYINFO 수정정보
 */

class ImageGeneratorController {
    constructor() {
        this.isGenerating = false;
        this.apiClient = new ApiClient();
        this.uiManager = new UiManager();
        
        // 상태 관리자 연결
        if (window.appState) {
            this.stateManager = window.appState;
            this.setupStateSubscription();
        }
    }
    
    /**
     * 상태 변경 구독 설정
     */
    setupStateSubscription() {
        this.stateManager.subscribe((newState, prevState) => {
            // 로딩 상태 변경 시 UI 업데이트
            if (newState.isLoading !== prevState.isLoading) {
                this.uiManager.toggleLoading(newState.isLoading);
            }
            
            // 결과 상태 변경 시 UI 업데이트
            if (newState.lastResult !== prevState.lastResult) {
                this.displayResults(newState.lastResult);
            }
        });
    }
    
    /**
     * 이미지 생성 메인 함수
     */
    async generateImage() {
        console.log('=== generateImage 시작 ===');
        
        if (this.isGenerating) {
            console.warn('이미지 생성이 이미 진행 중입니다.');
            return;
        }
        
        try {
            // 입력값 수집 및 검증
            const inputData = this.collectInputData();
            if (!this.validateInput(inputData)) {
                return;
            }
            
            this.isGenerating = true;
            
            // 상태 관리자 업데이트
            if (this.stateManager) {
                this.stateManager.setLoading(true);
                this.stateManager.clearResults();
                this.stateManager.updateSettings(inputData);
            }
            
            // UI 초기화
            this.uiManager.clearResults();
            this.uiManager.showLoading();
            
            // API 호출
            console.log('API 호출 시작:', inputData);
            const result = await this.apiClient.generateImage(inputData);
            console.log('API 호출 성공:', result);
            
            // 결과 처리
            this.handleSuccess(result);
            
        } catch (error) {
            console.error('generateImage 오류:', error);
            this.handleError(error);
        } finally {
            this.isGenerating = false;
            this.uiManager.hideLoading();
            
            if (this.stateManager) {
                this.stateManager.setLoading(false);
            }
        }
    }
    
    /**
     * 입력 데이터 수집
     */
    collectInputData() {
        return {
            prompt: $(SELECTORS.PROMPT_INPUT).val().trim(),
            modelType: $(SELECTORS.MODEL_TYPE_SELECT).val(),
            indexType: $(SELECTORS.INDEX_TYPE_SELECT).val(),
            searchNum: parseInt($(SELECTORS.SEARCH_NUM_INPUT).val(), 10),
            querySend: true
        };
    }
    
    /**
     * 입력값 검증
     */
    validateInput(data) {
        if (!data.prompt) {
            this.uiManager.displayError('프롬프트를 입력해주세요.');
            return false;
        }
        
        if (isNaN(data.searchNum) || data.searchNum < 1 || data.searchNum > 10) {
            this.uiManager.displayError('검색 개수는 1-10 사이의 숫자여야 합니다.');
            return false;
        }
        
        return true;
    }
    
    /**
     * 성공 응답 처리
     */
    handleSuccess(result) {
        console.log('이미지 생성 성공:', result);
        
        // 상태 관리자 업데이트
        if (this.stateManager) {
            this.stateManager.setResult(result);
        }
        
        // UI 업데이트
        this.displayResults(result);
        
        // 서버 제한 알림 (백엔드에서 추가한 제한 정보)
        if (result._server_limitation) {
            this.uiManager.displayWarning(result._server_limitation.message);
        }
    }
    
    /**
     * 오류 처리
     */
    handleError(error) {
        console.error('이미지 생성 오류:', error);
        
        let errorMessage = '이미지 생성 중 오류가 발생했습니다.';
        
        if (error.response) {
            // HTTP 오류
            const data = error.response;
            switch (data.error_type) {
                case 'validation_error':
                    errorMessage = data.detail || '입력값이 유효하지 않습니다.';
                    break;
                case 'connection_error':
                    errorMessage = '외부 API 서버에 연결할 수 없습니다. 네트워크를 확인해주세요.';
                    break;
                case 'api_error':
                    errorMessage = `외부 API 오류 (${data.status_code}): ${data.detail}`;
                    break;
                default:
                    errorMessage = data.detail || errorMessage;
            }
        }
        
        this.uiManager.displayError(errorMessage);
    }
    
    /**
     * 결과 표시
     */
    displayResults(result) {
        if (!result || !result.result) {
            return;
        }
        
        // 쿼리 이미지 표시
        if (result.queryImage) {
            this.uiManager.displayQueryImage(result.queryImage);
        }
        
        // 결과 이미지들 표시
        if (result.vectorResult && result.vectorResult.length > 0) {
            this.uiManager.displayResultImages(result.vectorResult);
        }
        
        // JSON 뷰어 표시
        this.uiManager.displayJson(result);
    }
    
    /**
     * 프리셋 적용 (향후 확장용)
     */
    applyPreset(presetName) {
        console.log(`프리셋 적용: ${presetName}`);
        // TODO: 프리셋 로직 구현
    }
    
    /**
     * API 변경 (향후 확장용)
     */
    changeApi(apiName) {
        console.log(`API 변경: ${apiName}`);
        if (this.stateManager) {
            this.stateManager.setCurrentApi(apiName);
        }
        // TODO: API 변경 로직 구현
    }
}

// 전역으로 노출
window.ImageGeneratorController = ImageGeneratorController;