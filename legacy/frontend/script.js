// AI多Agent工作流平台 - 前端交互脚本

class WorkflowPlatform {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.currentLang = localStorage.getItem('language') || 'zh';
        this.chatMessages = [];
        this.isTyping = false;
        this.projectStatus = 'clarification';
        this.uploadedFiles = [];
        
        // API配置
        this.config = window.API_CONFIG?.getConfig() || {
            BASE_URL: 'http://localhost:8080/api/v1',
            ENDPOINTS: {}
        };
        this.sessionId = localStorage.getItem('sessionId') || null;
        this.authToken = localStorage.getItem('authToken') || null;
        
        // LLM服务
        this.llmService = new window.LLMService();
        
        this.init();
    }
    
    async init() {
        this.setupTheme();
        this.setupEventListeners();
        this.setupFileUpload();
        this.setupChat();
        
        // 初始化会话
        await this.initSession();
        
        this.loadInitialData();
    }
    
    // ==================== API服务层 ====================
    
    /**
     * 通用API请求方法
     */
    async apiRequest(endpoint, options = {}) {
        const url = `${this.config.BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(this.authToken && { 'Authorization': `Bearer ${this.authToken}` }),
                ...options.headers
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error?.message || '请求失败');
            }
            
            return await response.json();
        } catch (error) {
            console.error('API请求错误:', error);
            this.showNotification(`请求失败: ${error.message}`, 'error');
            throw error;
        }
    }
    
    /**
     * 初始化会话
     */
    async initSession() {
        if (!this.sessionId) {
            try {
                const response = await this.apiRequest('/sessions', {
                    method: 'POST',
                    body: JSON.stringify({
                        user_id: this.generateUserId(),
                        language: this.currentLang
                    })
                });
                
                this.sessionId = response.session_id;
                localStorage.setItem('sessionId', this.sessionId);
                console.log('会话创建成功:', this.sessionId);
                
            } catch (error) {
                console.error('创建会话失败:', error);
                // 使用本地模式
                this.sessionId = this.generateUserId();
            }
        }
    }
    
    /**
     * 发送聊天消息到API
     */
    async sendMessageToAPI(content, attachments = []) {
        try {
            const response = await this.apiRequest(`/sessions/${this.sessionId}/messages`, {
                method: 'POST',
                body: JSON.stringify({
                    content: content,
                    message_type: attachments.length > 0 ? 'file' : 'text',
                    attachments: attachments
                })
            });
            
            return response.bot_response;
        } catch (error) {
            console.error('发送消息失败:', error);
            return null;
        }
    }
    
    /**
     * 上传文件到API
     */
    async uploadFileToAPI(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('session_id', this.sessionId);
            
            const response = await fetch(`${this.config.BASE_URL}/files/upload`, {
                method: 'POST',
                headers: {
                    ...(this.authToken && { 'Authorization': `Bearer ${this.authToken}` })
                },
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('文件上传失败');
            }
            
            return await response.json();
        } catch (error) {
            console.error('文件上传错误:', error);
            this.showNotification(`文件上传失败: ${error.message}`, 'error');
            throw error;
        }
    }
    
    /**
     * 生成报价
     */
    async generateQuote(files = []) {
        try {
            const response = await this.apiRequest(`/sessions/${this.sessionId}/quote`, {
                method: 'POST',
                body: JSON.stringify({
                    mrd_id: this.mrdId,
                    services: ['ocr', 'tts']
                })
            });
            
            return response;
        } catch (error) {
            console.error('生成报价失败:', error);
            return null;
        }
    }
    
    /**
     * 创建支付
     */
    async createPayment(quoteId) {
        try {
            const response = await this.apiRequest('/payments/escrow', {
                method: 'POST',
                body: JSON.stringify({
                    quote_id: quoteId,
                    wallet_address: this.walletAddress,
                    payment_method: 'crossme'
                })
            });
            
            return response;
        } catch (error) {
            console.error('创建支付失败:', error);
            return null;
        }
    }
    
    /**
     * 获取项目状态
     */
    async getProjectStatus() {
        try {
            const response = await this.apiRequest(`/projects/${this.sessionId}/status`);
            return response;
        } catch (error) {
            console.error('获取项目状态失败:', error);
            return null;
        }
    }
    
    /**
     * 获取项目结果
     */
    async getProjectResults() {
        try {
            const response = await this.apiRequest(`/projects/${this.sessionId}/results`);
            return response;
        } catch (error) {
            console.error('获取项目结果失败:', error);
            return null;
        }
    }
    
    /**
     * 生成用户ID
     */
    generateUserId() {
        return 'user_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
    
    /**
     * 从API更新报价
     */
    async updateQuoteFromAPI() {
        try {
            const quoteData = await this.generateQuote();
            if (quoteData) {
                this.currentQuoteId = quoteData.quote_id;
                this.updateQuoteDisplay(quoteData);
            }
        } catch (error) {
            console.error('更新报价失败:', error);
            // 降级到本地计算
            this.updateQuote();
        }
    }
    
    /**
     * 更新报价显示
     */
    updateQuoteDisplay(quoteData) {
        // 更新任务列表
        const quoteRows = document.querySelectorAll('.quote-row');
        quoteData.tasks.forEach((task, index) => {
            if (quoteRows[index]) {
                const row = quoteRows[index];
                row.querySelector('.col-price').textContent = `$${task.price.toFixed(2)}`;
                row.querySelector('.col-time').textContent = task.estimated_time;
            }
        });
        
        // 更新总价
        document.querySelector('.summary-row:nth-child(1) span:last-child').textContent = `$${quoteData.subtotal.toFixed(2)}`;
        document.querySelector('.summary-row:nth-child(2) span:last-child').textContent = `$${quoteData.platform_fee.toFixed(2)}`;
        document.querySelector('.summary-row.total span:last-child').textContent = `$${quoteData.total.toFixed(2)}`;
        document.querySelector('#paymentButton').innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"/>
            </svg>
            立即支付 $${quoteData.total.toFixed(2)}
        `;
    }
    
    /**
     * 开始轮询项目状态
     */
    startStatusPolling() {
        this.statusPollingInterval = setInterval(async () => {
            try {
                const statusData = await this.getProjectStatus();
                if (statusData) {
                    this.updateTimelineFromAPI(statusData);
                    
                    // 如果项目完成，停止轮询
                    if (statusData.current_phase === 'completed') {
                        clearInterval(this.statusPollingInterval);
                        await this.handleProjectCompletion();
                    }
                }
            } catch (error) {
                console.error('获取项目状态失败:', error);
            }
        }, 5000); // 每5秒轮询一次
    }
    
    /**
     * 从API更新时间轴
     */
    updateTimelineFromAPI(statusData) {
        const timelineItems = document.querySelectorAll('.timeline-item');
        
        statusData.milestones.forEach((milestone, index) => {
            if (timelineItems[index]) {
                const item = timelineItems[index];
                const marker = item.querySelector('.timeline-marker');
                const percentage = item.querySelector('.timeline-percentage');
                const progressBar = item.querySelector('.progress-bar');
                
                // 更新状态类
                item.className = `timeline-item ${milestone.status}`;
                
                // 更新进度
                percentage.textContent = `${milestone.progress}%`;
                progressBar.style.width = `${milestone.progress}%`;
                
                // 更新标记图标
                if (milestone.status === 'completed') {
                    marker.innerHTML = `
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/>
                        </svg>
                    `;
                } else if (milestone.status === 'in_progress') {
                    marker.innerHTML = `<div class="loading-spinner"></div>`;
                }
            }
        });
    }
    
    /**
     * 处理项目完成
     */
    async handleProjectCompletion() {
        try {
            const results = await this.getProjectResults();
            if (results) {
                this.showNotification('🎉 项目完成！文件已准备好下载', 'success');
                this.enableDownloadWithResults(results);
                this.addBotMessage('🎉 项目完成！您可以在下方下载区域获取所有文件。');
            }
        } catch (error) {
            console.error('获取项目结果失败:', error);
            this.enableDownload(); // 降级到原有方法
        }
    }
    
    /**
     * 启用下载（带API结果）
     */
    enableDownloadWithResults(results) {
        const downloadButton = document.querySelector('.download-button');
        downloadButton.disabled = false;
        downloadButton.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 13.293a1 1 0 011.414 0L9 14.586V7a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"/>
            </svg>
            下载项目文件 (${results.deliverables.length} 个文件)
        `;
        
        downloadButton.addEventListener('click', () => {
            this.downloadFilesFromAPI(results);
        });
        
        this.updateTransactionHistory();
    }
    
    /**
     * 从API下载文件
     */
    async downloadFilesFromAPI(results) {
        try {
            this.showNotification('开始下载项目文件...', 'info');
            
            // 下载打包文件
            if (results.package_url) {
                const link = document.createElement('a');
                link.href = results.package_url;
                link.download = 'project_results.zip';
                link.click();
            } else {
                // 逐个下载文件
                for (const file of results.deliverables) {
                    const link = document.createElement('a');
                    link.href = file.download_url;
                    link.download = file.file_name;
                    link.click();
                    await new Promise(resolve => setTimeout(resolve, 500)); // 避免并发下载
                }
            }
            
            this.showNotification('下载完成！', 'success');
        } catch (error) {
            console.error('下载失败:', error);
            this.showNotification('下载失败，请稍后重试', 'error');
        }
    }
    
    /**
     * 显示建议按钮
     */
    showSuggestions(suggestions) {
        const chatMessages = document.getElementById('chatMessages');
        const suggestionsEl = document.createElement('div');
        suggestionsEl.className = 'suggestions fade-in';
        
        suggestionsEl.innerHTML = `
            <div class="suggestions-title">建议回复:</div>
            ${suggestions.map(suggestion => 
                `<button class="suggestion-btn" onclick="document.getElementById('messageInput').value='${suggestion}'">${suggestion}</button>`
            ).join('')}
        `;
        
        chatMessages.appendChild(suggestionsEl);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // ==================== 设置管理 ====================
    
    /**
     * 打开设置面板
     */
    openSettings() {
        const modal = document.getElementById('settingsModal');
        modal.classList.add('show');
        
        // 加载当前设置
        this.loadSettings();
        
        // 绑定事件监听器
        this.setupSettingsListeners();
    }
    
    /**
     * 关闭设置面板
     */
    closeSettings() {
        const modal = document.getElementById('settingsModal');
        modal.classList.remove('show');
    }
    
    /**
     * 加载当前设置
     */
    loadSettings() {
        const providerSelect = document.getElementById('llmProvider');
        const apiKeyInput = document.getElementById('apiKey');
        
        // 设置当前提供商
        providerSelect.value = this.llmService.provider;
        
        // 设置API密钥（部分显示）
        if (this.llmService.apiKey) {
            apiKeyInput.value = '*'.repeat(20);
        }
        
        // 更新API密钥组显示
        this.updateApiKeyVisibility();
        
        // 更新提供商信息
        this.updateProviderInfo();
        
        // 更新连接状态
        this.updateConnectionStatus();
    }
    
    /**
     * 设置事件监听器
     */
    setupSettingsListeners() {
        // 关闭按钮
        document.getElementById('closeSettings').onclick = () => this.closeSettings();
        document.getElementById('cancelSettings').onclick = () => this.closeSettings();
        
        // 点击遮罩关闭
        document.getElementById('settingsModal').onclick = (e) => {
            if (e.target.id === 'settingsModal') {
                this.closeSettings();
            }
        };
        
        // 提供商切换
        document.getElementById('llmProvider').onchange = (e) => {
            this.updateApiKeyVisibility();
            this.updateProviderInfo();
        };
        
        // API密钥显示/隐藏
        document.getElementById('toggleApiKey').onclick = () => {
            const input = document.getElementById('apiKey');
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
        };
        
        // 测试连接
        document.getElementById('testConnection').onclick = () => this.testConnection();
        
        // 保存设置
        document.getElementById('saveSettings').onclick = () => this.saveSettings();
    }
    
    /**
     * 更新API密钥输入框显示
     */
    updateApiKeyVisibility() {
        const provider = document.getElementById('llmProvider').value;
        const apiKeyGroup = document.getElementById('apiKeyGroup');
        const needsKey = this.llmService.providers[provider]?.needsKey;
        
        apiKeyGroup.style.display = needsKey ? 'block' : 'none';
    }
    
    /**
     * 更新提供商信息
     */
    updateProviderInfo() {
        const provider = document.getElementById('llmProvider').value;
        const providerInfo = document.getElementById('providerInfo');
        
        const infos = {
            mock: {
                title: '本地模拟模式',
                description: '使用预设的智能回复，无需API密钥，适合功能测试。',
                features: ['免费使用', '响应迅速', '功能完整', '无需配置']
            },
            openai: {
                title: 'OpenAI GPT',
                description: '使用OpenAI的GPT模型，需要API密钥。',
                features: ['高质量回复', '支持多轮对话', '理解能力强', '需要付费API']
            },
            deepseek: {
                title: 'DeepSeek',
                description: '国产大模型，性价比高，需要API密钥。',
                features: ['中文优化', '价格实惠', '响应快速', '支持长文本']
            },
            qianwen: {
                title: '通义千问',
                description: '阿里云的大模型服务，需要API密钥。',
                features: ['中文理解佳', '多模态支持', '企业级稳定', '丰富的API']
            },
            ollama: {
                title: 'Ollama本地部署',
                description: '本地运行的开源模型，需要先安装Ollama。',
                features: ['完全免费', '数据隐私', '可定制化', '需本地部署']
            }
        };
        
        const info = infos[provider];
        if (info) {
            providerInfo.innerHTML = `
                <h4>${info.title}</h4>
                <p>${info.description}</p>
                <ul>
                    ${info.features.map(feature => `<li>${feature}</li>`).join('')}
                </ul>
            `;
        }
    }
    
    /**
     * 更新连接状态
     */
    updateConnectionStatus() {
        const statusEl = document.getElementById('connectionStatus');
        const provider = this.llmService.provider;
        
        if (provider === 'mock') {
            statusEl.className = 'connection-status connected';
            statusEl.querySelector('span').textContent = '本地模拟模式';
        } else {
            statusEl.className = 'connection-status';
            statusEl.querySelector('span').textContent = '未连接';
        }
    }
    
    /**
     * 测试连接
     */
    async testConnection() {
        const testBtn = document.getElementById('testConnection');
        const statusEl = document.getElementById('connectionStatus');
        
        testBtn.disabled = true;
        testBtn.textContent = '测试中...';
        statusEl.className = 'connection-status connecting';
        statusEl.querySelector('span').textContent = '连接中...';
        
        try {
            const result = await this.llmService.testConnection();
            
            if (result.success) {
                statusEl.className = 'connection-status connected';
                statusEl.querySelector('span').textContent = '连接成功';
                this.showNotification('连接测试成功！', 'success');
            } else {
                statusEl.className = 'connection-status error';
                statusEl.querySelector('span').textContent = '连接失败';
                this.showNotification(`连接失败: ${result.message}`, 'error');
            }
        } catch (error) {
            statusEl.className = 'connection-status error';
            statusEl.querySelector('span').textContent = '连接错误';
            this.showNotification('连接测试失败', 'error');
        }
        
        testBtn.disabled = false;
        testBtn.textContent = '测试连接';
    }
    
    /**
     * 保存设置
     */
    saveSettings() {
        const provider = document.getElementById('llmProvider').value;
        const apiKey = document.getElementById('apiKey').value;
        
        // 保存提供商
        this.llmService.setProvider(provider);
        
        // 保存API密钥（如果不是星号）
        if (apiKey && !apiKey.startsWith('*')) {
            this.llmService.setApiKey(apiKey);
        }
        
        this.showNotification('设置已保存', 'success');
        this.closeSettings();
        
        // 更新连接状态
        setTimeout(() => {
            this.updateConnectionStatus();
        }, 500);
    }
    
    // 主题设置
    setupTheme() {
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        this.updateThemeIcon();
    }
    
    updateThemeIcon() {
        const themeToggle = document.getElementById('themeToggle');
        const icon = themeToggle.querySelector('.theme-icon');
        
        if (this.currentTheme === 'dark') {
            icon.innerHTML = `<path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/>`;
        } else {
            icon.innerHTML = `<path d="M10 2L13.09 8.26L20 9L14 14.74L15.18 21.02L10 17.77L4.82 21.02L6 14.74L0 9L6.91 8.26L10 2Z"/>`;
        }
    }
    
    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
        this.updateThemeIcon();
        
        // 添加过渡动画
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    }
    
    // 事件监听器设置
    setupEventListeners() {
        // 主题切换
        document.getElementById('themeToggle').addEventListener('click', () => {
            this.toggleTheme();
        });
        
        // 设置按钮
        document.getElementById('settingsToggle').addEventListener('click', () => {
            this.openSettings();
        });
        
        // 语言切换
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchLanguage(e.target.dataset.lang);
            });
        });
        
        // 开始项目按钮
        document.getElementById('startProject').addEventListener('click', () => {
            this.scrollToChat();
        });
        
        // 发送消息
        document.getElementById('sendMessage').addEventListener('click', () => {
            this.sendMessage();
        });
        
        // 回车发送消息
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // 支付按钮
        document.getElementById('paymentButton').addEventListener('click', () => {
            this.processPayment();
        });
        
        // 平滑滚动导航
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }
    
    // 语言切换
    switchLanguage(lang) {
        this.currentLang = lang;
        localStorage.setItem('language', lang);
        
        // 更新语言按钮状态
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });
        
        // 这里可以添加多语言文本替换逻辑
        this.updateLanguageTexts();
    }
    
    updateLanguageTexts() {
        const texts = {
            zh: {
                heroTitle: '智能化多Agent协作平台',
                heroSubtitle: '从需求澄清到成果交付，AI Agent自动化工作流让您的项目更高效',
                startProject: '开始项目',
                // 可以添加更多翻译
            },
            en: {
                heroTitle: 'AI-Powered Multi-Agent Workflow Platform',
                heroSubtitle: 'From requirement clarification to delivery, AI agents automate your workflow for maximum efficiency',
                startProject: 'Start Project',
                // 可以添加更多翻译
            }
        };
        
        const currentTexts = texts[this.currentLang];
        if (currentTexts) {
            document.querySelector('.hero-title').textContent = currentTexts.heroTitle;
            document.querySelector('.hero-subtitle').textContent = currentTexts.heroSubtitle;
            document.querySelector('#startProject span').textContent = currentTexts.startProject;
        }
    }
    
    // 文件上传设置
    setupFileUpload() {
        const uploadArea = document.getElementById('fileUpload');
        const fileInput = document.getElementById('fileInput');
        
        // 点击上传
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        // 文件选择
        fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });
        
        // 拖拽上传
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });
    }
    
    // 处理上传的文件
    async handleFiles(files) {
        for (const file of Array.from(files)) {
            if (this.validateFile(file)) {
                try {
                    // 显示上传中状态
                    this.showNotification(`正在上传 ${file.name}...`, 'info');
                    
                    // 调用API上传文件
                    const uploadResult = await this.uploadFileToAPI(file);
                    
                    if (uploadResult) {
                        // 保存文件信息
                        this.uploadedFiles.push({
                            local_file: file,
                            server_info: uploadResult
                        });
                        
                        this.displayUploadedFile(file, uploadResult);
                        this.showNotification(`${file.name} 上传成功`, 'success');
                        
                        // 更新报价
                        await this.updateQuoteFromAPI();
                    }
                } catch (error) {
                    this.showNotification(`${file.name} 上传失败`, 'error');
                    console.error('文件上传失败:', error);
                }
            }
        }
    }
    
    validateFile(file) {
        const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
        const maxSize = 10 * 1024 * 1024; // 10MB
        
        if (!allowedTypes.includes(file.type)) {
            this.showNotification('不支持的文件格式', 'error');
            return false;
        }
        
        if (file.size > maxSize) {
            this.showNotification('文件大小超过限制', 'error');
            return false;
        }
        
        return true;
    }
    
    displayUploadedFile(file) {
        const chatMessages = document.getElementById('chatMessages');
        const fileMessage = document.createElement('div');
        fileMessage.className = 'message user-message fade-in';
        
        fileMessage.innerHTML = `
            <div class="message-content">
                <div class="file-preview">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"/>
                    </svg>
                    <span>${file.name}</span>
                    <small>(${this.formatFileSize(file.size)})</small>
                </div>
                <span class="message-time">刚刚</span>
            </div>
            <div class="message-avatar">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z"/>
                </svg>
            </div>
        `;
        
        chatMessages.appendChild(fileMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // 模拟AI回复
        setTimeout(() => {
            this.addBotMessage(`收到文件：${file.name}。正在分析内容并更新报价...`);
        }, 1000);
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // 聊天功能设置
    setupChat() {
        this.chatMessages = [
            { type: 'bot', content: '您好！我是AI助手，可以帮您澄清项目需求。请告诉我您需要什么服务？', time: new Date() }
        ];
    }
    
    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        this.addUserMessage(message);
        input.value = '';
        
        // 调用API获取AI回复
        this.showTypingIndicator();
        
        try {
            // 优先使用LLM服务
            const botResponse = await this.llmService.generateResponse(message, this.chatMessages);
            this.hideTypingIndicator();
            
            if (botResponse && botResponse.content) {
                this.addBotMessage(botResponse.content);
                
                // 如果有建议回复，显示建议按钮
                if (botResponse.suggestions && botResponse.suggestions.length > 0) {
                    this.showSuggestions(botResponse.suggestions);
                }
            } else {
                // 降级到API调用
                const apiResponse = await this.sendMessageToAPI(message);
                if (apiResponse && apiResponse.content) {
                    this.addBotMessage(apiResponse.content);
                } else {
                    this.generateBotResponse(message);
                }
            }
        } catch (error) {
            this.hideTypingIndicator();
            // 最后降级到本地模拟
            this.generateBotResponse(message);
        }
    }
    
    addUserMessage(content) {
        const chatMessages = document.getElementById('chatMessages');
        const messageEl = document.createElement('div');
        messageEl.className = 'message user-message slide-up';
        
        messageEl.innerHTML = `
            <div class="message-content">
                <p>${this.escapeHtml(content)}</p>
                <span class="message-time">刚刚</span>
            </div>
            <div class="message-avatar">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z"/>
                </svg>
            </div>
        `;
        
        chatMessages.appendChild(messageEl);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        this.chatMessages.push({ type: 'user', content, time: new Date() });
    }
    
    addBotMessage(content) {
        const chatMessages = document.getElementById('chatMessages');
        const messageEl = document.createElement('div');
        messageEl.className = 'message bot-message slide-up';
        
        messageEl.innerHTML = `
            <div class="message-avatar">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1L13.5 2.5L16.17 5.17H7.83L10.5 2.5L9 1L3 7V9H21ZM12 8C13.1 8 14 8.9 14 10V22H10V10C10 8.9 10.9 8 12 8Z"/>
                </svg>
            </div>
            <div class="message-content">
                <p>${content}</p>
                <span class="message-time">刚刚</span>
            </div>
        `;
        
        chatMessages.appendChild(messageEl);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        this.chatMessages.push({ type: 'bot', content, time: new Date() });
    }
    
    generateBotResponse(userMessage) {
        const responses = [
            '明白了，我需要更多详细信息来为您生成准确的报价。',
            '根据您的需求，我推荐使用我们的Agent A进行图片处理，Agent B进行语音合成。',
            '请上传您的文件，这样我可以更好地估算处理时间和成本。',
            '您的项目看起来很有趣！让我为您制定一个详细的执行计划。',
            '基于您提供的信息，我已经更新了报价。请查看右侧的报价面板。'
        ];
        
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        this.addBotMessage(randomResponse);
    }
    
    showTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        indicator.classList.add('show');
        this.isTyping = true;
    }
    
    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        indicator.classList.remove('show');
        this.isTyping = false;
    }
    
    // 更新报价
    updateQuote() {
        const basePrice = 20.00;
        const fileCount = this.uploadedFiles.length;
        const additionalCost = fileCount * 5.00;
        const subtotal = basePrice + additionalCost;
        const platformFee = subtotal * 0.05;
        const total = subtotal + platformFee;
        
        // 更新报价显示
        document.querySelector('.summary-row:nth-child(1) span:last-child').textContent = `$${subtotal.toFixed(2)}`;
        document.querySelector('.summary-row:nth-child(2) span:last-child').textContent = `$${platformFee.toFixed(2)}`;
        document.querySelector('.summary-row.total span:last-child').textContent = `$${total.toFixed(2)}`;
        document.querySelector('#paymentButton').innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"/>
            </svg>
            立即支付 $${total.toFixed(2)}
        `;
        
        // 添加动画效果
        document.querySelector('.quote-summary').classList.add('slide-up');
        setTimeout(() => {
            document.querySelector('.quote-summary').classList.remove('slide-up');
        }, 300);
    }
    
    // 处理支付
    async processPayment() {
        this.showNotification('正在连接智能合约...', 'info');
        
        try {
            // 调用API创建支付
            const paymentResult = await this.createPayment(this.currentQuoteId);
            
            if (paymentResult && paymentResult.contract_address) {
                this.showNotification('智能合约创建成功，正在确认支付...', 'info');
                
                // 更新合约地址显示
                document.querySelector('.contract-address small').textContent = 
                    `合约地址: ${paymentResult.contract_address}`;
                
                // 模拟支付确认（实际应该跳转到钱包或支付页面）
                setTimeout(async () => {
                    try {
                        // 这里应该是支付确认的逻辑
                        this.showNotification('支付成功！项目已开始执行', 'success');
                        this.updateProjectStatus('payment');
                        this.startProjectExecution();
                        
                        // 开始轮询项目状态
                        this.startStatusPolling();
                        
                    } catch (error) {
                        this.showNotification('支付确认失败', 'error');
                    }
                }, 2000);
                
            } else {
                this.showNotification('创建智能合约失败', 'error');
            }
        } catch (error) {
            this.showNotification('支付处理失败', 'error');
            console.error('支付错误:', error);
        }
    }
    
    // 更新项目状态
    updateProjectStatus(status) {
        this.projectStatus = status;
        
        const statusMap = {
            'clarification': { text: '需求澄清', badge: 'active' },
            'quote': { text: '生成报价', badge: 'active' },
            'payment': { text: '等待支付', badge: 'completed' },
            'agent-a': { text: 'Agent A 执行', badge: 'active' },
            'agent-b': { text: 'Agent B 执行', badge: 'active' },
            'packaging': { text: '成果打包', badge: 'active' },
            'completed': { text: '项目完成', badge: 'completed' }
        };
        
        // 更新进度时间轴
        this.updateTimeline(status);
        
        // 更新支付状态
        if (status === 'payment') {
            document.querySelector('.escrow-status .status-badge').textContent = '已支付';
            document.querySelector('.escrow-status .status-badge').className = 'status-badge completed';
        }
    }
    
    // 更新时间轴
    updateTimeline(currentStatus) {
        const timeline = document.querySelectorAll('.timeline-item');
        const statusOrder = ['clarification', 'quote', 'payment', 'agent-a', 'agent-b', 'packaging'];
        const currentIndex = statusOrder.indexOf(currentStatus);
        
        timeline.forEach((item, index) => {
            const marker = item.querySelector('.timeline-marker');
            const percentage = item.querySelector('.timeline-percentage');
            const progressBar = item.querySelector('.progress-bar');
            
            if (index < currentIndex) {
                item.className = 'timeline-item completed';
                percentage.textContent = '100%';
                progressBar.style.width = '100%';
            } else if (index === currentIndex) {
                item.className = 'timeline-item active';
                // 模拟进度更新
                this.animateProgress(progressBar, percentage);
            } else {
                item.className = 'timeline-item pending';
                percentage.textContent = '0%';
                progressBar.style.width = '0%';
            }
        });
    }
    
    // 动画进度条
    animateProgress(progressBar, percentage) {
        let progress = 0;
        const targetProgress = Math.random() * 60 + 30; // 30-90%的随机进度
        
        const animation = setInterval(() => {
            progress += 2;
            progressBar.style.width = `${progress}%`;
            percentage.textContent = `${progress}%`;
            
            if (progress >= targetProgress) {
                clearInterval(animation);
            }
        }, 100);
    }
    
    // 开始项目执行
    startProjectExecution() {
        // 模拟Agent执行流程
        setTimeout(() => {
            this.updateProjectStatus('agent-a');
            this.addBotMessage('Agent A 开始处理您的图片文件...');
        }, 3000);
        
        setTimeout(() => {
            this.updateProjectStatus('agent-b');
            this.addBotMessage('Agent A 完成！Agent B 开始生成语音文件...');
        }, 8000);
        
        setTimeout(() => {
            this.updateProjectStatus('packaging');
            this.addBotMessage('Agent B 完成！正在打包最终成果...');
        }, 12000);
        
        setTimeout(() => {
            this.updateProjectStatus('completed');
            this.addBotMessage('🎉 项目完成！您可以在下方下载区域获取所有文件。');
            this.enableDownload();
        }, 15000);
    }
    
    // 启用下载
    enableDownload() {
        const downloadButton = document.querySelector('.download-button');
        downloadButton.disabled = false;
        downloadButton.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 13.293a1 1 0 011.414 0L9 14.586V7a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"/>
            </svg>
            下载项目文件
        `;
        
        downloadButton.addEventListener('click', () => {
            this.downloadFiles();
        });
        
        // 更新交易记录
        this.updateTransactionHistory();
    }
    
    // 下载文件
    downloadFiles() {
        this.showNotification('开始下载项目文件...', 'info');
        
        // 模拟文件下载
        setTimeout(() => {
            this.showNotification('下载完成！', 'success');
        }, 2000);
    }
    
    // 更新交易记录
    updateTransactionHistory() {
        const transactionList = document.querySelector('.transaction-list');
        const completedTransaction = document.createElement('div');
        completedTransaction.className = 'transaction-item fade-in';
        
        completedTransaction.innerHTML = `
            <div class="transaction-info">
                <span class="transaction-type">里程碑释放</span>
                <span class="transaction-time">${new Date().toLocaleString()}</span>
            </div>
            <span class="transaction-amount">$21.00</span>
        `;
        
        transactionList.appendChild(completedTransaction);
    }
    
    // 显示通知
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type} slide-up`;
        notification.textContent = message;
        
        // 添加样式
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '1000',
            maxWidth: '300px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
        });
        
        // 根据类型设置背景色
        const colors = {
            info: '#3B82F6',
            success: '#10B981',
            warning: '#F59E0B',
            error: '#EF4444'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // 自动移除
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    // 滚动到聊天区域
    scrollToChat() {
        document.querySelector('.chat-panel').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
        
        // 聚焦到输入框
        setTimeout(() => {
            document.getElementById('messageInput').focus();
        }, 500);
    }
    
    // HTML转义
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // 加载初始数据
    loadInitialData() {
        // 模拟加载动画
        document.querySelectorAll('.panel').forEach((panel, index) => {
            panel.style.opacity = '0';
            panel.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                panel.style.transition = 'all 0.5s ease';
                panel.style.opacity = '1';
                panel.style.transform = 'translateY(0)';
            }, index * 200);
        });
        
        // 清除过渡效果
        setTimeout(() => {
            document.querySelectorAll('.panel').forEach(panel => {
                panel.style.transition = '';
            });
        }, 2000);
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new WorkflowPlatform();
});

// 性能优化：图片懒加载
document.addEventListener('DOMContentLoaded', () => {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
});

// PWA支持
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
