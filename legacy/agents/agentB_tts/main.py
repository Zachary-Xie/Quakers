"""
Agent B - 文字转语音 (TTS) 服务
使用 ElevenLabs API 进行高质量语音合成
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
import asyncio
import aiofiles
from datetime import datetime
import logging
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agent B - TTS Service",
    description="文字转语音服务，使用ElevenLabs API",
    version="1.0.0"
)

# 配置
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# 确保目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 初始化ElevenLabs客户端
if ELEVENLABS_API_KEY:
    elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)
else:
    elevenlabs = None
    logger.warning("ElevenLabs API key not found. Service will run in mock mode.")

# 数据模型
class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = "21m00Tcm4TlvDq8ikWAM"  # 默认语音ID
    voice_settings: Optional[dict] = None
    model_id: Optional[str] = "eleven_multilingual_v2"
    language: Optional[str] = "zh"
    output_format: Optional[str] = "mp3"

class TTSResponse(BaseModel):
    task_id: str
    status: str
    message: str
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    created_at: datetime

class QCReport(BaseModel):
    score: float  # 0-100 质量分数
    audio_quality: float  # 音频质量评分
    text_accuracy: float  # 文本准确性评分
    voice_consistency: float  # 语音一致性评分
    issues: List[str]  # 发现的问题
    recommendations: List[str]  # 改进建议
    generated_at: datetime

class TaskStatus(BaseModel):
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    text: str
    voice_id: str
    audio_url: Optional[str] = None
    vtt_url: Optional[str] = None  # VTT字幕文件URL
    duration: Optional[float] = None
    file_size: Optional[int] = None
    qc_report: Optional[QCReport] = None  # QC质检报告
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class BatchTTSRequest(BaseModel):
    texts: List[str]
    voice_id: Optional[str] = "21m00Tcm4TlvDq8ikWAM"
    voice_settings: Optional[dict] = None
    model_id: Optional[str] = "eleven_multilingual_v2"
    language: Optional[str] = "zh"
    output_format: Optional[str] = "mp3"

# 内存中的任务存储（生产环境应使用数据库）
tasks = {}

# 默认语音设置
DEFAULT_VOICE_SETTINGS = {
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0.0,
    "use_speaker_boost": True
}

@app.get("/")
async def root():
    """服务健康检查"""
    return {
        "service": "Agent B - TTS Service",
        "status": "running",
        "version": "1.0.0",
        "elevenlabs_connected": elevenlabs is not None
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        if elevenlabs:
            # 测试ElevenLabs连接
            models = elevenlabs.models.get_all()
            return {
                "status": "healthy",
                "elevenlabs_connected": True,
                "available_models": len(models)
            }
        else:
            return {
                "status": "healthy",
                "elevenlabs_connected": False,
                "mode": "mock"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/voices")
async def get_voices():
    """获取可用语音列表"""
    try:
        if elevenlabs:
            voices = elevenlabs.voices.get_all()
            return {
                "voices": [
                    {
                        "voice_id": voice.voice_id,
                        "name": voice.name,
                        "category": voice.category,
                        "description": voice.description,
                        "labels": voice.labels
                    }
                    for voice in voices
                ]
            }
        else:
            # 返回模拟语音列表
            return {
                "voices": [
                    {
                        "voice_id": "21m00Tcm4TlvDq8ikWAM",
                        "name": "Rachel",
                        "category": "premade",
                        "description": "默认女性语音",
                        "labels": {"gender": "female", "age": "young"}
                    },
                    {
                        "voice_id": "AZnzlk1XvdvUeBnXmlld",
                        "name": "Domi",
                        "category": "premade", 
                        "description": "默认男性语音",
                        "labels": {"gender": "male", "age": "young"}
                    }
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取语音列表失败: {str(e)}")

@app.post("/tts", response_model=TTSResponse)
async def create_tts_task(request: TTSRequest, background_tasks: BackgroundTasks):
    """创建TTS任务"""
    try:
        # 验证输入
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="文本内容不能为空")
        
        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="文本长度不能超过5000字符")
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务记录
        task = TaskStatus(
            task_id=task_id,
            status="pending",
            progress=0,
            text=request.text,
            voice_id=request.voice_id,
            created_at=datetime.now()
        )
        tasks[task_id] = task
        
        # 添加后台任务
        background_tasks.add_task(process_tts_task, task_id, request)
        
        return TTSResponse(
            task_id=task_id,
            status="pending",
            message="TTS任务已创建，正在处理中...",
            created_at=task.created_at
        )
        
    except Exception as e:
        logger.error(f"创建TTS任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")

@app.get("/task/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return tasks[task_id]

@app.get("/task/{task_id}/download")
async def download_audio(task_id: str):
    """下载生成的音频文件"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks[task_id]
    
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")
    
    if not task.audio_url:
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    file_path = os.path.join(OUTPUT_DIR, f"{task_id}.mp3")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=f"tts_{task_id}.mp3",
        media_type="audio/mpeg"
    )

@app.get("/task/{task_id}/vtt")
async def download_vtt(task_id: str):
    """下载生成的VTT字幕文件"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks[task_id]
    
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")
    
    if not task.vtt_url:
        raise HTTPException(status_code=404, detail="VTT文件不存在")
    
    file_path = os.path.join(OUTPUT_DIR, f"{task_id}.vtt")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="VTT文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=f"subtitle_{task_id}.vtt",
        media_type="text/vtt"
    )

@app.get("/task/{task_id}/qc-report")
async def get_qc_report(task_id: str):
    """获取QC质检报告"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks[task_id]
    
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")
    
    if not task.qc_report:
        raise HTTPException(status_code=404, detail="QC报告不存在")
    
    return task.qc_report

@app.post("/batch-tts")
async def create_batch_tts(request: BatchTTSRequest, background_tasks: BackgroundTasks):
    """创建批量TTS任务"""
    try:
        if len(request.texts) > 10:
            raise HTTPException(status_code=400, detail="批量任务不能超过10个文本")
        
        task_ids = []
        for text in request.texts:
            tts_request = TTSRequest(
                text=text,
                voice_id=request.voice_id,
                voice_settings=request.voice_settings,
                model_id=request.model_id,
                language=request.language,
                output_format=request.output_format
            )
            
            task_id = str(uuid.uuid4())
            task = TaskStatus(
                task_id=task_id,
                status="pending",
                progress=0,
                text=text,
                voice_id=request.voice_id,
                created_at=datetime.now()
            )
            tasks[task_id] = task
            task_ids.append(task_id)
            
            # 添加后台任务
            background_tasks.add_task(process_tts_task, task_id, tts_request)
        
        return {
            "batch_id": str(uuid.uuid4()),
            "task_ids": task_ids,
            "total_tasks": len(task_ids),
            "status": "created"
        }
        
    except Exception as e:
        logger.error(f"创建批量TTS任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建批量任务失败: {str(e)}")

@app.get("/tasks")
async def list_tasks(limit: int = 50, offset: int = 0):
    """获取任务列表"""
    task_list = list(tasks.values())
    task_list.sort(key=lambda x: x.created_at, reverse=True)
    
    return {
        "tasks": task_list[offset:offset + limit],
        "total": len(task_list),
        "limit": limit,
        "offset": offset
    }

async def process_tts_task(task_id: str, request: TTSRequest):
    """处理TTS任务的后台函数"""
    try:
        task = tasks[task_id]
        task.status = "processing"
        task.progress = 10
        
        logger.info(f"开始处理TTS任务: {task_id}")
        
        if elevenlabs:
            # 使用ElevenLabs API
            await process_with_elevenlabs(task, request)
        else:
            # 模拟处理
            await process_mock_tts(task, request)
        
        task.status = "completed"
        task.progress = 100
        task.completed_at = datetime.now()
        
        logger.info(f"TTS任务完成: {task_id}")
        
    except Exception as e:
        logger.error(f"处理TTS任务失败 {task_id}: {str(e)}")
        task = tasks[task_id]
        task.status = "failed"
        task.error_message = str(e)
        task.completed_at = datetime.now()

async def process_with_elevenlabs(task: TaskStatus, request: TTSRequest):
    """使用ElevenLabs API处理TTS"""
    try:
        # 设置语音参数
        voice_settings = VoiceSettings(**DEFAULT_VOICE_SETTINGS)
        if request.voice_settings:
            voice_settings = VoiceSettings(**request.voice_settings)
        
        # 生成音频
        task.progress = 30
        
        audio = elevenlabs.generate(
            text=request.text,
            voice=Voice(
                voice_id=request.voice_id,
                settings=voice_settings
            ),
            model_id=request.model_id
        )
        
        task.progress = 50
        
        # 保存音频文件
        output_path = os.path.join(OUTPUT_DIR, f"{task.task_id}.mp3")
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        
        # 获取文件信息
        file_size = os.path.getsize(output_path)
        estimated_duration = len(request.text) * 0.1  # 估算时长
        
        task.progress = 70
        
        # 生成VTT字幕文件
        await generate_vtt_file(task.task_id, request.text, estimated_duration)
        
        task.progress = 85
        
        # 生成QC报告
        qc_report = await generate_qc_report(task.task_id, request.text, output_path, estimated_duration)
        
        # 更新任务信息
        task.audio_url = f"/task/{task.task_id}/download"
        task.vtt_url = f"/task/{task.task_id}/vtt"
        task.file_size = file_size
        task.duration = estimated_duration
        task.qc_report = qc_report
        
        task.progress = 100
        
    except Exception as e:
        raise Exception(f"ElevenLabs处理失败: {str(e)}")

async def process_mock_tts(task: TaskStatus, request: TTSRequest):
    """模拟TTS处理"""
    try:
        # 模拟处理时间
        await asyncio.sleep(2)
        task.progress = 50
        
        # 创建模拟音频文件（实际项目中应该生成真实音频）
        output_path = os.path.join(OUTPUT_DIR, f"{task.task_id}.mp3")
        
        # 创建一个简单的文本文件作为模拟
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"模拟TTS音频文件\n任务ID: {task.task_id}\n文本: {request.text}\n语音ID: {request.voice_id}")
        
        estimated_duration = len(request.text) * 0.1
        
        task.progress = 70
        
        # 生成VTT字幕文件
        await generate_vtt_file(task.task_id, request.text, estimated_duration)
        
        task.progress = 85
        
        # 生成QC报告
        qc_report = await generate_qc_report(task.task_id, request.text, output_path, estimated_duration)
        
        # 更新任务信息
        task.audio_url = f"/task/{task.task_id}/download"
        task.vtt_url = f"/task/{task.task_id}/vtt"
        task.file_size = os.path.getsize(output_path)
        task.duration = estimated_duration
        task.qc_report = qc_report
        
        task.progress = 100
        
    except Exception as e:
        raise Exception(f"模拟TTS处理失败: {str(e)}")

async def generate_vtt_file(task_id: str, text: str, duration: float):
    """生成VTT字幕文件"""
    try:
        vtt_path = os.path.join(OUTPUT_DIR, f"{task_id}.vtt")
        
        # 简单的VTT字幕生成（实际应该根据音频进行精确时间轴分割）
        words = text.split()
        words_per_second = len(words) / duration if duration > 0 else 1
        
        vtt_content = "WEBVTT\n\n"
        
        current_time = 0.0
        words_per_chunk = max(1, int(words_per_second * 3))  # 每3秒一个字幕块
        
        for i in range(0, len(words), words_per_chunk):
            chunk_words = words[i:i + words_per_chunk]
            chunk_text = " ".join(chunk_words)
            
            start_time = current_time
            end_time = min(current_time + 3.0, duration)
            
            # 格式化时间
            start_formatted = format_vtt_time(start_time)
            end_formatted = format_vtt_time(end_time)
            
            vtt_content += f"{start_formatted} --> {end_formatted}\n"
            vtt_content += f"{chunk_text}\n\n"
            
            current_time = end_time
        
        # 保存VTT文件
        async with aiofiles.open(vtt_path, 'w', encoding='utf-8') as f:
            await f.write(vtt_content)
            
        logger.info(f"VTT字幕文件生成成功: {task_id}")
        
    except Exception as e:
        logger.error(f"VTT文件生成失败 {task_id}: {str(e)}")
        raise

def format_vtt_time(seconds: float) -> str:
    """格式化VTT时间格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

async def generate_qc_report(task_id: str, text: str, audio_path: str, duration: float) -> QCReport:
    """生成QC质检报告"""
    try:
        issues = []
        recommendations = []
        
        # 文本质量检查
        text_accuracy = 95.0
        if len(text) < 10:
            issues.append("文本长度过短，可能影响语音质量")
            text_accuracy -= 10
            recommendations.append("建议增加文本长度以获得更好的语音效果")
        
        if any(char in text for char in ['<', '>', '{', '}', '[', ']']):
            issues.append("文本包含特殊字符，可能影响语音合成")
            text_accuracy -= 5
            recommendations.append("建议清理文本中的特殊字符")
        
        # 音频质量检查（基于文件大小估算）
        audio_quality = 90.0
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            if file_size < 1024:  # 小于1KB可能有问题
                issues.append("音频文件大小异常，可能生成失败")
                audio_quality -= 20
                recommendations.append("检查音频生成过程是否正常")
        else:
            audio_quality = 0.0
            issues.append("音频文件不存在")
            recommendations.append("重新生成音频文件")
        
        # 语音一致性检查
        voice_consistency = 88.0
        if duration > 0:
            words_per_minute = len(text.split()) / (duration / 60)
            if words_per_minute > 200:
                issues.append("语速过快，可能影响理解")
                voice_consistency -= 10
                recommendations.append("考虑调整语音设置以降低语速")
            elif words_per_minute < 80:
                issues.append("语速过慢，可能影响听感")
                voice_consistency -= 5
                recommendations.append("考虑调整语音设置以提高语速")
        
        # 计算总分
        total_score = (text_accuracy + audio_quality + voice_consistency) / 3
        
        # 根据分数添加建议
        if total_score >= 90:
            recommendations.append("语音质量优秀，无需调整")
        elif total_score >= 80:
            recommendations.append("语音质量良好，可考虑微调")
        elif total_score >= 70:
            recommendations.append("语音质量一般，建议优化文本或语音设置")
        else:
            recommendations.append("语音质量较差，建议重新生成")
        
        return QCReport(
            score=total_score,
            audio_quality=audio_quality,
            text_accuracy=text_accuracy,
            voice_consistency=voice_consistency,
            issues=issues,
            recommendations=recommendations,
            generated_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"QC报告生成失败 {task_id}: {str(e)}")
        # 返回默认报告
        return QCReport(
            score=0.0,
            audio_quality=0.0,
            text_accuracy=0.0,
            voice_consistency=0.0,
            issues=[f"QC报告生成失败: {str(e)}"],
            recommendations=["请重新生成任务"],
            generated_at=datetime.now()
        )

@app.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """删除任务和相关文件"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks[task_id]
    
    # 删除音频文件
    if task.audio_url:
        audio_path = os.path.join(OUTPUT_DIR, f"{task_id}.mp3")
        if os.path.exists(audio_path):
            os.remove(audio_path)
    
    # 删除VTT字幕文件
    if task.vtt_url:
        vtt_path = os.path.join(OUTPUT_DIR, f"{task_id}.vtt")
        if os.path.exists(vtt_path):
            os.remove(vtt_path)
    
    # 删除任务记录
    del tasks[task_id]
    
    return {"message": "任务已删除，包括音频文件和VTT字幕文件"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

