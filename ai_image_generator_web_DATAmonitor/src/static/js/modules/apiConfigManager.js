/**
 * @File: apiConfigManager.js
 * @Date: 2025-08-06
 * @Brief: API 엔드포인트 설정 관리 모듈
 */

const ApiConfigManager = {
    endpoints: [],
    currentUrl: '',
    connectionStatus: 'checking', // 'connected', 'disconnected', 'checking'
    statusCheckInterval: null,
    
    async init() {
        console.log('ApiConfigManager 초기화 시작...');
        try {
            await this.loadEndpoints();
            this.setupEventListeners();
            this.updateUI();
            this.startConnectionMonitoring();
            console.log('ApiConfigManager 초기화 완료');
        } catch (error) {
            console.error('API Config Manager 초기화 실패:', error);
            this.showMessage('API 설정 로드 실패: ' + error.message, 'error');
        }
    },

    async loadEndpoints() {
        console.log('API 엔드포인트 로드 시작...');
        try {
            const response = await fetch('/api-endpoints');
            console.log('API 엔드포인트 응답 상태:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('API 엔드포인트 응답 데이터:', data);
            
            this.endpoints = data.predefined_endpoints || [];
            this.currentUrl = data.current_url || '';
            
            console.log('로드된 엔드포인트 개수:', this.endpoints.length);
            console.log('현재 URL:', this.currentUrl);
        } catch (error) {
            console.error('API 엔드포인트 로드 실패:', error);
            throw error;
        }
    },

    setupEventListeners() {
        console.log('이벤트 리스너 설정 시작...');
        
        // 설정 토글 (전체 헤더 클릭 가능)
        const configHeader = document.querySelector('.config_header');
        const toggleBtn = document.getElementById('toggle_config_btn');
        const configContent = document.getElementById('config_content');
        
        console.log('설정 헤더:', configHeader);
        console.log('토글 버튼:', toggleBtn);
        console.log('설정 컨텐츠:', configContent);
        
        if (configHeader && configContent && toggleBtn) {
            const toggleConfig = () => {
                console.log('설정 패널 토글됨');
                const isVisible = configContent.style.display !== 'none';
                configContent.style.display = isVisible ? 'none' : 'block';
                toggleBtn.textContent = isVisible ? '▼' : '▲';
                console.log('패널 상태 변경:', isVisible ? '숨김' : '표시');
            };
            
            configHeader.addEventListener('click', toggleConfig);
            console.log('설정 헤더 클릭 이벤트 리스너 등록 완료');
        } else {
            console.error('설정 헤더, 토글 버튼 또는 설정 컨텐츠를 찾을 수 없음');
        }

        // 커스텀 URL 설정 버튼
        const setCustomBtn = document.getElementById('set_custom_url_btn');
        const customInput = document.getElementById('custom_url_input');
        
        console.log('커스텀 버튼:', setCustomBtn);
        console.log('커스텀 입력:', customInput);
        
        if (setCustomBtn && customInput) {
            setCustomBtn.addEventListener('click', () => {
                console.log('커스텀 URL 버튼 클릭됨');
                const customUrl = customInput.value.trim();
                if (customUrl) {
                    this.changeApiUrl(customUrl);
                }
            });

            // Enter 키로도 설정 가능
            customInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    console.log('Enter 키 눌림');
                    const customUrl = customInput.value.trim();
                    if (customUrl) {
                        this.changeApiUrl(customUrl);
                    }
                }
            });
            console.log('커스텀 URL 이벤트 리스너 등록 완료');
        } else {
            console.error('커스텀 URL 요소들을 찾을 수 없음');
        }

        // 새로고침 버튼
        const refreshBtn = document.getElementById('refresh_connection_btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                console.log('연결 상태 새로고침 버튼 클릭됨');
                this.checkConnectionStatus(true);
            });
            console.log('새로고침 버튼 이벤트 리스너 등록 완료');
        } else {
            console.error('새로고침 버튼을 찾을 수 없음');
        }
    },

    updateUI() {
        this.updateCurrentUrlDisplay();
        this.createEndpointButtons();
        this.updateConnectionStatusUI();
    },

    updateCurrentUrlDisplay() {
        const currentUrlElement = document.getElementById('current_api_url');
        if (currentUrlElement) {
            currentUrlElement.textContent = this.currentUrl || '알 수 없음';
        }
    },

    createEndpointButtons() {
        const buttonsContainer = document.getElementById('endpoint_buttons');
        if (!buttonsContainer) return;

        buttonsContainer.innerHTML = '';

        this.endpoints.forEach((endpoint, index) => {
            const button = document.createElement('button');
            button.className = 'endpoint_btn';
            button.textContent = endpoint.name;
            button.title = endpoint.description;
            
            // 현재 URL과 일치하면 active 클래스 추가
            if (endpoint.url === this.currentUrl) {
                button.classList.add('active');
            }

            button.addEventListener('click', () => {
                this.changeApiUrl(endpoint.url);
            });

            buttonsContainer.appendChild(button);
        });
    },

    async changeApiUrl(newUrl) {
        if (!newUrl) {
            alert('URL을 입력하세요.');
            return;
        }

        if (!newUrl.startsWith('http://') && !newUrl.startsWith('https://')) {
            alert('올바른 URL 형식이 아닙니다. http:// 또는 https://로 시작해야 합니다.');
            return;
        }

        try {
            const response = await fetch('/change-api-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: newUrl })
            });

            const data = await response.json();

            if (response.ok) {
                this.currentUrl = newUrl;
                this.updateCurrentUrlDisplay();
                this.updateButtonStates();
                
                // 커스텀 URL 입력 필드 초기화
                const customInput = document.getElementById('custom_url_input');
                if (customInput) {
                    customInput.value = '';
                }

                // 연결 상태 즉시 확인
                this.checkConnectionStatus(true);

                // 성공 메시지 표시 (선택적)
                this.showMessage(`API URL이 변경되었습니다: ${newUrl}`, 'success');
                
                console.log('API URL 변경 성공:', data);
            } else {
                throw new Error(data.detail || 'API URL 변경 실패');
            }
        } catch (error) {
            console.error('API URL 변경 오류:', error);
            this.showMessage(`API URL 변경 실패: ${error.message}`, 'error');
        }
    },

    updateButtonStates() {
        const buttons = document.querySelectorAll('.endpoint_btn');
        buttons.forEach(button => {
            const endpoint = this.endpoints.find(ep => ep.name === button.textContent);
            if (endpoint && endpoint.url === this.currentUrl) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
    },

    showMessage(message, type = 'info') {
        // 간단한 메시지 표시 (기존 error_zone 활용)
        const errorZone = document.getElementById('error_zone');
        if (errorZone) {
            errorZone.textContent = message;
            errorZone.style.color = type === 'error' ? 'red' : 
                                   type === 'success' ? 'green' : 'blue';
            
            // 3초 후 메시지 제거
            setTimeout(() => {
                errorZone.textContent = '';
            }, 3000);
        } else {
            // error_zone이 없으면 alert 사용
            alert(message);
        }
    },

    // 연결 상태 모니터링 시작
    startConnectionMonitoring() {
        console.log('연결 상태 모니터링 시작');
        // 초기 상태 확인
        this.checkConnectionStatus();
        
        // 30초마다 상태 확인
        this.statusCheckInterval = setInterval(() => {
            this.checkConnectionStatus();
        }, 30000);
    },

    // 연결 상태 확인
    async checkConnectionStatus(showAnimation = false) {
        console.log('API 연결 상태 확인 중...');
        
        // 확인 중 상태로 설정
        this.setConnectionStatus('checking');
        
        // 새로고침 버튼 애니메이션
        if (showAnimation) {
            const refreshBtn = document.getElementById('refresh_connection_btn');
            if (refreshBtn) {
                refreshBtn.classList.add('spinning');
            }
        }

        try {
            const response = await fetch('/api-status', {
                method: 'GET',
                cache: 'no-cache'
            });

            const data = await response.json();

            if (response.ok && data.status === 'connected') {
                this.setConnectionStatus('connected');
                console.log('API 연결 상태: 정상');
            } else {
                this.setConnectionStatus('disconnected');
                console.log('API 연결 상태: 실패', data);
            }
        } catch (error) {
            console.error('연결 상태 확인 실패:', error);
            this.setConnectionStatus('disconnected');
        } finally {
            // 새로고침 버튼 애니메이션 제거
            if (showAnimation) {
                setTimeout(() => {
                    const refreshBtn = document.getElementById('refresh_connection_btn');
                    if (refreshBtn) {
                        refreshBtn.classList.remove('spinning');
                    }
                }, 1000);
            }
        }
    },

    // 연결 상태 설정
    setConnectionStatus(status) {
        const previousStatus = this.connectionStatus;
        this.connectionStatus = status;
        
        // UI 업데이트
        this.updateConnectionStatusUI();
        
        // 상태 변경 시 플래시 효과
        if (previousStatus !== status && previousStatus !== 'checking') {
            this.flashStatusChange(status);
        }
    },

    // 연결 상태 UI 업데이트
    updateConnectionStatusUI() {
        const statusDot = document.getElementById('status_dot');
        const statusText = document.getElementById('connection_status_text');
        
        if (!statusDot || !statusText) return;

        // 기존 클래스 제거
        statusDot.className = 'status_dot';
        statusText.className = '';

        // 상태별 클래스 및 텍스트 설정
        switch (this.connectionStatus) {
            case 'connected':
                statusDot.classList.add('connected');
                statusText.classList.add('connected');
                statusText.textContent = '연결됨';
                break;
            case 'disconnected':
                statusDot.classList.add('disconnected');
                statusText.classList.add('disconnected');
                statusText.textContent = '연결 실패';
                break;
            case 'checking':
            default:
                statusDot.classList.add('checking');
                statusText.classList.add('checking');
                statusText.textContent = '연결 확인 중...';
                break;
        }
    },

    // 상태 변경 플래시 효과
    flashStatusChange(newStatus) {
        const statusDot = document.getElementById('status_dot');
        if (!statusDot) return;

        const flashClass = newStatus === 'connected' ? 'flash-success' : 'flash-error';
        
        statusDot.classList.add(flashClass);
        setTimeout(() => {
            statusDot.classList.remove(flashClass);
        }, 600);
    },

    // 정리 함수 (페이지 언로드시 호출)
    cleanup() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
            this.statusCheckInterval = null;
        }
    }
};

// 페이지 언로드시 정리
window.addEventListener('beforeunload', () => {
    if (window.ApiConfigManager) {
        window.ApiConfigManager.cleanup();
    }
});

// 전역에서 사용할 수 있도록 window 객체에 추가
window.ApiConfigManager = ApiConfigManager;