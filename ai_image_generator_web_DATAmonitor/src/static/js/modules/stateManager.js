/*
 * @File: stateManager.js
 * @Date: 2025-08-05
 * @Author: SGM
 * @Brief: 애플리케이션 상태 관리자
 * @section MODIFYINFO 수정정보
 */

class StateManager {
    constructor() {
        this.state = {
            // API 관련 상태
            currentApi: 'imagen',
            availableApis: {},
            
            // UI 상태
            isLoading: false,
            currentPreset: null,
            
            // 설정 상태
            settings: {
                modelType: 'l14',
                indexType: 'cos',
                searchNum: 4
            },
            
            // 애플리케이션 설정
            config: null,
            
            // 결과 상태
            lastResult: null,
            queryImage: null,
            resultImages: []
        };
        
        this.subscribers = [];
        this.initialized = false;
    }
    
    /**
     * 상태 업데이트
     * @param {Object} newState - 업데이트할 상태
     */
    setState(newState) {
        const prevState = { ...this.state };
        this.state = { ...this.state, ...newState };
        
        // 상태 변경을 구독자들에게 알림
        this.notifySubscribers(prevState, this.state);
        
        console.log('State updated:', newState);
    }
    
    /**
     * 현재 상태 반환
     * @param {string} key - 특정 상태 키 (선택사항)
     * @returns {*} 상태 값
     */
    getState(key = null) {
        if (key) {
            return this.state[key];
        }
        return { ...this.state };
    }
    
    /**
     * 상태 변경 구독
     * @param {Function} callback - 상태 변경 시 호출될 콜백
     */
    subscribe(callback) {
        this.subscribers.push(callback);
        
        // 구독 해제 함수 반환
        return () => {
            const index = this.subscribers.indexOf(callback);
            if (index > -1) {
                this.subscribers.splice(index, 1);
            }
        };
    }
    
    /**
     * 구독자들에게 상태 변경 알림
     * @param {Object} prevState - 이전 상태
     * @param {Object} newState - 새로운 상태
     */
    notifySubscribers(prevState, newState) {
        this.subscribers.forEach(callback => {
            try {
                callback(newState, prevState);
            } catch (error) {
                console.error('Error in state subscriber:', error);
            }
        });
    }
    
    /**
     * 서버에서 설정 로드
     */
    async loadConfig() {
        try {
            const response = await fetch('/config');
            if (response.ok) {
                const data = await response.json();
                this.setState({
                    config: data.config,
                    availableApis: data.apis
                });
                this.initialized = true;
                console.log('애플리케이션 설정 로드 완료');
            } else {
                console.error('설정 로드 실패:', response.status);
            }
        } catch (error) {
            console.error('설정 로드 중 오류:', error);
        }
    }
    
    /**
     * API 변경
     * @param {string} apiName - 새로운 API 이름
     */
    setCurrentApi(apiName) {
        if (this.state.availableApis[apiName]) {
            this.setState({ currentApi: apiName });
            console.log(`API 변경: ${apiName}`);
        } else {
            console.error(`알 수 없는 API: ${apiName}`);
        }
    }
    
    /**
     * 설정 업데이트
     * @param {Object} newSettings - 새로운 설정
     */
    updateSettings(newSettings) {
        this.setState({
            settings: { ...this.state.settings, ...newSettings }
        });
    }
    
    /**
     * 로딩 상태 변경
     * @param {boolean} isLoading - 로딩 여부
     */
    setLoading(isLoading) {
        this.setState({ isLoading });
    }
    
    /**
     * 결과 데이터 설정
     * @param {Object} result - API 응답 결과
     */
    setResult(result) {
        this.setState({
            lastResult: result,
            queryImage: result.queryImage || null,
            resultImages: result.vectorResult || []
        });
    }
    
    /**
     * 결과 초기화
     */
    clearResults() {
        this.setState({
            lastResult: null,
            queryImage: null,
            resultImages: []
        });
    }
    
    /**
     * 상태 초기화 여부 확인
     * @returns {boolean} 초기화 완료 여부
     */
    isInitialized() {
        return this.initialized;
    }
}

// 전역 상태 관리자 인스턴스
const appState = new StateManager();

// 페이지 로드 시 설정 자동 로드
document.addEventListener('DOMContentLoaded', () => {
    appState.loadConfig();
});

// 전역으로 노출 (다른 스크립트에서 사용할 수 있도록)
window.appState = appState;