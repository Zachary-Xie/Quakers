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
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式 - 完全按照原始设计
st.markdown("""
<style>
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* 全局样式重置 */
    .main .block-container {
        padding-top: 0;
        padding-bottom: 0;
        max-width: 100%;
        margin: 0;
    }
    
    /* 隐藏Streamlit默认组件样式 */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #D1D5DB;
        padding: 0.75rem;
        font-size: 0.9rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid #D1D5DB;
        padding: 0.75rem;
        font-size: 0.9rem;
    }
    
    .stSelectbox > div > div > div {
        border-radius: 8px;
    }
    
    .stFileUploader > div {
        border-radius: 8px;
        border: 2px dashed #D1D5DB;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #3B82F6;
        background: #F8FAFC;
    }
    
    /* 顶部导航栏 */
    .top-nav {
        background: #FFFFFF;
        padding: 1rem 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        height: 60px;
    }
    
    .nav-brand {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.2rem;
        font-weight: 600;
        color: #1F2937;
    }
    
    .nav-brand-icon {
        width: 32px;
        height: 32px;
        background: #3B82F6;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
    }
    
    .nav-menu {
        display: flex;
        gap: 2rem;
        align-items: center;
    }
    
    .nav-link {
        color: #6B7280;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s;
    }
    
    .nav-link:hover {
        color: #3B82F6;
    }
    
    .nav-actions {
        display: flex;
        gap: 1rem;
        align-items: center;
    }
    
    /* Hero区域 */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 120px 2rem 80px;
        text-align: center;
        color: white;
        margin-top: 60px;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 2rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .hero-cta {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: #FFFFFF;
        color: #3B82F6;
        padding: 1rem 2rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .hero-cta:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    
    /* 主要内容区域 */
    .main-content {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 2rem;
    }
    
    /* 卡片样式 */
    .card {
        background: #FFFFFF;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    
    .card-header {
        padding: 1.5rem 1.5rem 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1F2937;
        border-bottom: 1px solid #F3F4F6;
    }
    
    .card-body {
        padding: 1.5rem;
    }
    
    /* 聊天区域 */
    .chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background: #F9FAFB;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .chat-message {
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
    }
    
    .chat-message.user {
        flex-direction: row-reverse;
    }
    
    .chat-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        font-weight: 600;
        flex-shrink: 0;
    }
    
    .chat-avatar.user {
        background: #3B82F6;
        color: white;
    }
    
    .chat-avatar.assistant {
        background: #10B981;
        color: white;
    }
    
    .chat-bubble {
        max-width: 70%;
        padding: 0.75rem 1rem;
        border-radius: 18px;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    .chat-bubble.user {
        background: #3B82F6;
        color: white;
        border-bottom-right-radius: 6px;
    }
    
    .chat-bubble.assistant {
        background: #FFFFFF;
        color: #1F2937;
        border: 1px solid #E5E7EB;
        border-bottom-left-radius: 6px;
    }
    
    /* 输入区域 */
    .chat-input-container {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    .chat-input {
        flex: 1;
        padding: 0.75rem 1rem;
        border: 1px solid #D1D5DB;
        border-radius: 24px;
        outline: none;
        font-size: 0.9rem;
        transition: border-color 0.3s;
    }
    
    .chat-input:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .send-button {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #3B82F6;
        color: white;
        border: none;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .send-button:hover {
        background: #2563EB;
        transform: scale(1.1);
    }
    
    /* 报价表格 */
    .quote-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1rem;
    }
    
    .quote-table th {
        background: #F9FAFB;
        padding: 0.75rem;
        text-align: left;
        font-weight: 600;
        color: #374151;
        border-bottom: 1px solid #E5E7EB;
        font-size: 0.9rem;
    }
    
    .quote-table td {
        padding: 0.75rem;
        border-bottom: 1px solid #F3F4F6;
        font-size: 0.9rem;
        color: #1F2937;
    }
    
    .quote-table .service-icon {
        width: 20px;
        height: 20px;
        display: inline-block;
        margin-right: 0.5rem;
        vertical-align: middle;
    }
    
    .quote-table .price {
        font-weight: 600;
        color: #059669;
    }
    
    .quote-total {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        background: #F9FAFB;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .quote-total .total-price {
        font-size: 1.2rem;
        color: #059669;
    }
    
    /* 支付按钮 */
    .payment-button {
        width: 100%;
        padding: 1rem;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .payment-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    }
    
    /* 进度时间轴 */
    .timeline {
        position: relative;
    }
    
    .timeline-item {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        position: relative;
    }
    
    .timeline-icon {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        font-weight: 600;
        margin-right: 1rem;
        z-index: 2;
    }
    
    .timeline-icon.completed {
        background: #10B981;
        color: white;
    }
    
    .timeline-icon.pending {
        background: #F59E0B;
        color: white;
    }
    
    .timeline-icon.waiting {
        background: #D1D5DB;
        color: #6B7280;
    }
    
    .timeline-content {
        flex: 1;
    }
    
    .timeline-title {
        font-weight: 600;
        color: #1F2937;
        margin-bottom: 0.25rem;
        font-size: 0.95rem;
    }
    
    .timeline-description {
        color: #6B7280;
        font-size: 0.85rem;
    }
    
    .timeline-progress {
        color: #3B82F6;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* 统计卡片 */
    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .stat-card {
        background: #F9FAFB;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #3B82F6;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: #6B7280;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* 文件上传区域 */
    .upload-area {
        border: 2px dashed #D1D5DB;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .upload-area:hover {
        border-color: #3B82F6;
        background: #F8FAFC;
    }
    
    .upload-icon {
        font-size: 2rem;
        color: #9CA3AF;
        margin-bottom: 1rem;
    }
    
    .upload-text {
        color: #6B7280;
        font-size: 0.9rem;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-content {
            grid-template-columns: 1fr;
            padding: 1rem;
        }
        
        .hero-title {
            font-size: 2rem;
        }
        
        .nav-menu {
            display: none;
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
        """Mock AI response"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["image", "picture", "photo", "ocr", "text recognition", "extract"]):
            return {
                "content": "I see you mentioned image processing needs. I can help you use OCR technology to recognize text in images and convert it to Markdown format. Please upload your image file.",
                "suggestions": ["Upload Image File", "View OCR Service Details", "Get Quote"]
            }
        elif any(word in message_lower for word in ["voice", "audio", "tts", "speech", "sound"]):
            return {
                "content": "I understand you need text-to-speech services. I can convert your text into high-quality audio files. Please enter the text content you want to convert.",
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
    
    # 顶部导航栏
    st.markdown("""
    <div class="top-nav">
        <div class="nav-brand">
            <div class="nav-brand-icon">AI</div>
            <span>AI Workflow</span>
        </div>
        <div class="nav-menu">
            <a href="#" class="nav-link">How it Works</a>
            <a href="#" class="nav-link">My Orders</a>
            <a href="/Admin" class="nav-link" style="color: #3B82F6; font-weight: 600;">⚙️ Admin</a>
        </div>
        <div class="nav-actions">
            <span style="color: #6B7280; font-size: 0.9rem;">EN</span>
            <span style="color: #6B7280; font-size: 0.9rem;">⭐</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 添加admin页面快速访问按钮
    if st.button("⚙️ Go to Admin Dashboard", key="admin_link", help="Access system configuration and analytics"):
        st.switch_page("pages/1_Admin.py")
    
    # Hero区域
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">AI Multi-Agent Workflow Platform</h1>
        <p class="hero-subtitle">From requirement clarification to content delivery, AI Agents make workflows more efficient</p>
        <a href="#main-content" class="hero-cta">
            Start Project →
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    # 从admin配置加载设置
    if "admin_data" not in st.session_state:
        st.session_state.admin_data = {
            "system_config": {
                "llm_provider": "mock",
                "llm_api_key": "",
                "elevenlabs_api_key": "",
                "default_voice": "21m00Tcm4TlvDq8ikWAM",
                "max_file_size": 10,
                "supported_formats": ["png", "jpg", "jpeg", "pdf"]
            }
        }
    
    # 使用admin配置
    config = st.session_state.admin_data["system_config"]
    
    # 初始化会话状态
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "project_data" not in st.session_state:
        st.session_state.project_data = {
            "files": [],
            "quotes": [],
            "tasks": []
        }
    
    # 主要内容区域 - 三个卡片
    st.markdown('<div id="main-content" class="main-content">', unsafe_allow_html=True)
    
    # 创建三列布局
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # 第一个卡片：智能对话
    with col1:
        with st.container():
            st.markdown("""
            <div class="card">
                <div class="card-header">
                    💬 Smart Conversation
                    <span style="background: #10B981; color: white; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8rem; margin-left: auto;">Connected</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 聊天容器
            chat_container = st.container()
            with chat_container:
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                
                # 显示聊天消息
                for message in st.session_state.messages:
                    if message["role"] == "user":
                        st.markdown(f"""
                        <div class="chat-message user">
                            <div class="chat-bubble user">{message["content"]}</div>
                            <div class="chat-avatar user">👤</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="chat-message">
                            <div class="chat-avatar assistant">🤖</div>
                            <div class="chat-bubble assistant">{message["content"]}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # 文件上传区域
            st.markdown("**📁 Upload Files**")
            uploaded_file = st.file_uploader(
                "Choose an image file",
                type=config["supported_formats"],
                help=f"Supports {', '.join(config['supported_formats']).upper()} formats (Max: {config['max_file_size']}MB)",
                key="file_uploader"
            )
            
            if uploaded_file is not None:
                st.success(f"📁 File uploaded: {uploaded_file.name}")
                
                if st.button("🔍 Start OCR Recognition", key="ocr_btn"):
                    # 检查文件大小
                    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
                    if file_size_mb > config["max_file_size"]:
                        st.error(f"❌ File size ({file_size_mb:.1f}MB) exceeds limit ({config['max_file_size']}MB)")
                    else:
                        with st.spinner("Recognizing text in image..."):
                            image_data = uploaded_file.read()
                            ocr_result = services['ocr'].extract_text_mock(image_data)
                            
                            if ocr_result["status"] == "completed":
                                st.session_state.project_data["files"].append({
                                    "type": "ocr",
                                    "filename": uploaded_file.name,
                                    "result": ocr_result
                                })
                                
                                st.session_state.messages.append({
                                    "role": "user",
                                    "content": f"Uploaded image file: {uploaded_file.name}"
                                })
                                st.session_state.messages.append({
                                    "role": "assistant", 
                                    "content": f"✅ OCR Recognition Completed!\n\n**Extracted Text:**\n{ocr_result['extracted_text']}\n\n**Quality Score:** {ocr_result['qc_report']['score']}/100"
                                })
                                
                                # 更新admin统计数据
                                if "admin_data" not in st.session_state:
                                    st.session_state.admin_data = {"total_projects": 0, "total_revenue": 0}
                                st.session_state.admin_data["total_projects"] = st.session_state.admin_data.get("total_projects", 0) + 1
                                st.session_state.admin_data["total_revenue"] = st.session_state.admin_data.get("total_revenue", 0) + 15.00
                                
                                st.rerun()
            
            # 聊天输入
            st.markdown("**💭 Chat Input**")
            user_input = st.text_input(
                "Enter your message:",
                placeholder="Type your request here...",
                key="chat_input"
            )
            
            if st.button("Send Message", key="send_message") and user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                with st.spinner("AI is thinking..."):
                    # 使用admin配置中的LLM设置
                    if config["llm_provider"] == "mock":
                        response = services['llm']._mock_response(user_input)
                    else:
                        # 对于其他提供商，可以扩展支持
                        response = services['llm']._mock_response(user_input)
                    
                    ai_response = response["content"]
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    st.rerun()
    
    # 第二个卡片：报价与支付
    with col2:
        with st.container():
            st.markdown("""
            <div class="card">
                <div class="card-header">
                    💰 Quote & Payment
                    <span style="background: #F59E0B; color: white; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8rem; margin-left: auto;">Pending</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 生成报价按钮
            st.markdown("**📊 Generate Quote**")
            if st.button("Generate Project Quote", key="generate_quote"):
                quote = {
                    "quote_id": str(uuid.uuid4()),
                    "tasks": [
                        {
                            "name": "Image Text Recognition",
                            "description": "Recognize text in images and convert to Markdown format",
                            "price": 52.00,
                            "estimated_time": "5-10 minutes",
                            "agent": "Agent A"
                        },
                        {
                            "name": "Text-to-Speech",
                            "description": "Convert text to high-quality audio files",
                            "price": 8.00,
                            "estimated_time": "3-5 minutes", 
                            "agent": "Agent B"
                        }
                    ],
                    "total_price": 21.00,
                    "currency": "USD",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.project_data["quotes"].append(quote)
                st.rerun()
            
            # 显示报价
            if st.session_state.project_data["quotes"]:
                latest_quote = st.session_state.project_data["quotes"][-1]
                
                st.markdown("**📋 Quote Details**")
                
                # 服务表格
                quote_data = []
                for task in latest_quote["tasks"]:
                    quote_data.append({
                        "Service": task["name"],
                        "Agent": task["agent"],
                        "Time": task["estimated_time"],
                        "Price": f"${task['price']:.2f}"
                    })
                
                st.table(quote_data)
                
                # 总计
                subtotal = sum(task['price'] for task in latest_quote['tasks'])
                platform_fee = 1.00
                total = latest_quote['total_price']
                
                st.markdown("**💳 Payment Summary**")
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.write("Subtotal:")
                    st.write("Platform Fee (5%):")
                    st.write("**Total:**")
                with col_b:
                    st.write(f"${subtotal:.2f}")
                    st.write(f"${platform_fee:.2f}")
                    st.write(f"**${total:.2f}**")
                
                # 智能合约信息
                st.info("💎 **Smart Contract Escrow**\nFunds will be held in CrossMe smart contract and released automatically upon project completion.")
                
                # 支付按钮
                if st.button(f"💳 Pay ${total:.2f}", key="payment_btn"):
                    st.session_state.project_data["payment_status"] = "completed"
                    st.success("✅ Payment successful! Project started.")
                    st.rerun()
            
            else:
                st.info("Click 'Generate Project Quote' to start")
            
            # TTS功能
            st.markdown("**🎵 Text-to-Speech Service**")
            tts_text = st.text_area(
                "Enter text to convert:",
                height=100,
                placeholder="Type or paste your text here..."
            )
            
            if st.button("🔊 Generate Speech", key="tts_btn") and tts_text:
                with st.spinner("Generating speech..."):
                    # 使用admin配置中的设置
                    if config["elevenlabs_api_key"]:
                        tts_result = services['tts'].generate_tts_with_elevenlabs(
                            tts_text, config["default_voice"], config["elevenlabs_api_key"]
                        )
                    else:
                        tts_result = services['tts'].generate_tts_mock(tts_text, config["default_voice"])
                    
                    if "error" in tts_result:
                        st.error(f"❌ {tts_result['error']}")
                    else:
                        st.success("✅ Speech generated successfully!")
                        
                        # 显示音频播放器（如果有实际音频数据）
                        if "audio_data" in tts_result:
                            st.audio(tts_result["audio_data"], format="audio/mp3")
                        
                        # 显示QC报告
                        if "qc_report" in tts_result:
                            qc = tts_result["qc_report"]
                            st.markdown(f"""
                            **QC Quality Report:**
                            - Overall Score: {qc['score']}/100
                            - Audio Quality: {qc['audio_quality']}/100
                            - Text Accuracy: {qc['text_accuracy']}/100
                            - Voice Consistency: {qc['voice_consistency']}/100
                            """)
                        
                        # 保存到项目数据
                        st.session_state.project_data["files"].append({
                            "type": "tts",
                            "text": tts_text,
                            "result": tts_result
                        })
                        
                        # 更新admin统计数据
                        if "admin_data" not in st.session_state:
                            st.session_state.admin_data = {"total_projects": 0, "total_revenue": 0}
                        st.session_state.admin_data["total_projects"] = st.session_state.admin_data.get("total_projects", 0) + 1
                        st.session_state.admin_data["total_revenue"] = st.session_state.admin_data.get("total_revenue", 0) + 8.00
    
    # 第三个卡片：项目进度
    with col3:
        with st.container():
            st.markdown("""
            <div class="card">
                <div class="card-header">
                    📈 Project Progress
                    <span style="color: #3B82F6; font-size: 0.8rem; margin-left: auto;">2/6 Complete</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 进度时间轴
            st.markdown("**🔄 Workflow Timeline**")
            
            timeline_stages = [
                {"name": "Requirements", "status": "completed", "desc": "AI conversation understanding"},
                {"name": "Quote Generation", "status": "completed" if st.session_state.project_data["quotes"] else "waiting", "desc": "Auto-generate service quote"},
                {"name": "Smart Payment", "status": "completed" if st.session_state.project_data.get("payment_status") == "completed" else "waiting", "desc": "CrossMe contract escrow"},
                {"name": "Agent A Execution", "status": "pending" if st.session_state.project_data.get("payment_status") == "completed" else "waiting", "desc": "Image text recognition"},
                {"name": "Agent B Execution", "status": "waiting", "desc": "Text-to-speech synthesis"},
                {"name": "Result Packaging", "status": "waiting", "desc": "Prepare final deliverables"}
            ]
            
            for i, stage in enumerate(timeline_stages):
                if stage["status"] == "completed":
                    icon = "✅"
                    progress = 100
                elif stage["status"] == "pending":
                    icon = "⏳"
                    progress = 50
                else:
                    icon = "○"
                    progress = 0
                
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 1rem; padding: 0.75rem; background: {'#ECFDF5' if stage['status'] == 'completed' else '#FFF7ED' if stage['status'] == 'pending' else '#F9FAFB'}; border-radius: 8px;">
                    <div style="margin-right: 1rem; font-size: 1.2rem;">{icon}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: #1F2937;">{stage['name']}</div>
                        <div style="font-size: 0.85rem; color: #6B7280;">{stage['desc']}</div>
                    </div>
                    <div style="font-size: 0.85rem; color: #3B82F6; font-weight: 500;">{progress}%</div>
                </div>
                """, unsafe_allow_html=True)
                
                if progress > 0:
                    st.progress(progress / 100)
            
            # 项目统计
            st.markdown("**📊 Project Statistics**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Files Processed", len(st.session_state.project_data['files']))
            with col_b:
                st.metric("Quotes Generated", len(st.session_state.project_data['quotes']))
            
            # 处理结果
            if st.session_state.project_data["files"]:
                st.markdown("**📁 Processing Results**")
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
    
    # 关闭主要内容区域
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 底部区域
    st.markdown("""
    <div style="background: #F9FAFB; padding: 2rem; margin-top: 2rem; text-align: center;">
        <div style="max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
            <div>
                <h3 style="color: #1F2937; margin-bottom: 1rem;">Download Center</h3>
                <p style="color: #6B7280; font-size: 0.9rem; margin-bottom: 1rem;">
                    All project deliverables will be available for download here upon completion
                </p>
                <button style="background: #3B82F6; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: not-allowed; opacity: 0.5;">
                    📥 Download Project Files
                </button>
            </div>
            <div>
                <h3 style="color: #1F2937; margin-bottom: 1rem;">Transaction History</h3>
                <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #E5E7EB;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="color: #6B7280; font-size: 0.9rem;">AI Workflow Services</span>
                        <span style="font-weight: 600;">$21.00</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #6B7280; font-size: 0.9rem;">Smart Contract Escrow</span>
                        <span style="font-weight: 600;">$21.00</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
