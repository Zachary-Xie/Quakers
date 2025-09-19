# 🚀 GitHub + Streamlit Cloud 部署指南

## 📋 部署步骤

### 1. GitHub仓库设置

1. **创建GitHub仓库**:
   ```bash
   # 在GitHub上创建新仓库: ai-workflow-platform
   ```

2. **推送代码到GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Streamlit版本"
   git branch -M main
   git remote add origin https://github.com/your-username/ai-workflow-platform.git
   git push -u origin main
   ```

### 2. Streamlit Cloud部署

1. **访问Streamlit Cloud**: https://share.streamlit.io/

2. **连接GitHub账号**并授权访问仓库

3. **创建新应用**:
   - Repository: `your-username/ai-workflow-platform`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

4. **配置环境变量**:
   在Streamlit Cloud的App settings中添加secrets:
   ```toml
   # 可选: 预设API密钥 (建议用户自行在界面中输入)
   OPENAI_API_KEY = "your_openai_api_key"
   DEEPSEEK_API_KEY = "your_deepseek_api_key"
   ELEVENLABS_API_KEY = "your_elevenlabs_api_key"
   ```

5. **部署应用**: 点击"Deploy!"按钮

### 3. 自动部署配置

GitHub Actions已配置自动测试，每次推送代码时会自动验证：
- Python环境设置
- 依赖包安装
- Streamlit应用导入测试

### 4. 域名和访问

部署成功后，您的应用将可通过以下地址访问：
- `https://your-app-name.streamlit.app`
- 或自定义域名 (Streamlit Pro功能)

## 🔧 本地开发

### 环境设置
```bash
# 克隆仓库
git clone https://github.com/your-username/ai-workflow-platform.git
cd ai-workflow-platform

# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 本地运行
```bash
# 启动Streamlit应用
streamlit run streamlit_app.py

# 应用将在 http://localhost:8501 运行
```

### 开发调试
```bash
# 启用调试模式
streamlit run streamlit_app.py --logger.level=debug

# 清除缓存
streamlit cache clear
```

## 🔑 API密钥管理

### 生产环境 (Streamlit Cloud)
- 在Streamlit Cloud的App settings中配置secrets
- 密钥会被安全加密存储

### 本地开发
- 创建 `.streamlit/secrets.toml` 文件
- 参考 `.streamlit/secrets.toml.example` 模板
- **注意**: 不要将真实API密钥提交到Git

### 用户输入 (推荐)
- 应用支持用户在侧边栏直接输入API密钥
- 密钥仅在会话期间存储，不会持久化

## 📊 监控和分析

### Streamlit Analytics
- 自动收集基础使用统计
- 可在Streamlit Cloud控制台查看

### 自定义监控
```python
# 在streamlit_app.py中添加
import streamlit as st

# 使用情况统计
if 'usage_stats' not in st.session_state:
    st.session_state.usage_stats = {
        'ocr_requests': 0,
        'tts_requests': 0,
        'chat_messages': 0
    }
```

## 🛠️ 故障排除

### 常见问题

1. **应用启动失败**:
   - 检查 `requirements.txt` 中的包版本
   - 确认 `streamlit_app.py` 语法正确

2. **API调用失败**:
   - 验证API密钥格式和权限
   - 检查网络连接和API配额

3. **文件上传问题**:
   - Streamlit默认限制文件大小为200MB
   - 可在config.toml中调整: `maxUploadSize = 1024`

### 日志查看
- Streamlit Cloud: 在App控制台查看实时日志
- 本地: 终端会显示详细日志信息

## 🚀 性能优化

### 缓存策略
```python
# 使用Streamlit缓存
@st.cache_data
def expensive_computation(data):
    return processed_data

@st.cache_resource
def load_model():
    return model
```

### 会话管理
```python
# 合理使用session_state
if 'key' not in st.session_state:
    st.session_state.key = default_value
```

## 📈 扩展功能

### 添加新功能
1. 在 `streamlit_app.py` 中添加新的服务类
2. 在主界面中添加相应的UI组件
3. 更新 `requirements.txt` (如需新依赖)
4. 测试并推送到GitHub

### 多页面应用
```python
# 可考虑升级为多页面结构
pages/
├── 1_🏠_Home.py
├── 2_🖼️_OCR.py
├── 3_🎵_TTS.py
└── 4_📊_Analytics.py
```

## 🔒 安全考虑

- API密钥通过HTTPS传输
- 不在客户端存储敏感信息
- 定期更新依赖包版本
- 启用Streamlit的CSRF保护

---

## 📞 支持

如遇到问题，请：
1. 查看Streamlit官方文档: https://docs.streamlit.io/
2. 检查GitHub Issues
3. 联系项目维护者
