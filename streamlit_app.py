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

# 现代化CSS样式 - 基于参考设计的美观界面
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* 全局样式重置 */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding: 0;
        max-width: 100%;
        margin: 0;
    }
    
    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        margin: 0;
        padding: 0;
    }
    
    /* 顶部导航栏 - 现代化设计 */
    .modern-nav {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        padding: 1rem 2rem;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
        animation: slideDown 0.8s ease-out;
    }
    
    @keyframes slideDown {
        from { transform: translateY(-100%); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .nav-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 1.25rem;
        font-weight: 700;
        color: #1a1a1a;
    }
    
    .nav-logo {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .nav-menu {
        display: flex;
        gap: 2rem;
        align-items: center;
    }
    
    .nav-link {
        color: #64748b;
        text-decoration: none;
        font-weight: 500;
        font-size: 0.95rem;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .nav-link:hover {
        color: #667eea;
        background: rgba(102, 126, 234, 0.1);
        transform: translateY(-1px);
    }
    
    .nav-link.admin {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
    }
    
    .nav-link.admin:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Hero区域 - 现代化渐变 */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="1" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="1" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
        animation: fadeInUp 1.2s ease-out;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(50px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        opacity: 0.95;
        margin-bottom: 3rem;
        max-width: 700px;
        line-height: 1.6;
        font-weight: 400;
    }
    
    .hero-cta {
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
        background: rgba(255, 255, 255, 0.95);
        color: #667eea;
        padding: 1.25rem 2.5rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        transition: all 0.4s ease;
        backdrop-filter: blur(10px);
    }
    
    .hero-cta:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        background: white;
    }
    
    /* 主要内容区域 - 现代化网格布局 */
    .main-content {
        padding: 4rem 2rem;
        max-width: 1400px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
        gap: 2rem;
        animation: fadeIn 1s ease-out 0.3s both;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* 现代化卡片设计 */
    .modern-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        transition: all 0.4s ease;
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
    }
    
    .modern-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
    }
    
    .modern-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .card-header {
        padding: 2rem 2rem 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .card-title {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 1.25rem;
        font-weight: 600;
        color: #1a1a1a;
    }
    
    .card-icon {
        font-size: 1.5rem;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-connected {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    .status-pending {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
    }
    
    .card-body {
        padding: 0 2rem 2rem;
    }
    
    /* 聊天界面现代化 */
    .chat-container {
        height: 350px;
        overflow-y: auto;
        padding: 1.5rem;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: transparent;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.3);
        border-radius: 3px;
    }
    
    .chat-message {
        margin-bottom: 1.5rem;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        animation: messageSlide 0.5s ease-out;
    }
    
    @keyframes messageSlide {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .chat-message.user {
        flex-direction: row-reverse;
    }
    
    .chat-message.user .chat-bubble {
        animation: messageSlideRight 0.5s ease-out;
    }
    
    @keyframes messageSlideRight {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .chat-avatar {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        font-weight: 600;
        flex-shrink: 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .chat-avatar.user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .chat-avatar.assistant {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .chat-bubble {
        max-width: 75%;
        padding: 1rem 1.25rem;
        border-radius: 18px;
        font-size: 0.95rem;
        line-height: 1.5;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .chat-bubble.user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-bottom-right-radius: 6px;
    }
    
    .chat-bubble.assistant {
        background: white;
        color: #374151;
        border: 1px solid rgba(0, 0, 0, 0.05);
        border-bottom-left-radius: 6px;
    }
    
    /* 现代化按钮样式 */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: none;
        padding: 1rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* 输入框现代化 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid rgba(0, 0, 0, 0.05);
        padding: 1rem;
        font-size: 0.95rem;
        background: rgba(255, 255, 255, 0.8);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        background: white;
    }
    
    /* 文件上传现代化 */
    .stFileUploader > div {
        border-radius: 16px;
        border: 2px dashed rgba(102, 126, 234, 0.3);
        padding: 2.5rem;
        text-align: center;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    }
    
    .stFileUploader > div:hover {
        border-color: #667eea;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        transform: translateY(-2px);
    }
    
    /* 进度时间轴现代化 */
    .timeline-item {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding: 1rem;
        border-radius: 12px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .timeline-item.completed {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    .timeline-item.pending {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
        border: 1px solid rgba(245, 158, 11, 0.2);
    }
    
    .timeline-item.waiting {
        background: rgba(0, 0, 0, 0.02);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .timeline-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        font-weight: 600;
        margin-right: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .timeline-icon.completed {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .timeline-icon.pending {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    
    .timeline-icon.waiting {
        background: #f1f5f9;
        color: #64748b;
    }
    
    /* 统计卡片 */
    .stat-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-content {
            grid-template-columns: 1fr;
            padding: 2rem 1rem;
        }
        
        .hero-title {
            font-size: 2.5rem;
        }
        
        .hero-subtitle {
            font-size: 1.1rem;
        }
        
        .nav-menu {
            display: none;
        }
        
        .modern-nav {
            padding: 1rem;
        }
    }
    
    /* 加载动画 */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 2s infinite;
    }
    
    /* 成功/错误消息样式 */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        color: #065f46;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px;
        color: #991b1b;
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
    
    # 现代化顶部导航栏
    st.markdown("""
    <div class="modern-nav">
        <div class="nav-brand">
            <div class="nav-logo">AI</div>
            <span>AI Workflow</span>
        </div>
        <div class="nav-menu">
            <a href="#" class="nav-link">How it Works</a>
            <a href="#" class="nav-link">My Orders</a>
            <a href="/Admin" class="nav-link admin">⚙️ Admin</a>
        </div>
        <div style="display: flex; gap: 1rem; align-items: center;">
            <span style="color: #64748b; font-size: 0.9rem; font-weight: 500;">EN</span>
            <span style="color: #64748b; font-size: 1.1rem;">⭐</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 添加admin页面快速访问按钮
    if st.button("⚙️ Go to Admin Dashboard", key="admin_link", help="Access system configuration and analytics"):
        st.switch_page("pages/1_Admin.py")
    
    # 现代化Hero区域
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <h1 class="hero-title">AI Multi-Agent Workflow Platform</h1>
            <p class="hero-subtitle">From requirement clarification to content delivery, AI Agents make workflows more efficient</p>
            <a href="#main-content" class="hero-cta">
                🚀 Start Project
            </a>
        </div>
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
            <div class="modern-card">
                <div class="card-header">
                    <div class="card-title">
                        <div class="card-icon">💬</div>
                        Smart Conversation
                    </div>
                    <span class="status-badge status-connected">Connected</span>
                </div>
                <div class="card-body">
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
            
            st.markdown("""
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 第二个卡片：报价与支付
    with col2:
        with st.container():
            st.markdown("""
            <div class="modern-card">
                <div class="card-header">
                    <div class="card-title">
                        <div class="card-icon">💰</div>
                        Quote & Payment
                    </div>
                    <span class="status-badge status-pending">Pending</span>
                </div>
                <div class="card-body">
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
            
            st.markdown("""
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 第三个卡片：项目进度
    with col3:
        with st.container():
            st.markdown("""
            <div class="modern-card">
                <div class="card-header">
                    <div class="card-title">
                        <div class="card-icon">📈</div>
                        Project Progress
                    </div>
                    <span style="color: #667eea; font-size: 0.85rem; font-weight: 600;">2/6 Complete</span>
                </div>
                <div class="card-body">
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
                <div class="timeline-item {stage['status']}">
                    <div class="timeline-icon {stage['status']}">{icon}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: #1a1a1a; font-size: 0.95rem;">{stage['name']}</div>
                        <div style="font-size: 0.85rem; color: #64748b; margin-top: 0.25rem;">{stage['desc']}</div>
                    </div>
                    <div style="font-size: 0.85rem; color: #667eea; font-weight: 600;">{progress}%</div>
                </div>
                """, unsafe_allow_html=True)
                
                if progress > 0:
                    st.progress(progress / 100)
            
            # 项目统计
            st.markdown("**📊 Project Statistics**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{len(st.session_state.project_data['files'])}</div>
                    <div class="stat-label">Files Processed</div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{len(st.session_state.project_data['quotes'])}</div>
                    <div class="stat-label">Quotes Generated</div>
                </div>
                """, unsafe_allow_html=True)
            
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
            
            st.markdown("""
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 关闭主要内容区域
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 现代化底部区域
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%); padding: 4rem 2rem; margin-top: 3rem;">
        <div style="max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 3rem;">
            <div class="modern-card" style="padding: 2rem; text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📥</div>
                <h3 style="color: #1a1a1a; margin-bottom: 1rem; font-size: 1.3rem; font-weight: 600;">Download Center</h3>
                <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 2rem; line-height: 1.6;">
                    All project deliverables will be available for download here upon completion
                </p>
                <button style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 1rem 2rem; border-radius: 12px; cursor: not-allowed; opacity: 0.6; font-weight: 600; font-size: 0.95rem; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);">
                    📥 Download Project Files
                </button>
            </div>
            <div class="modern-card" style="padding: 2rem; text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">💳</div>
                <h3 style="color: #1a1a1a; margin-bottom: 1rem; font-size: 1.3rem; font-weight: 600;">Transaction History</h3>
                <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(0, 0, 0, 0.05); margin-top: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 1rem; padding-bottom: 0.75rem; border-bottom: 1px solid rgba(0, 0, 0, 0.05);">
                        <span style="color: #64748b; font-size: 0.9rem; font-weight: 500;">AI Workflow Services</span>
                        <span style="font-weight: 600; color: #1a1a1a;">$21.00</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #64748b; font-size: 0.9rem; font-weight: 500;">Smart Contract Escrow</span>
                        <span style="font-weight: 600; color: #10b981;">$21.00</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
