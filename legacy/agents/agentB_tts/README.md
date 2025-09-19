# Agent B - 文字转语音 (TTS) 服务

基于ElevenLabs API的高质量文字转语音服务，支持多种语言和语音模型。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

复制配置文件并设置您的ElevenLabs API密钥：

```bash
cp config.env.example config.env
# 编辑 config.env 文件，设置 ELEVENLABS_API_KEY
```

### 3. 启动服务

```bash
python run.py
```

服务将在 `http://localhost:8002` 启动

### 4. 查看API文档

访问 `http://localhost:8002/docs` 查看交互式API文档

## 📋 API接口

### 基础信息

- **服务地址**: `http://localhost:8002`
- **认证方式**: ElevenLabs API Key (xi-api-key header)
- **数据格式**: JSON

### 主要端点

#### 1. 健康检查
```http
GET /health
```

#### 2. 获取可用语音
```http
GET /voices
```

#### 3. 创建TTS任务
```http
POST /tts
Content-Type: application/json

{
  "text": "要转换的文字",
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.75
  },
  "model_id": "eleven_multilingual_v2",
  "language": "zh",
  "output_format": "mp3"
}
```

#### 4. 查询任务状态
```http
GET /task/{task_id}
```

#### 5. 下载音频文件
```http
GET /task/{task_id}/download
```

#### 6. 下载VTT字幕文件
```http
GET /task/{task_id}/vtt
```

#### 7. 获取QC质检报告
```http
GET /task/{task_id}/qc-report
```

#### 8. 批量TTS
```http
POST /batch-tts
Content-Type: application/json

{
  "texts": ["文本1", "文本2", "文本3"],
  "voice_id": "21m00Tcm4TlvDq8ikWAM"
}
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ELEVENLABS_API_KEY` | ElevenLabs API密钥 | 必填 |
| `HOST` | 服务主机 | 0.0.0.0 |
| `PORT` | 服务端口 | 8002 |
| `DEBUG` | 调试模式 | True |
| `UPLOAD_DIR` | 上传目录 | uploads |
| `OUTPUT_DIR` | 输出目录 | outputs |
| `MAX_FILE_SIZE` | 最大文件大小 | 10485760 (10MB) |

### 语音设置

```json
{
  "stability": 0.5,        // 稳定性 (0.0-1.0)
  "similarity_boost": 0.75, // 相似度增强 (0.0-1.0)
  "style": 0.0,            // 风格 (0.0-1.0)
  "use_speaker_boost": true // 使用说话人增强
}
```

## 🧪 测试

运行测试脚本：

```bash
python test_api.py
```

测试包括：
- 健康检查
- 语音列表获取
- 单次TTS任务
- VTT字幕文件生成和下载
- QC质检报告生成和获取
- 批量TTS任务
- 任务状态查询

## 📊 使用示例

### Python示例

```python
import requests

# 创建TTS任务
response = requests.post('http://localhost:8002/tts', json={
    'text': '你好，世界！',
    'voice_id': '21m00Tcm4TlvDq8ikWAM',
    'language': 'zh'
})

task_id = response.json()['task_id']

# 查询任务状态
status = requests.get(f'http://localhost:8002/task/{task_id}').json()
print(f"状态: {status['status']}")

# 下载音频文件
if status['status'] == 'completed':
    audio_response = requests.get(f'http://localhost:8002/task/{task_id}/download')
    with open('output.mp3', 'wb') as f:
        f.write(audio_response.content)
```

### cURL示例

```bash
# 创建TTS任务
curl -X POST "http://localhost:8002/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!",
    "voice_id": "21m00Tcm4TlvDq8ikWAM"
  }'

# 查询任务状态
curl "http://localhost:8002/task/{task_id}"

# 下载音频
curl "http://localhost:8002/task/{task_id}/download" -o output.mp3
```

## 🔍 故障排除

### 常见问题

1. **API密钥错误**
   - 检查 `ELEVENLABS_API_KEY` 是否正确设置
   - 确认API密钥有效且有足够额度

2. **服务无法启动**
   - 检查端口8002是否被占用
   - 确认所有依赖已正确安装

3. **TTS任务失败**
   - 检查文本长度是否超过5000字符
   - 确认语音ID是否有效
   - 查看任务错误信息

### 日志查看

服务运行时会在控制台输出详细日志，包括：
- 任务创建和处理状态
- API调用结果
- 错误信息

## 📈 性能优化

1. **并发处理**: 服务支持多个TTS任务并发处理
2. **文件缓存**: 生成的音频文件会缓存，避免重复生成
3. **异步处理**: 使用FastAPI的异步特性提高性能
4. **资源管理**: 自动清理过期任务和文件

## 🔒 安全说明

- API密钥存储在环境变量中，不会暴露在代码中
- 支持任务访问控制（可扩展）
- 文件上传和下载有大小限制
- 建议在生产环境中使用HTTPS

## 📝 更新日志

### v1.0.0
- 初始版本发布
- 支持ElevenLabs API集成
- 提供完整的REST API接口
- 支持批量TTS处理
- 包含测试和文档

