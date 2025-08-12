/*
 * @File: uiManager.js
 * @Date: 2025-08-05
 * @Author: Claude
 * @Brief: UI 관리 모듈
 * @section MODIFYINFO 수정정보
 */

class UiManager {
    constructor() {
        this.elements = this.cacheElements();
    }
    
    /**
     * DOM 요소 캐싱
     */
    cacheElements() {
        return {
            promptInput: $(SELECTORS.PROMPT_INPUT),
            modelTypeSelect: $(SELECTORS.MODEL_TYPE_SELECT),
            indexTypeSelect: $(SELECTORS.INDEX_TYPE_SELECT),
            searchNumInput: $(SELECTORS.SEARCH_NUM_INPUT),
            errorZone: $(SELECTORS.ERROR_ZONE),
            loadingZone: $(SELECTORS.LOADING_ZONE),
            queryImageZone: $(SELECTORS.QUERY_IMAGE_ZONE),
            resultImageZone: $(SELECTORS.RESULT_IMAGE_ZONE),
            jsonViewer: $(SELECTORS.JSON_VIEWER),
            generatorBtn: $(SELECTORS.GENERATOR_BTN)
        };
    }
    
    /**
     * 로딩 상태 표시
     */
    showLoading() {
        this.elements.loadingZone.show();
        this.elements.generatorBtn.prop('disabled', true);
    }
    
    /**
     * 로딩 상태 숨김
     */
    hideLoading() {
        this.elements.loadingZone.hide();
        this.elements.generatorBtn.prop('disabled', false);
    }
    
    /**
     * 로딩 상태 토글
     */
    toggleLoading(isLoading) {
        if (isLoading) {
            this.showLoading();
        } else {
            this.hideLoading();
        }
    }
    
    /**
     * 결과 영역 초기화
     */
    clearResults() {
        this.elements.queryImageZone.empty();
        this.elements.resultImageZone.empty();
        this.elements.jsonViewer.hide();
        this.clearError();
    }
    
    /**
     * 오류 메시지 표시
     */
    displayError(message) {
        this.elements.errorZone.text(message).show();
        console.error('UI Error:', message);
    }
    
    /**
     * 경고 메시지 표시
     */
    displayWarning(message) {
        // 경고는 에러보다 덜 강조되도록 스타일 구분
        this.elements.errorZone
            .text(message)
            .removeClass('error')
            .addClass('warning')
            .show();
        console.warn('UI Warning:', message);
    }
    
    /**
     * 오류 메시지 제거
     */
    clearError() {
        this.elements.errorZone.text('').hide().removeClass('warning error');
    }
    
    /**
     * 쿼리 이미지 표시
     */
    displayQueryImage(base64Image) {
        if (!base64Image) return;
        
        const img = $('<img>', {
            src: BASE64_PREFIX + base64Image,
            class: 'query_image',
            alt: '생성된 쿼리 이미지'
        });
        
        this.elements.queryImageZone.empty().append(img);
    }
    
    /**
     * 결과 이미지들 표시
     */
    displayResultImages(vectorResult) {
        if (!vectorResult || vectorResult.length === 0) {
            return;
        }
        
        this.elements.resultImageZone.empty();
        
        vectorResult.forEach((item, index) => {
            if (item.image && item.percents !== undefined) {
                const resultBlock = this.createResultBlock(item, index);
                this.elements.resultImageZone.append(resultBlock);
            }
        });
        
        // 이미지 로드 완료 후 애니메이션 효과 (선택사항)
        this.animateResults();
    }
    
    /**
     * 결과 블록 생성
     */
    createResultBlock(item, index) {
        const block = $('<div class="result_block">');
        
        const img = $('<img>', {
            src: BASE64_PREFIX + item.image,
            class: 'result_image',
            alt: `결과 이미지 ${index + 1}`,
            loading: 'lazy'  // 지연 로딩
        });
        
        const percent = $('<div class="result_percent">').text(
            `유사도: ${item.percents.toFixed(1)}%`
        );
        
        block.append(img, percent);
        return block;
    }
    
    /**
     * JSON 뷰어 표시
     */
    displayJson(data) {
        try {
            // JSON 뷰어 라이브러리 사용
            this.elements.jsonViewer.jsonViewer(data, {
                collapsed: true,  // 기본적으로 접힌 상태
                withQuotes: false,
                withLinks: false
            }).show();
        } catch (error) {
            console.error('JSON 뷰어 오류:', error);
            // 라이브러리 실패 시 기본 JSON 표시
            this.elements.jsonViewer
                .text(JSON.stringify(data, null, 2))
                .show();
        }
    }
    
    /**
     * 결과 애니메이션 효과
     */
    animateResults() {
        this.elements.resultImageZone.find('.result_block').each(function(index) {
            $(this).css('opacity', '0').delay(index * 100).animate({
                opacity: 1
            }, 300);
        });
    }
    
    /**
     * 입력값 초기화
     */
    resetInputs() {
        this.elements.promptInput.val('');
        this.elements.searchNumInput.val(DEFAULT_VALUES.SEARCH_NUM);
        this.clearResults();
    }
    
    /**
     * 설정값 적용 (프리셋 등에서 사용)
     */
    applySettings(settings) {
        if (settings.modelType) {
            this.elements.modelTypeSelect.val(settings.modelType);
        }
        if (settings.indexType) {
            this.elements.indexTypeSelect.val(settings.indexType);
        }
        if (settings.searchNum) {
            this.elements.searchNumInput.val(settings.searchNum);
        }
    }
    
    /**
     * 현재 설정값 가져오기
     */
    getCurrentSettings() {
        return {
            prompt: this.elements.promptInput.val().trim(),
            modelType: this.elements.modelTypeSelect.val(),
            indexType: this.elements.indexTypeSelect.val(),
            searchNum: parseInt(this.elements.searchNumInput.val(), 10)
        };
    }
}

// 전역으로 노출
window.UiManager = UiManager;