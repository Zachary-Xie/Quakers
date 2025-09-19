// API配置文件
const API_CONFIG = {
    // 基础配置
    BASE_URL: 'http://localhost:8080/api/v1',
    
    // 环境配置
    ENVIRONMENT: 'development', // development, staging, production
    
    // 超时设置
    TIMEOUT: 30000, // 30秒
    
    // 重试配置
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000, // 1秒
    
    // API端点
    ENDPOINTS: {
        // 会话管理
        SESSIONS: '/sessions',
        SESSION_BY_ID: (id) => `/sessions/${id}`,
        
        // 聊天对话
        MESSAGES: (sessionId) => `/sessions/${sessionId}/messages`,
        MESSAGE_HISTORY: (sessionId, limit = 50, offset = 0) => 
            `/sessions/${sessionId}/messages?limit=${limit}&offset=${offset}`,
        
        // 文件管理
        FILE_UPLOAD: '/files/upload',
        FILE_INFO: (fileId) => `/files/${fileId}`,
        
        // MRD和报价
        GENERATE_MRD: (sessionId) => `/sessions/${sessionId}/mrd`,
        GENERATE_QUOTE: (sessionId) => `/sessions/${sessionId}/quote`,
        QUOTE_BY_ID: (quoteId) => `/quotes/${quoteId}`,
        
        // 支付和合约
        CREATE_ESCROW: '/payments/escrow',
        CONFIRM_PAYMENT: (escrowId) => `/payments/${escrowId}/confirm`,
        TRANSACTION_HISTORY: (sessionId) => `/payments/transactions?session_id=${sessionId}`,
        
        // 项目管理
        PROJECT_STATUS: (sessionId) => `/projects/${sessionId}/status`,
        PROJECT_RESULTS: (sessionId) => `/projects/${sessionId}/results`,
        PROJECT_DOWNLOAD: (sessionId) => `/projects/${sessionId}/download`,
        
        // Agent任务
        AGENT_TASK: (agentType, taskId) => `/agents/${agentType}/tasks/${taskId}`,
        
        // Webhook
        CROSSME_WEBHOOK: '/webhooks/crossme'
    },
    
    // 外部服务配置
    EXTERNAL_SERVICES: {
        // CrossMe智能合约
        CROSSME: {
            API_URL: 'https://api.crossme.io/v1',
            TESTNET_URL: 'https://testnet-api.crossme.io/v1',
            EXPLORER_URL: 'https://explorer.crossme.io'
        },
        
        // 大模型服务（如果直接调用）
        LLM_SERVICES: {
            OPENAI: {
                API_URL: 'https://api.openai.com/v1',
                MODEL: 'gpt-4'
            },
            ANTHROPIC: {
                API_URL: 'https://api.anthropic.com/v1',
                MODEL: 'claude-3-sonnet-20240229'
            }
        }
    },
    
    // 错误代码映射
    ERROR_CODES: {
        'INVALID_REQUEST': '请求参数错误',
        'UNAUTHORIZED': '未授权访问',
        'FORBIDDEN': '禁止访问',
        'NOT_FOUND': '资源不存在',
        'RATE_LIMITED': '请求频率限制',
        'SERVER_ERROR': '服务器内部错误',
        'NETWORK_ERROR': '网络连接错误',
        'TIMEOUT_ERROR': '请求超时',
        'FILE_TOO_LARGE': '文件过大',
        'UNSUPPORTED_FORMAT': '不支持的文件格式',
        'INSUFFICIENT_FUNDS': '余额不足',
        'PAYMENT_FAILED': '支付失败',
        'CONTRACT_ERROR': '合约执行错误'
    },
    
    // 文件上传限制
    FILE_LIMITS: {
        MAX_SIZE: 10 * 1024 * 1024, // 10MB
        ALLOWED_TYPES: [
            'image/jpeg',
            'image/png', 
            'image/webp',
            'application/pdf',
            'text/plain'
        ],
        MAX_FILES_PER_SESSION: 20
    },
    
    // 轮询配置
    POLLING: {
        PROJECT_STATUS_INTERVAL: 5000, // 5秒
        MAX_POLLING_DURATION: 300000, // 5分钟
        EXPONENTIAL_BACKOFF: true
    },
    
    // 缓存配置
    CACHE: {
        SESSION_DURATION: 24 * 60 * 60 * 1000, // 24小时
        FILE_INFO_DURATION: 60 * 60 * 1000, // 1小时
        QUOTE_DURATION: 30 * 60 * 1000 // 30分钟
    },
    
    // 通知配置
    NOTIFICATIONS: {
        DURATION: 3000, // 3秒
        MAX_VISIBLE: 5,
        POSITIONS: {
            DEFAULT: 'top-right',
            MOBILE: 'top-center'
        }
    },
    
    // 环境特定配置
    getConfig() {
        const baseConfig = this;
        
        switch (this.ENVIRONMENT) {
            case 'production':
                return {
                    ...baseConfig,
                    BASE_URL: 'https://api.aiworkflow.com/v1',
                    EXTERNAL_SERVICES: {
                        ...baseConfig.EXTERNAL_SERVICES,
                        CROSSME: {
                            ...baseConfig.EXTERNAL_SERVICES.CROSSME,
                            API_URL: 'https://api.crossme.io/v1'
                        }
                    }
                };
                
            case 'staging':
                return {
                    ...baseConfig,
                    BASE_URL: 'https://staging-api.aiworkflow.com/v1',
                    EXTERNAL_SERVICES: {
                        ...baseConfig.EXTERNAL_SERVICES,
                        CROSSME: {
                            ...baseConfig.EXTERNAL_SERVICES.CROSSME,
                            API_URL: baseConfig.EXTERNAL_SERVICES.CROSSME.TESTNET_URL
                        }
                    }
                };
                
            default: // development
                return baseConfig;
        }
    },
    
    // 获取完整的API URL
    getApiUrl(endpoint) {
        const config = this.getConfig();
        return `${config.BASE_URL}${endpoint}`;
    },
    
    // 获取错误消息
    getErrorMessage(errorCode) {
        return this.ERROR_CODES[errorCode] || '未知错误';
    },
    
    // 验证文件类型和大小
    validateFile(file) {
        const errors = [];
        
        if (file.size > this.FILE_LIMITS.MAX_SIZE) {
            errors.push(`文件大小超过限制 (${this.FILE_LIMITS.MAX_SIZE / 1024 / 1024}MB)`);
        }
        
        if (!this.FILE_LIMITS.ALLOWED_TYPES.includes(file.type)) {
            errors.push('不支持的文件格式');
        }
        
        return {
            valid: errors.length === 0,
            errors
        };
    }
};

// 导出配置（如果在模块环境中）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API_CONFIG;
}

// 全局可访问（浏览器环境）
if (typeof window !== 'undefined') {
    window.API_CONFIG = API_CONFIG;
}
