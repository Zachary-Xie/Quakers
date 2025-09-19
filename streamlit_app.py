#!/usr/bin/env python3
"""
AI多智能体工作流平台 - Streamlit版本
GitHub部署友好的单文件应用
"""

import streamlit as st
import requests
import json
import time
import uuid
import os
import tempfile
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any
import io
from PIL import Image

# 页面配置
st.set_page_config(
    page_title="AI Multi-Agent Workflow Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 参考原版设计
st.markdown("""
<style>
    /* 主题色彩 */
    :root {
        --primary-color: #3B82F6;
        --accent-color: #9333EA;
        --success-color: #10B981;
        --background-color: #F9FAFB;
        --card-background: #FFFFFF;
        --text-primary: #1F2937;
        --text-secondary: #6B7280;
        --border-color: #E5E7EB;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 主容器样式 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* 主标题样式 */
    .main-header {
        text-align: center;
        color: var(--primary-color);
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-subtitle {
        text-align: center;
        color: var(--text-secondary);
        font-size: 1.25rem;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    /* 聊天消息样式 */
    .chat-message {
        padding: 1.25rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        animation: slideIn 0.3s ease-out;
    }
    
    .user-message {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-left: 4px solid var(--primary-color);
        margin-left: 2rem;
        position: relative;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #F5F5F5 0%, #EEEEEE 100%);
        border-left: 4px solid var(--accent-color);
        margin-right: 2rem;
        position: relative;
    }
    
    .message-avatar {
        position: absolute;
        left: -2rem;
        top: 50%;
        transform: translateY(-50%);
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    
    .user-avatar {
        background: linear-gradient(135deg, var(--primary-color), #1E40AF);
        color: white;
    }
    
    .assistant-avatar {
        background: linear-gradient(135deg, var(--accent-color), #7C3AED);
        color: white;
    }
    
    /* 面板样式 */
    .panel {
        background: var(--card-background);
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid var(--border-color);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .panel:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .panel-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* 状态卡片 */
    .status-card {
        background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
        border: 1px solid #0EA5E9;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .status-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, var(--primary-color), var(--accent-color));
    }
    
    /* 指标卡片 */
    .metric-card {
        background: var(--card-background);
        border-radius: 1rem;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }
    
    .metric-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.875rem;
    }
    
    /* 时间轴样式 */
    .timeline-item {
        display: flex;
        align-items: center;
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 0.75rem;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .timeline-item.completed {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border-left: 4px solid var(--success-color);
    }
    
    .timeline-item.pending {
        background: linear-gradient(135deg, #FFF7ED 0%, #FED7AA 100%);
        border-left: 4px solid #F59E0B;
    }
    
    .timeline-item.waiting {
        background: linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 100%);
        border-left: 4px solid #9CA3AF;
    }
    
    .timeline-icon {
        font-size: 1.5rem;
        margin-right: 1rem;
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }
    
    .timeline-content {
        flex: 1;
    }
    
    .timeline-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
    }
    
    .timeline-description {
        color: var(--text-secondary);
        font-size: 0.875rem;
    }
    
    /* 按钮样式 */
    .stButton > button {
        border-radius: 0.75rem;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, var(--primary-color) 0%, #1E40AF 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
    }
    
    /* 文件上传区域 */
    .uploadedFile {
        border-radius: 1rem;
        border: 2px dashed var(--border-color);
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .uploadedFile:hover {
        border-color: var(--primary-color);
        background: #F8FAFC;
    }
    
    /* 进度条样式 */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        border-radius: 1rem;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
    }
    
    /* 动画效果 */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .chat-message {
            margin-left: 0;
            margin-right: 0;
        }
        
        .user-message, .assistant-message {
            margin-left: 0;
            margin-right: 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# LLM服务类
class LLMService:
    def __init__(self):
        self.providers = {
            'mock': {'name': 'Local Mock', 'needsKey': False},
            'openai': {'name': 'OpenAI GPT', 'needsKey': True, 'url': 'https://api.openai.com/v1/chat/completions'},
            'deepseek': {'name': 'DeepSeek', 'needsKey': True, 'url': 'https://api.aimlapi.com/v1/chat/completions'},
            'qianwen': {'name': 'Qianwen', 'needsKey': True, 'url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'},
        }
    
    async def generate_response(self, message: str, provider: str, api_key: str = None, history: List = None) -> Dict:
        """Generate AI response"""
        if provider == 'mock':
            return self._mock_response(message)
        
        if not api_key and self.providers[provider]['needsKey']:
            return {"error": "API key required"}
        
        try:
            if provider == 'openai':
                return await self._call_openai(message, api_key, history or [])
            elif provider == 'deepseek':
                return await self._call_deepseek(message, api_key, history or [])
            elif provider == 'qianwen':
                return await self._call_qianwen(message, api_key, history or [])
        except Exception as e:
            return {"error": f"API call failed: {str(e)}"}
    
    def _mock_response(self, message: str) -> Dict:
        """Mock response"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["image", "picture", "photo", "ocr", "text recognition"]):
            return {
                "content": "I see you mentioned image processing needs. I can help you use OCR technology to recognize text in images and convert it to Markdown format. Please upload your image file.",
                "suggestions": ["Upload Image File", "View OCR Service Details", "Get Quote"]
            }
        elif any(word in message_lower for word in ["voice", "audio", "tts", "speech", "sound"]):
            return {
                "content": "I understand you need text-to-speech service. I can convert your text into high-quality audio files. Please enter the text content you want to convert.",
                "suggestions": ["Enter Text Content", "Choose Voice Type", "Preview Voice Sample"]
            }
        else:
            return {
                "content": "Hello! I'm the AI assistant for the workflow platform. I can help you with:\n\n🖼️ **Image Text Recognition**: Convert text in images to Markdown format\n🔊 **Text-to-Speech**: Convert text to high-quality audio files\n\nPlease tell me what you need help with.",
                "suggestions": ["Upload Image File", "Enter Text to Convert", "View Service Pricing"]
            }
    
    async def _call_openai(self, message: str, api_key: str, history: List) -> Dict:
        """Call OpenAI API"""
        messages = [{"role": "system", "content": "You are an AI assistant for a workflow platform, specializing in OCR and TTS tasks."}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post(self.providers['openai']['url'], headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return {"content": result['choices'][0]['message']['content']}
        else:
            return {"error": f"OpenAI API Error: {response.status_code}"}
    
    async def _call_deepseek(self, message: str, api_key: str, history: List) -> Dict:
        """Call DeepSeek API"""
        messages = [{"role": "system", "content": "You are an AI assistant for a workflow platform, specializing in OCR and TTS tasks."}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post(self.providers['deepseek']['url'], headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return {"content": result['choices'][0]['message']['content']}
        else:
            return {"error": f"DeepSeek API Error: {response.status_code}"}

# TTS服务类
class TTSService:
    def __init__(self):
        self.voices = {
            "21m00Tcm4TlvDq8ikWAM": "Rachel - 英语女声",
            "AZnzlk1XvdvUeBnXmlld": "Domi - 英语女声", 
            "EXAVITQu4vr4xnSDxMaL": "Bella - 英语女声",
            "ErXwobaYiN019PkySvjV": "Antoni - 英语男声",
            "MF3mGyEYCl7XYWbV9V6O": "Elli - 英语女声",
            "TxGEqnHWrfWFTfGW9XjX": "Josh - 英语男声"
        }
    
    def generate_tts_mock(self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> Dict:
        """模拟TTS生成"""
        return {
            "task_id": str(uuid.uuid4()),
            "status": "completed",
            "text": text,
            "voice_id": voice_id,
            "voice_name": self.voices.get(voice_id, "未知语音"),
            "duration": len(text) * 0.1,
            "file_size": len(text) * 100,
            "qc_report": {
                "score": 92.5,
                "audio_quality": 90.0,
                "text_accuracy": 95.0,
                "voice_consistency": 88.0,
                "issues": [],
                "recommendations": ["语音质量优秀"]
            }
        }
    
    def generate_tts_with_elevenlabs(self, text: str, voice_id: str, api_key: str) -> Dict:
        """使用ElevenLabs API生成TTS"""
        if not api_key:
            return {"error": "需要ElevenLabs API密钥"}
        
        url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice_id
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return {
                    "task_id": str(uuid.uuid4()),
                    "status": "completed",
                    "audio_data": response.content,
                    "content_type": "audio/mpeg"
                }
            else:
                return {"error": f"ElevenLabs API错误: {response.status_code}"}
        except Exception as e:
            return {"error": f"TTS生成失败: {str(e)}"}

# OCR服务类
class OCRService:
    def __init__(self):
        pass
    
    def extract_text_mock(self, image_data: bytes) -> Dict:
        """模拟OCR文字提取"""
        return {
            "task_id": str(uuid.uuid4()),
            "status": "completed",
            "extracted_text": "这是从图像中提取的示例文本内容。\n\n## 识别结果\n\n实际项目中，这里会显示OCR识别出的真实文本内容，并格式化为Markdown格式。",
            "confidence": 0.95,
            "qc_report": {
                "score": 88.0,
                "text_quality": 90.0,
                "image_quality": 85.0,
                "recognition_accuracy": 92.0,
                "issues": ["部分字符置信度较低"],
                "recommendations": ["建议提高图像分辨率"]
            }
        }

# 初始化服务
@st.cache_resource
def get_services():
    return {
        'llm': LLMService(),
        'tts': TTSService(),
        'ocr': OCRService()
    }

def main():
    """主应用函数"""
    services = get_services()
    
    # Hero Section
    st.markdown("<h1 class='main-header'>🤖 AI Multi-Agent Workflow Platform</h1>", unsafe_allow_html=True)
    st.markdown("<p class='main-subtitle'>Transform your content with intelligent OCR and TTS services</p>", unsafe_allow_html=True)
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # LLM Configuration
        st.subheader("🧠 AI Model Settings")
        llm_provider = st.selectbox(
            "Choose AI Service Provider",
            options=list(services['llm'].providers.keys()),
            format_func=lambda x: services['llm'].providers[x]['name']
        )
        
        llm_api_key = ""
        if services['llm'].providers[llm_provider]['needsKey']:
            llm_api_key = st.text_input(
                "API Key", 
                type="password",
                help=f"Enter your {services['llm'].providers[llm_provider]['name']} API key"
            )
        
        # TTS Configuration
        st.subheader("🎵 Text-to-Speech Settings")
        use_elevenlabs = st.checkbox("Use ElevenLabs TTS", help="Requires ElevenLabs API key")
        
        elevenlabs_api_key = ""
        if use_elevenlabs:
            elevenlabs_api_key = st.text_input(
                "ElevenLabs API Key",
                type="password"
            )
        
        voice_id = st.selectbox(
            "Select Voice",
            options=list(services['tts'].voices.keys()),
            format_func=lambda x: services['tts'].voices[x]
        )
        
        # Clear Chat History
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # 初始化会话状态
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "project_data" not in st.session_state:
        st.session_state.project_data = {
            "files": [],
            "quotes": [],
            "tasks": []
        }
    
    # 主界面三列布局
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown('<div class="panel"><div class="panel-header">💬 Smart Conversation</div>', unsafe_allow_html=True)
        
        # Display Chat History
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div class="message-avatar user-avatar">👤</div>
                        <strong>You:</strong><br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="message-avatar assistant-avatar">🤖</div>
                        <strong>Assistant:</strong><br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # File Upload
        uploaded_file = st.file_uploader(
            "📁 Upload Image File (OCR)",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            help="Supports PNG, JPG, JPEG, PDF formats"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            if uploaded_file.type.startswith('image'):
                st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            
            if st.button("🔍 Start OCR Recognition"):
                with st.spinner("Recognizing text in image..."):
                    # Process OCR
                    image_data = uploaded_file.read()
                    ocr_result = services['ocr'].extract_text_mock(image_data)
                    
                    if ocr_result["status"] == "completed":
                        st.session_state.project_data["files"].append({
                            "type": "ocr",
                            "filename": uploaded_file.name,
                            "result": ocr_result
                        })
                        
                        # Add to chat history
                        st.session_state.messages.append({
                            "role": "user",
                            "content": f"Uploaded image file: {uploaded_file.name}"
                        })
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"✅ OCR Recognition Completed!\n\n**Extracted Text:**\n{ocr_result['extracted_text']}\n\n**Quality Score:** {ocr_result['qc_report']['score']}/100"
                        })
                        st.rerun()
        
        # Chat Input
        user_input = st.text_input("💭 Enter your question or request:", key="chat_input")
        
        if st.button("Send", key="send_message") and user_input:
            # 添加用户消息
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Generate AI response
            with st.spinner("AI is thinking..."):
                history = [{"role": msg["role"], "content": msg["content"]} 
                          for msg in st.session_state.messages[-5:]]  # Keep only last 5 messages as context
                
                import asyncio
                try:
                    # Since Streamlit doesn't support async, use synchronous approach
                    if llm_provider == 'mock':
                        response = services['llm']._mock_response(user_input)
                    else:
                        # API calls need to be synchronous here
                        response = {"content": "Sorry, external API calls are temporarily unavailable in Streamlit environment. Please use Local Mock mode."}
                except Exception as e:
                    response = {"error": str(e)}
                
                if "error" in response:
                    ai_response = f"❌ {response['error']}"
                else:
                    ai_response = response["content"]
                
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="panel"><div class="panel-header">💰 Quote & Payment</div>', unsafe_allow_html=True)
        
        # Generate Quote
        if st.button("📊 Generate Project Quote"):
            quote = {
                "quote_id": str(uuid.uuid4()),
                "tasks": [
                    {
                        "name": "Image OCR Recognition",
                        "description": "Recognize text in images and convert to Markdown format",
                        "price": 50.0,
                        "estimated_time": "5-10 minutes"
                    },
                    {
                        "name": "Text-to-Speech",
                        "description": "Convert text to high-quality audio files",
                        "price": 30.0,
                        "estimated_time": "3-8 minutes"
                    }
                ],
                "total_price": 80.0,
                "currency": "USD",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            st.session_state.project_data["quotes"].append(quote)
            st.success("✅ Quote generated successfully!")
        
        # Display Quote
        if st.session_state.project_data["quotes"]:
            latest_quote = st.session_state.project_data["quotes"][-1]
            
            st.markdown(f"""
            <div class="status-card">
                <h4>📋 Latest Quote</h4>
                <p><strong>Quote ID:</strong> {latest_quote['quote_id'][:8]}...</p>
                <p><strong>Total Price:</strong> ${latest_quote['total_price']}</p>
                <p><strong>Created:</strong> {latest_quote['created_at']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📝 Task Details")
            for task in latest_quote["tasks"]:
                with st.expander(f"{task['name']} - ${task['price']}"):
                    st.write(f"**Description:** {task['description']}")
                    st.write(f"**Estimated Time:** {task['estimated_time']}")
            
            # Mock Payment
            if st.button("💳 Confirm Payment"):
                st.session_state.project_data["payment_status"] = "completed"
                st.success("✅ Payment successful! Project started.")
        
        # TTS Function
        st.subheader("🎵 Text-to-Speech")
        tts_text = st.text_area("Enter text to convert:", height=100)
        
        if st.button("🔊 Generate Speech") and tts_text:
            with st.spinner("Generating speech..."):
                if use_elevenlabs and elevenlabs_api_key:
                    tts_result = services['tts'].generate_tts_with_elevenlabs(
                        tts_text, voice_id, elevenlabs_api_key
                    )
                else:
                    tts_result = services['tts'].generate_tts_mock(tts_text, voice_id)
                
                if "error" in tts_result:
                    st.error(f"❌ {tts_result['error']}")
                else:
                    st.success("✅ Speech generated successfully!")
                    
                    # Display TTS results
                    if "audio_data" in tts_result:
                        st.audio(tts_result["audio_data"], format="audio/mp3")
                    
                    # Display QC Report
                    if "qc_report" in tts_result:
                        qc = tts_result["qc_report"]
                        st.markdown(f"""
                        **QC Quality Report:**
                        - Overall Score: {qc['score']}/100
                        - Audio Quality: {qc['audio_quality']}/100
                        - Text Accuracy: {qc['text_accuracy']}/100
                        - Voice Consistency: {qc['voice_consistency']}/100
                        """)
                    
                    # Save to project data
                    st.session_state.project_data["files"].append({
                        "type": "tts",
                        "text": tts_text,
                        "result": tts_result
                    })
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="panel"><div class="panel-header">📈 Project Progress</div>', unsafe_allow_html=True)
        
        # Progress Timeline
        timeline_stages = [
            {"name": "Requirements", "status": "completed", "progress": 100},
            {"name": "Quote Generation", "status": "completed" if st.session_state.project_data["quotes"] else "pending", "progress": 100 if st.session_state.project_data["quotes"] else 0},
            {"name": "Payment", "status": "completed" if st.session_state.project_data.get("payment_status") == "completed" else "pending", "progress": 100 if st.session_state.project_data.get("payment_status") == "completed" else 0},
            {"name": "Processing", "status": "completed" if st.session_state.project_data["files"] else "pending", "progress": 100 if st.session_state.project_data["files"] else 0},
            {"name": "Quality Check", "status": "completed" if st.session_state.project_data["files"] else "pending", "progress": 100 if st.session_state.project_data["files"] else 0},
            {"name": "Delivery", "status": "completed" if len(st.session_state.project_data["files"]) >= 2 else "pending", "progress": 100 if len(st.session_state.project_data["files"]) >= 2 else 0}
        ]
        
        for i, stage in enumerate(timeline_stages):
            if stage["status"] == "completed":
                icon = "✅"
                css_class = "completed"
            elif stage["status"] == "pending":
                icon = "⏳"
                css_class = "pending"
            else:
                icon = "⭕"
                css_class = "waiting"
            
            st.markdown(f"""
            <div class="timeline-item {css_class}">
                <div class="timeline-icon">{icon}</div>
                <div class="timeline-content">
                    <div class="timeline-title">{stage['name']}</div>
                    <div class="timeline-description">Progress: {stage['progress']}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if stage["progress"] > 0:
                st.progress(stage["progress"] / 100)
        
        # Project Statistics
        st.subheader("📊 Project Statistics")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{len(st.session_state.project_data['files'])}</div>
                <div class="metric-label">Files Processed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{len(st.session_state.project_data['quotes'])}</div>
                <div class="metric-label">Quotes Generated</div>
            </div>
            """, unsafe_allow_html=True)
        
        # File Results
        if st.session_state.project_data["files"]:
            st.subheader("📁 Processing Results")
            for i, file_data in enumerate(st.session_state.project_data["files"]):
                with st.expander(f"{file_data['type'].upper()} - {file_data.get('filename', f'Task {i+1}')}"):
                    if file_data["type"] == "ocr":
                        st.markdown("**Extracted Text:**")
                        st.text_area("", value=file_data["result"]["extracted_text"], height=100, disabled=True, key=f"ocr_{i}")
                        st.markdown(f"**Confidence:** {file_data['result']['confidence']:.2%}")
                    elif file_data["type"] == "tts":
                        st.markdown(f"**Original Text:** {file_data['text']}")
                        if "qc_report" in file_data["result"]:
                            st.markdown(f"**Quality Score:** {file_data['result']['qc_report']['score']}/100")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
