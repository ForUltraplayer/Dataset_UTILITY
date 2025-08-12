/*
 * @File: apiClient.js
 * @Date: 2025-08-05
 * @Author: SGM
 * @Brief: API 통신 클라이언트 모듈
 * @section MODIFYINFO 수정정보
 */

class ApiClient {
    constructor() {
        this.baseUrl = '';  // 현재 호스트 사용
        this.defaultTimeout = 600000; // 600초 (10분) - 백엔드와 동일하게 설정
    }
    
    /**
     * 이미지 생성 API 호출
     */
    async generateImage(data, apiName = null) {
        const endpoint = apiName ? `/create/${apiName}` : API_ENDPOINTS.CREATE;
        
        console.log('ApiClient.generateImage 호출:', { data, apiName, endpoint });
        
        try {
            const response = await this.makeRequest('POST', endpoint, data);
            console.log('ApiClient 응답 성공:', response);
            return response;
        } catch (error) {
            console.error('ApiClient 오류:', error);
            throw this.handleApiError(error);
        }
    }
    
    /**
     * 서버 설정 정보 가져오기
     */
    async getConfig() {
        try {
            const response = await this.makeRequest('GET', '/config');
            return response;
        } catch (error) {
            console.error('설정 로드 실패:', error);
            return null;
        }
    }
    
    /**
     * 서버 상태 확인
     */
    async checkHealth() {
        try {
            const response = await this.makeRequest('GET', '/health');
            return response;
        } catch (error) {
            console.error('헬스체크 실패:', error);
            return null;
        }
    }
    
    /**
     * API 연결 상태 확인
     */
    async checkApiStatus() {
        try {
            const response = await this.makeRequest('GET', '/api-status');
            return response;
        } catch (error) {
            console.error('API 상태 확인 실패:', error);
            return null;
        }
    }
    
    /**
     * HTTP 요청 실행
     */
    async makeRequest(method, endpoint, data = null) {
        return new Promise((resolve, reject) => {
            const ajaxOptions = {
                url: this.baseUrl + endpoint,
                type: method,
                timeout: this.defaultTimeout,
                success: (response, textStatus, jqXHR) => {
                    resolve(response);
                },
                error: (jqXHR, textStatus, errorThrown) => {
                    const error = this.parseError(jqXHR, textStatus, errorThrown);
                    reject(error);
                }
            };
            
            if (data && (method === 'POST' || method === 'PUT')) {
                ajaxOptions.contentType = 'application/json';
                ajaxOptions.data = JSON.stringify(data);
            }
            
            $.ajax(ajaxOptions);
        });
    }
    
    /**
     * 오류 응답 파싱
     */
    parseError(jqXHR, textStatus, errorThrown) {
        let errorInfo = {
            status: jqXHR.status,
            statusText: jqXHR.statusText,
            textStatus: textStatus,
            errorThrown: errorThrown,
            response: null
        };
        
        try {
            if (jqXHR.responseText) {
                errorInfo.response = JSON.parse(jqXHR.responseText);
            }
        } catch (e) {
            errorInfo.response = { detail: jqXHR.responseText };
        }
        
        return errorInfo;
    }
    
    /**
     * API 오류 처리
     */
    handleApiError(error) {
        // 구체적인 오류 정보 생성
        const processedError = {
            message: '알 수 없는 오류가 발생했습니다.',
            type: 'unknown',
            status: error.status,
            response: error.response
        };
        
        if (error.textStatus === 'timeout') {
            processedError.message = '요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.';
            processedError.type = 'timeout';
        } else if (error.textStatus === 'error') {
            if (error.status === 0) {
                processedError.message = '서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.';
                processedError.type = 'network';
            } else if (error.response && error.response.detail) {
                processedError.message = error.response.detail;
                processedError.type = error.response.error_type || 'server_error';
            }
        }
        
        return processedError;
    }
    
    /**
     * 요청 타임아웃 설정
     */
    setTimeout(timeout) {
        this.defaultTimeout = timeout;
    }
}

// 전역으로 노출
window.ApiClient = ApiClient;