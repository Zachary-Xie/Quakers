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
    page_title="智能化多Agent协作平台",
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
        """模拟回复"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["图片", "图像", "照片", "ocr", "识别", "文字"]):
            return {
                "content": "我看到您提到了图像处理需求。我可以帮您使用OCR技术识别图像中的文字，并将其转换为Markdown格式。请上传您的图像文件。",
                "suggestions": ["上传图像文件", "查看OCR服务详情", "获取报价"]
            }
        elif any(word in message_lower for word in ["语音", "音频", "tts", "朗读", "播放"]):
            return {
                "content": "我了解您需要文本转语音服务。我可以将您的文本转换为高质量的语音文件。请输入您要转换的文本内容。",
                "suggestions": ["输入文本内容", "选择语音类型", "试听语音样本"]
            }
        else:
            return {
                "content": "您好！我是AI工作流平台的智能助手。我可以帮您处理：\n\n🖼️ **图像文字识别**：将图片中的文字转换为Markdown格式\n🔊 **文本转语音**：将文本转换为高质量语音文件\n\n请告诉我您需要什么帮助。",
                "suggestions": ["上传图像文件", "输入要转换的文本", "查看服务价格"]
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
            <span>AI工作流</span>
        </div>
        <div class="nav-menu">
            <a href="#" class="nav-link">工作流程</a>
            <a href="#" class="nav-link">我的订单</a>
        </div>
        <div class="nav-actions">
            <span style="color: #6B7280; font-size: 0.9rem;">中</span>
            <span style="color: #6B7280; font-size: 0.9rem;">简</span>
            <span style="color: #6B7280; font-size: 0.9rem;">⭐</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero区域
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">智能化多Agent协作平台</h1>
        <p class="hero-subtitle">从需求澄清到内容交付，AI Agent协作让工作流程更高效</p>
        <a href="#main-content" class="hero-cta">
            开始项目 →
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    # 隐藏的配置区域（通过session state管理）
    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = "mock"
    if "llm_api_key" not in st.session_state:
        st.session_state.llm_api_key = ""
    if "use_elevenlabs" not in st.session_state:
        st.session_state.use_elevenlabs = False
    if "elevenlabs_api_key" not in st.session_state:
        st.session_state.elevenlabs_api_key = ""
    if "voice_id" not in st.session_state:
        st.session_state.voice_id = "21m00Tcm4TlvDq8ikWAM"
    
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
    
    # 第一个卡片：智能对话
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                💬 智能对话
                <span style="background: #10B981; color: white; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8rem; margin-left: auto;">已连接</span>
            </div>
            <div class="card-body">
                <div class="chat-container" id="chat-container">
        """, unsafe_allow_html=True)
        
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
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 文件上传区域
        uploaded_file = st.file_uploader(
            "",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            help="支持PNG、JPG、JPEG、PDF格式",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            st.markdown("""
            <div style="background: #F0F9FF; padding: 1rem; border-radius: 8px; margin: 1rem 0; border: 1px solid #0EA5E9;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: #0EA5E9;">📁</span>
                    <span style="font-size: 0.9rem; color: #1F2937;">""" + uploaded_file.name + """</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔍 开始OCR识别", key="ocr_btn"):
                with st.spinner("正在识别图像中的文字..."):
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
                            "content": f"上传了图像文件: {uploaded_file.name}"
                        })
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"✅ OCR识别完成！\n\n**识别结果:**\n{ocr_result['extracted_text']}\n\n**质量评分:** {ocr_result['qc_report']['score']}/100"
                        })
                        st.rerun()
        
        # 聊天输入
        user_input = st.text_input("", placeholder="输入您的需求...", key="chat_input", label_visibility="collapsed")
        
        if st.button("发送", key="send_message") and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.spinner("AI正在思考..."):
                response = services['llm']._mock_response(user_input)
                ai_response = response["content"]
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                💰 报价与支付
                <span style="background: #F59E0B; color: white; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8rem; margin-left: auto;">待付款</span>
            </div>
            <div class="card-body">
        """, unsafe_allow_html=True)
        
        # 生成报价按钮
        if st.button("📊 生成项目报价", key="generate_quote"):
            quote = {
                "quote_id": str(uuid.uuid4()),
                "tasks": [
                    {
                        "name": "图像文字识别",
                        "description": "将图像中的文字识别并转换为Markdown格式",
                        "price": 52.00,
                        "estimated_time": "5-10分钟",
                        "agent": "Agent A"
                    },
                    {
                        "name": "文本转语音",
                        "description": "将文本转换为高质量语音文件",
                        "price": 8.00,
                        "estimated_time": "3-5分钟", 
                        "agent": "Agent B"
                    }
                ],
                "total_price": 21.00,
                "currency": "CNY",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.project_data["quotes"].append(quote)
        
        # 显示报价表格
        if st.session_state.project_data["quotes"]:
            latest_quote = st.session_state.project_data["quotes"][-1]
            
            st.markdown("""
            <table class="quote-table">
                <thead>
                    <tr>
                        <th>服务项目</th>
                        <th>执行方</th>
                        <th>预计时间</th>
                        <th>价格</th>
                    </tr>
                </thead>
                <tbody>
            """, unsafe_allow_html=True)
            
            for task in latest_quote["tasks"]:
                icon = "📄" if "图像" in task["name"] else "🎵"
                st.markdown(f"""
                <tr>
                    <td><span class="service-icon">{icon}</span>{task["name"]}</td>
                    <td>{task["agent"]}</td>
                    <td>{task["estimated_time"]}</td>
                    <td class="price">¥{task["price"]:.2f}</td>
                </tr>
                """, unsafe_allow_html=True)
            
            st.markdown("</tbody></table>", unsafe_allow_html=True)
            
            # 小计和总计
            st.markdown(f"""
            <div style="padding: 0.5rem 0; border-bottom: 1px solid #F3F4F6; display: flex; justify-content: space-between;">
                <span>小计</span>
                <span>¥{sum(task['price'] for task in latest_quote['tasks']):.2f}</span>
            </div>
            <div style="padding: 0.5rem 0; border-bottom: 1px solid #F3F4F6; display: flex; justify-content: space-between;">
                <span>平台费 (5%)</span>
                <span>¥1.00</span>
            </div>
            <div class="quote-total">
                <span>总计</span>
                <span class="total-price">¥{latest_quote['total_price']:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # 智能合约支付区域
            st.markdown("""
            <div style="background: #ECFDF5; padding: 1rem; border-radius: 8px; border: 1px solid #10B981; margin: 1rem 0;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="color: #10B981; font-weight: 600;">💎 智能合约托管</span>
                    <span style="background: #10B981; color: white; padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.7rem;">已部署</span>
                </div>
                <p style="font-size: 0.85rem; color: #065F46; margin: 0;">
                    资金将通过CrossMe智能合约托管，项目完成后自动释放给服务商
                </p>
                <p style="font-size: 0.8rem; color: #6B7280; margin: 0.5rem 0 0 0;">
                    合约地址：0x742d35Cc6aB8C0532Df4f3d...
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # 支付按钮
            if st.button("💳 立即支付 ¥21.00", key="payment_btn"):
                st.session_state.project_data["payment_status"] = "completed"
                st.success("✅ 支付成功！项目已启动")
                st.rerun()
        
        else:
            # 空状态
            st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #9CA3AF;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
                <p>点击"生成项目报价"开始</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                📈 执行进度
                <span style="color: #3B82F6; font-size: 0.8rem; margin-left: auto;">2/6 完成</span>
            </div>
            <div class="card-body">
        """, unsafe_allow_html=True)
        
        # 进度时间轴
        timeline_stages = [
            {"name": "需求澄清", "status": "completed", "progress": "100%", "desc": "AI对话理解需求"},
            {"name": "报价生成", "status": "completed" if st.session_state.project_data["quotes"] else "waiting", "progress": "100%" if st.session_state.project_data["quotes"] else "0%", "desc": "自动生成服务报价"},
            {"name": "智能支付", "status": "completed" if st.session_state.project_data.get("payment_status") == "completed" else "waiting", "progress": "100%" if st.session_state.project_data.get("payment_status") == "completed" else "0%", "desc": "CrossMe合约托管"},
            {"name": "Agent A执行", "status": "pending" if st.session_state.project_data.get("payment_status") == "completed" else "waiting", "progress": "0%", "desc": "图像文字识别处理"},
            {"name": "Agent B执行", "status": "waiting", "progress": "0%", "desc": "文本转语音合成"},
            {"name": "成果打包", "status": "waiting", "progress": "0%", "desc": "整理交付成果"}
        ]
        
        st.markdown('<div class="timeline">', unsafe_allow_html=True)
        
        for stage in timeline_stages:
            if stage["status"] == "completed":
                icon = "✅"
                css_class = "completed"
            elif stage["status"] == "pending":
                icon = "⏳"
                css_class = "pending"
            else:
                icon = stage["progress"]
                css_class = "waiting"
            
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-icon {css_class}">{icon if stage['status'] != 'waiting' else '○'}</div>
                <div class="timeline-content">
                    <div class="timeline-title">{stage['name']}</div>
                    <div class="timeline-description">{stage['desc']}</div>
                    <div class="timeline-progress">{stage['progress']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 项目统计
        st.markdown("""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">""" + str(len(st.session_state.project_data['files'])) + """</div>
                <div class="stat-label">已处理文件</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">""" + str(len(st.session_state.project_data['quotes'])) + """</div>
                <div class="stat-label">生成报价</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 处理结果
        if st.session_state.project_data["files"]:
            st.markdown('<h4 style="margin-bottom: 1rem; color: #1F2937;">📁 处理结果</h4>', unsafe_allow_html=True)
            for i, file_data in enumerate(st.session_state.project_data["files"]):
                with st.expander(f"{file_data['type'].upper()} - {file_data.get('filename', f'任务{i+1}')}"):
                    if file_data["type"] == "ocr":
                        st.markdown("**识别文本:**")
                        st.text_area("", value=file_data["result"]["extracted_text"], height=100, disabled=True, key=f"ocr_{i}")
                        st.markdown(f"**置信度:** {file_data['result']['confidence']:.2%}")
                    elif file_data["type"] == "tts":
                        st.markdown(f"**原文本:** {file_data['text']}")
                        if "qc_report" in file_data["result"]:
                            st.markdown(f"**质量评分:** {file_data['result']['qc_report']['score']}/100")
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # 关闭主要内容区域
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 底部区域
    st.markdown("""
    <div style="background: #F9FAFB; padding: 2rem; margin-top: 2rem; text-align: center;">
        <div style="max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
            <div>
                <h3 style="color: #1F2937; margin-bottom: 1rem;">下载中心</h3>
                <p style="color: #6B7280; font-size: 0.9rem; margin-bottom: 1rem;">
                    完成项目后，所有成果将在此处提供下载
                </p>
                <button style="background: #3B82F6; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: not-allowed; opacity: 0.5;">
                    📥 下载项目文件
                </button>
            </div>
            <div>
                <h3 style="color: #1F2937; margin-bottom: 1rem;">交易记录</h3>
                <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #E5E7EB;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="color: #6B7280; font-size: 0.9rem;">社交媒体</span>
                        <span style="font-weight: 600;">¥21.00</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #6B7280; font-size: 0.9rem;">智能合约托管</span>
                        <span style="font-weight: 600;">¥21.00</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
