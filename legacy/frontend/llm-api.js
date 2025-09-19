// 大模型API集成模块

class LLMService {
    constructor() {
        this.config = window.API_CONFIG?.getConfig() || {};
        this.apiKey = localStorage.getItem('llm_api_key') || '';
        this.provider = localStorage.getItem('llm_provider') || 'mock'; // mock, openai, deepseek, qianwen
        
        // API配置
        this.providers = {
            mock: {
                name: '本地模拟',
                url: null,
                needsKey: false
            },
            deepseek: {
                name: 'DeepSeek',
                url: 'https://api.aimlapi.com/v1/chat/completions',
                needsKey: true,
                model: 'deepseek-chat'
            }

        };
        
        this.systemPrompt = `你是AI工作流平台的智能助手，专门帮助用户澄清项目需求。

你的职责：
1. 通过对话了解用户的具体需求
2. 询问关键信息：输入文件类型、期望输出格式、质量要求、时间要求等
3. 基于需求推荐合适的Agent服务组合
4. 解释服务流程和预期结果
5. 提供专业建议和最佳实践

当前可用服务：
- Agent A: 图片OCR文字识别（支持JPG、PNG、PDF）
- Agent B: 文字转语音合成（支持多种语音、语言）

请用友好、专业的语调与用户交流，主动询问必要信息。`;
    }
    
    /**
     * 生成AI回复
     */
    async generateResponse(userMessage, conversationHistory = []) {
        try {
            switch (this.provider) {
                case 'openai':
                    return await this.callOpenAI(userMessage, conversationHistory);
                case 'deepseek':
                    return await this.callDeepSeek(userMessage, conversationHistory);
                case 'qianwen':
                    return await this.callQianwen(userMessage, conversationHistory);
                case 'ollama':
                    return await this.callOllama(userMessage, conversationHistory);
                default:
                    return this.mockResponse(userMessage);
            }
        } catch (error) {
            console.error('LLM API调用失败:', error);
            // 降级到模拟响应
            return this.mockResponse(userMessage);
        }
    }
    
    
    /**
     * 调用DeepSeek API (通过AIML API代理)
     */
    async callDeepSeek(userMessage, history) {
        const messages = this.buildMessages(userMessage, history);
        
        const response = await fetch(this.providers.deepseek.url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: this.providers.deepseek.model,
                messages: messages,
                max_tokens: 1000,
                temperature: 0.7
            })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`DeepSeek API错误 (${response.status}): ${errorText}`);
        }
        
        const data = await response.json();
        
        // 检查响应格式
        if (data.choices && data.choices[0] && data.choices[0].message) {
            return {
                content: data.choices[0].message.content,
                suggestions: this.extractSuggestions(data.choices[0].message.content),
                requires_clarification: this.needsClarification(userMessage)
            };
        } else {
            throw new Error(`DeepSeek API响应格式错误: ${JSON.stringify(data)}`);
        }
    }
    
    /**
     * 调用通义千问API
     */
    async callQianwen(userMessage, history) {
        const messages = this.buildQianwenMessages(userMessage, history);
        
        const response = await fetch(this.providers.qianwen.url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify({
                model: this.providers.qianwen.model,
                input: {
                    messages: messages
                },
                parameters: {
                    max_tokens: 1000,
                    temperature: 0.7
                }
            })
        });
        
        if (!response.ok) {
            throw new Error(`通义千问API错误: ${response.status}`);
        }
        
        const data = await response.json();
        return {
            content: data.output.text,
            suggestions: this.extractSuggestions(data.output.text),
            requires_clarification: this.needsClarification(userMessage)
        };
    }
    
    
    /**
     * 模拟AI回复
     */
    mockResponse(userMessage) {
        const responses = [
            {
                trigger: ['图片', '图像', 'ocr', '文字识别', '识别'],
                response: '我了解您需要图片文字识别服务。请告诉我：\n\n1. 您有多少张图片需要处理？\n2. 图片中的文字是什么语言？\n3. 对识别准确率有什么要求？\n4. 需要保留原有格式还是纯文本即可？\n\n我会为您推荐最合适的处理方案。',
                suggestions: ['我有10张中文图片', '需要高精度识别', '保留原始格式']
            },
            {
                trigger: ['语音', '音频', 'tts', '文字转语音', '朗读'],
                response: '明白，您需要文字转语音服务。请提供一些详细信息：\n\n1. 文字内容大概有多少字？\n2. 希望使用什么语言和口音？\n3. 对语音的音质有什么要求？\n4. 需要什么格式的音频文件？\n\n这样我能为您生成更准确的报价。',
                suggestions: ['中文普通话', '高音质MP3', '大约1000字']
            },
            {
                trigger: ['多少钱', '价格', '费用', '报价', '成本'],
                response: '我们的定价非常透明：\n\n📸 图片文字识别：每张图片 $2-5（根据复杂度）\n🎵 文字转语音：每1000字 $3-8（根据语音质量）\n\n具体价格取决于：\n• 文件数量和大小\n• 处理复杂度\n• 质量要求\n• 加急程度\n\n上传文件后我会给出精确报价。',
                suggestions: ['上传我的文件', '了解质量标准', '查看处理时间']
            },
            {
                trigger: ['流程', '怎么做', '如何', '步骤'],
                response: '我们的AI工作流程很简单：\n\n1️⃣ **需求澄清** - 我们现在正在做的\n2️⃣ **文件上传** - 您上传需要处理的文件\n3️⃣ **智能报价** - 系统自动生成详细报价\n4️⃣ **安全支付** - 通过智能合约托管资金\n5️⃣ **AI处理** - Agent自动执行任务\n6️⃣ **质量检查** - 自动质检确保结果质量\n7️⃣ **成果交付** - 打包下载所有文件\n\n整个过程透明可追踪，资金安全有保障。',
                suggestions: ['开始上传文件', '了解智能合约', '查看示例结果']
            },
            {
                trigger: ['时间', '多久', '多长时间', '什么时候'],
                response: '处理时间取决于任务复杂度：\n\n⚡ **图片文字识别**：通常5-15分钟\n🎵 **文字转语音**：通常3-10分钟\n📦 **打包交付**：1-2分钟\n\n**影响因素：**\n• 文件数量和大小\n• 当前系统负载\n• 处理质量要求\n\n我们会在报价时给出准确的预计时间，并实时更新进度。',
                suggestions: ['了解加急服务', '查看实时进度', '优化处理时间']
            }
        ];
        
        // 寻找匹配的回复
        const matchedResponse = responses.find(r => 
            r.trigger.some(trigger => 
                userMessage.toLowerCase().includes(trigger)
            )
        );
        
        if (matchedResponse) {
            return {
                content: matchedResponse.response,
                suggestions: matchedResponse.suggestions,
                requires_clarification: true
            };
        }
        
        // 默认回复
        const defaultResponses = [
            '我明白了！为了给您提供最佳服务方案，能详细说说您的具体需求吗？比如需要处理什么类型的文件？',
            '好的，我来帮您分析一下。请告诉我更多详情，这样我能推荐最合适的Agent来处理您的任务。',
            '很有趣的需求！为了确保服务质量，请详细描述一下您希望达到的效果，我会制定最优的执行方案。',
            '收到！让我们一步步明确需求。请描述一下您的文件类型和期望的输出结果，我会为您匹配最适合的AI Agent。'
        ];
        
        return {
            content: defaultResponses[Math.floor(Math.random() * defaultResponses.length)],
            suggestions: ['上传文件查看', '了解服务详情', '获取价格估算'],
            requires_clarification: true
        };
    }
    
    /**
     * 构建消息格式
     */
    buildMessages(userMessage, history) {
        const messages = [
            { role: 'system', content: this.systemPrompt }
        ];
        
        // 添加历史对话（最近10轮）
        const recentHistory = history.slice(-10);
        recentHistory.forEach(msg => {
            messages.push({
                role: msg.type === 'user' ? 'user' : 'assistant',
                content: msg.content
            });
        });
        
        // 添加当前用户消息
        messages.push({ role: 'user', content: userMessage });
        
        return messages;
    }
    
    /**
     * 构建通义千问消息格式
     */
    buildQianwenMessages(userMessage, history) {
        const messages = [
            { role: 'system', content: this.systemPrompt }
        ];
        
        const recentHistory = history.slice(-10);
        recentHistory.forEach(msg => {
            messages.push({
                role: msg.type === 'user' ? 'user' : 'assistant',
                content: msg.content
            });
        });
        
        messages.push({ role: 'user', content: userMessage });
        
        return messages;
    }
    
    /**
     * 提取建议回复
     */
    extractSuggestions(response) {
        // 简单的建议提取逻辑
        const suggestions = [];
        
        if (response.includes('图片') || response.includes('识别')) {
            suggestions.push('上传图片文件');
        }
        if (response.includes('语音') || response.includes('音频')) {
            suggestions.push('了解语音服务');
        }
        if (response.includes('价格') || response.includes('费用')) {
            suggestions.push('查看详细报价');
        }
        
        return suggestions.length > 0 ? suggestions : ['继续对话', '上传文件', '查看服务'];
    }
    
    /**
     * 判断是否需要进一步澄清
     */
    needsClarification(userMessage) {
        const clarificationKeywords = ['什么', '怎么', '如何', '为什么', '多少', '哪个', '哪些'];
        return clarificationKeywords.some(keyword => userMessage.includes(keyword));
    }
    
    /**
     * 设置API密钥
     */
    setApiKey(key) {
        this.apiKey = key;
        localStorage.setItem('llm_api_key', key);
    }
    
    /**
     * 设置服务提供商
     */
    setProvider(provider) {
        if (this.providers[provider]) {
            this.provider = provider;
            localStorage.setItem('llm_provider', provider);
            return true;
        }
        return false;
    }
    
    /**
     * 获取可用的服务提供商
     */
    getProviders() {
        return this.providers;
    }
    
    /**
     * 测试API连接
     */
    async testConnection() {
        try {
            console.log(`测试 ${this.provider} 连接...`);
            
            if (this.provider === 'mock') {
                console.log('API URL: 本地模拟模式');
                console.log('API Key: 不需要');
            } else {
                console.log(`API URL: ${this.providers[this.provider]?.url}`);
                console.log(`API Key: ${this.apiKey ? '已设置' : '未设置'}`);
                
                // 检查是否需要API密钥但未设置
                if (this.providers[this.provider]?.needsKey && !this.apiKey) {
                    throw new Error('请先设置API密钥');
                }
            }
            
            const testResponse = await this.generateResponse('Hello, this is a test message.');
            
            console.log('测试响应:', testResponse);
            
            return {
                success: true,
                message: this.provider === 'mock' ? '本地模拟模式工作正常' : '连接成功',
                response: testResponse
            };
        } catch (error) {
            console.error('连接测试失败:', error);
            return {
                success: false,
                message: error.message,
                response: null
            };
        }
    }
}

// 导出服务
if (typeof window !== 'undefined') {
    window.LLMService = LLMService;
}
