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
    page_title="AI多智能体工作流平台",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #E3F2FD;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #F5F5F5;
        margin-right: 2rem;
    }
    .status-card {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
    }
    .metric-card {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# LLM服务类
class LLMService:
    def __init__(self):
        self.providers = {
            'mock': {'name': '本地模拟', 'needsKey': False},
            'openai': {'name': 'OpenAI GPT', 'needsKey': True, 'url': 'https://api.openai.com/v1/chat/completions'},
            'deepseek': {'name': 'DeepSeek', 'needsKey': True, 'url': 'https://api.aimlapi.com/v1/chat/completions'},
            'qianwen': {'name': '通义千问', 'needsKey': True, 'url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'},
        }
    
    async def generate_response(self, message: str, provider: str, api_key: str = None, history: List = None) -> Dict:
        """生成AI回复"""
        if provider == 'mock':
            return self._mock_response(message)
        
        if not api_key and self.providers[provider]['needsKey']:
            return {"error": "需要API密钥"}
        
        try:
            if provider == 'openai':
                return await self._call_openai(message, api_key, history or [])
            elif provider == 'deepseek':
                return await self._call_deepseek(message, api_key, history or [])
            elif provider == 'qianwen':
                return await self._call_qianwen(message, api_key, history or [])
        except Exception as e:
            return {"error": f"API调用失败: {str(e)}"}
    
    def _mock_response(self, message: str) -> Dict:
        """模拟回复"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["图片", "图像", "照片", "ocr"]):
            return {
                "content": "我看到您提到了图像处理需求。我可以帮您使用OCR技术识别图像中的文字，并将其转换为Markdown格式。请上传您的图像文件。",
                "suggestions": ["上传图像文件", "查看OCR服务详情", "获取报价"]
            }
        elif any(word in message_lower for word in ["语音", "音频", "tts"]):
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
        """调用OpenAI API"""
        messages = [{"role": "system", "content": "你是一个AI工作流平台的助手，专门处理OCR和TTS任务。"}]
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
            return {"error": f"OpenAI API错误: {response.status_code}"}
    
    async def _call_deepseek(self, message: str, api_key: str, history: List) -> Dict:
        """调用DeepSeek API"""
        messages = [{"role": "system", "content": "你是一个AI工作流平台的助手，专门处理OCR和TTS任务。"}]
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
            return {"error": f"DeepSeek API错误: {response.status_code}"}

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
    
    # 页面标题
    st.markdown("<h1 class='main-header'>🤖 AI多智能体工作流平台</h1>", unsafe_allow_html=True)
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 配置设置")
        
        # LLM配置
        st.subheader("🧠 AI模型设置")
        llm_provider = st.selectbox(
            "选择AI服务提供商",
            options=list(services['llm'].providers.keys()),
            format_func=lambda x: services['llm'].providers[x]['name']
        )
        
        llm_api_key = ""
        if services['llm'].providers[llm_provider]['needsKey']:
            llm_api_key = st.text_input(
                "API密钥", 
                type="password",
                help=f"请输入{services['llm'].providers[llm_provider]['name']}的API密钥"
            )
        
        # TTS配置
        st.subheader("🎵 语音合成设置")
        use_elevenlabs = st.checkbox("使用ElevenLabs TTS", help="需要ElevenLabs API密钥")
        
        elevenlabs_api_key = ""
        if use_elevenlabs:
            elevenlabs_api_key = st.text_input(
                "ElevenLabs API密钥",
                type="password"
            )
        
        voice_id = st.selectbox(
            "选择语音",
            options=list(services['tts'].voices.keys()),
            format_func=lambda x: services['tts'].voices[x]
        )
        
        # 清除聊天历史
        if st.button("🗑️ 清除聊天历史"):
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
        st.header("💬 智能对话")
        
        # 显示聊天历史
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 您:</strong><br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>🤖 助手:</strong><br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # 文件上传
        uploaded_file = st.file_uploader(
            "📁 上传图像文件 (OCR)",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            help="支持PNG、JPG、JPEG、PDF格式"
        )
        
        if uploaded_file is not None:
            # 显示上传的图像
            if uploaded_file.type.startswith('image'):
                st.image(uploaded_file, caption="上传的图像", use_column_width=True)
            
            if st.button("🔍 开始OCR识别"):
                with st.spinner("正在识别图像中的文字..."):
                    # 处理OCR
                    image_data = uploaded_file.read()
                    ocr_result = services['ocr'].extract_text_mock(image_data)
                    
                    if ocr_result["status"] == "completed":
                        st.session_state.project_data["files"].append({
                            "type": "ocr",
                            "filename": uploaded_file.name,
                            "result": ocr_result
                        })
                        
                        # 添加到聊天历史
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
        user_input = st.text_input("💭 输入您的问题或需求:", key="chat_input")
        
        if st.button("发送", key="send_message") and user_input:
            # 添加用户消息
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # 生成AI回复
            with st.spinner("AI正在思考..."):
                history = [{"role": msg["role"], "content": msg["content"]} 
                          for msg in st.session_state.messages[-5:]]  # 只保留最近5条消息作为上下文
                
                import asyncio
                try:
                    # 由于Streamlit不支持异步，使用同步方式
                    if llm_provider == 'mock':
                        response = services['llm']._mock_response(user_input)
                    else:
                        # 这里需要同步调用API
                        response = {"content": "抱歉，在Streamlit环境中暂时无法调用外部API。请使用本地模拟模式。"}
                except Exception as e:
                    response = {"error": str(e)}
                
                if "error" in response:
                    ai_response = f"❌ {response['error']}"
                else:
                    ai_response = response["content"]
                
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
    
    with col2:
        st.header("💰 报价与支付")
        
        # 生成报价
        if st.button("📊 生成项目报价"):
            quote = {
                "quote_id": str(uuid.uuid4()),
                "tasks": [
                    {
                        "name": "图像OCR识别",
                        "description": "将图像中的文字识别并转换为Markdown格式",
                        "price": 50.0,
                        "estimated_time": "5-10分钟"
                    },
                    {
                        "name": "文本转语音",
                        "description": "将文本转换为高质量语音文件",
                        "price": 30.0,
                        "estimated_time": "3-8分钟"
                    }
                ],
                "total_price": 80.0,
                "currency": "CNY",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            st.session_state.project_data["quotes"].append(quote)
            st.success("✅ 报价生成成功！")
        
        # 显示报价
        if st.session_state.project_data["quotes"]:
            latest_quote = st.session_state.project_data["quotes"][-1]
            
            st.markdown(f"""
            <div class="status-card">
                <h4>📋 最新报价</h4>
                <p><strong>报价ID:</strong> {latest_quote['quote_id'][:8]}...</p>
                <p><strong>总价:</strong> ¥{latest_quote['total_price']}</p>
                <p><strong>创建时间:</strong> {latest_quote['created_at']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📝 任务明细")
            for task in latest_quote["tasks"]:
                with st.expander(f"{task['name']} - ¥{task['price']}"):
                    st.write(f"**描述:** {task['description']}")
                    st.write(f"**预估时间:** {task['estimated_time']}")
            
            # 模拟支付
            if st.button("💳 确认支付"):
                st.session_state.project_data["payment_status"] = "completed"
                st.success("✅ 支付成功！项目已启动。")
        
        # TTS功能
        st.subheader("🎵 文本转语音")
        tts_text = st.text_area("输入要转换的文本:", height=100)
        
        if st.button("🔊 生成语音") and tts_text:
            with st.spinner("正在生成语音..."):
                if use_elevenlabs and elevenlabs_api_key:
                    tts_result = services['tts'].generate_tts_with_elevenlabs(
                        tts_text, voice_id, elevenlabs_api_key
                    )
                else:
                    tts_result = services['tts'].generate_tts_mock(tts_text, voice_id)
                
                if "error" in tts_result:
                    st.error(f"❌ {tts_result['error']}")
                else:
                    st.success("✅ 语音生成成功！")
                    
                    # 显示TTS结果
                    if "audio_data" in tts_result:
                        st.audio(tts_result["audio_data"], format="audio/mp3")
                    
                    # 显示QC报告
                    if "qc_report" in tts_result:
                        qc = tts_result["qc_report"]
                        st.markdown(f"""
                        **QC质量报告:**
                        - 总分: {qc['score']}/100
                        - 音频质量: {qc['audio_quality']}/100
                        - 文本准确性: {qc['text_accuracy']}/100
                        - 语音一致性: {qc['voice_consistency']}/100
                        """)
                    
                    # 保存到项目数据
                    st.session_state.project_data["files"].append({
                        "type": "tts",
                        "text": tts_text,
                        "result": tts_result
                    })
    
    with col3:
        st.header("📈 项目进度")
        
        # 进度时间轴
        timeline_stages = [
            {"name": "需求澄清", "status": "completed", "progress": 100},
            {"name": "报价生成", "status": "completed" if st.session_state.project_data["quotes"] else "pending", "progress": 100 if st.session_state.project_data["quotes"] else 0},
            {"name": "支付确认", "status": "completed" if st.session_state.project_data.get("payment_status") == "completed" else "pending", "progress": 100 if st.session_state.project_data.get("payment_status") == "completed" else 0},
            {"name": "任务处理", "status": "completed" if st.session_state.project_data["files"] else "pending", "progress": 100 if st.session_state.project_data["files"] else 0},
            {"name": "质量检查", "status": "completed" if st.session_state.project_data["files"] else "pending", "progress": 100 if st.session_state.project_data["files"] else 0},
            {"name": "交付完成", "status": "completed" if len(st.session_state.project_data["files"]) >= 2 else "pending", "progress": 100 if len(st.session_state.project_data["files"]) >= 2 else 0}
        ]
        
        for i, stage in enumerate(timeline_stages):
            if stage["status"] == "completed":
                icon = "✅"
                color = "#4CAF50"
            elif stage["status"] == "pending":
                icon = "⏳"
                color = "#FF9800"
            else:
                icon = "⭕"
                color = "#9E9E9E"
            
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
                <span style="color: {color}; font-weight: bold;">{stage['name']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if stage["progress"] > 0:
                st.progress(stage["progress"] / 100)
        
        # 项目统计
        st.subheader("📊 项目统计")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{len(st.session_state.project_data['files'])}</h3>
                <p>已处理文件</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{len(st.session_state.project_data['quotes'])}</h3>
                <p>生成报价</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 文件列表
        if st.session_state.project_data["files"]:
            st.subheader("📁 处理结果")
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

if __name__ == "__main__":
    main()
