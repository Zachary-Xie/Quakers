智能多Agent任务流平台

1. 项目愿景

实现一个端到端的智能生产线：客户 → 需求澄清 → 任务拆分/报价 → 多 Agent 执行 → 智能合约托管收款 → 打包交付。
四大模块：

入口与会话：UI + 大模型对话 + 支付

中心处理器：拆分、报价、调度

执行代理：Agent A 图转文、Agent B 文转音

交付与账款：打包输出、智能合约结算

2. 目录结构建议
   project-root/
   │
   ├─ README.md              # 本文件
   ├─ /docs                  # 设计文档、流程图、API 规范
   │   ├─ api\_spec.yaml
   │   ├─ state\_machine.md
   │   └─ prompt\_templates.md
   │
   ├─ /orchestrator          # 中心处理器（FastAPI/NestJS） 
   │   ├─ main.py
   │   ├─ routers/
   │   └─ models/
   │
   ├─ /agents
   │   ├─ agentA\_ocr/        # 图片转文字 (留出API接口)
   │   ├─ agentB\_tts/        # 文字转语音 (留出API接口)
   │   └─ auditor/           # 自动审核官  (留出API接口)
   │
   ├─ /frontend
   │   ├─ src/
   │   └─ public/
   │
   ├─ /contracts             # CrossMint 智能合约交互代码
   │   ├─ escrow.js
   │   └─ tests/
   │
   └─ /tests                 # 端到端与集成测试
3. 核心流程图
   flowchart LR
   A\[客户入口UI] -->|对话澄清| B\[会话Agent]
   B -->|输出MRD| C\[中心处理器/Orchestrator]
   C -->|拆分任务/报价| D\[支付后端+CrossMint合约]
   D -->|资金托管确认| E\[Agent A 图转文]
   E -->|审核通过释放里程碑1| F\[Agent B 文转音]
   F -->|审核通过释放里程碑2| G\[打包交付]
   G -->|最终确认释放尾款| H\[客户下载]
4. 模块职责与接口
   4.1 入口页面（UI + 会话Agent + 支付）

收集客户需求、上传文件

与大模型对话生成 MRD（明确需求单）

展示报价、支付、状态轴

4.2 中心处理器 Orchestrator

输入：MRD

输出：任务拆分（Agent A/B）、估时、成本、排期

里程碑管理、状态机、调用智能合约 SDK

4.3 Agent A/B

Agent A：OCR + 清洗 → Markdown

Agent B：TTS → MP3 + VTT 时间轴

输出包含 qc\_report 自检报告

4.4 智能合约（CrossMint）

托管资金、分里程碑释放、仲裁退款

Webhook 回调中心处理器更新状态

5. 核心数据结构

MRD（明确需求单）：目标、输入、输出标准、验收条件、预算、截止时间

Quote（报价单）：任务、工时、费率、缓冲、里程碑比例

Task Ticket（任务工单）：每个 Agent 一张，含输入、期望输出、状态

示例 JSON 见 docs/state\_machine.md。

6. Agent 指令（Prompt 模板）

详见 docs/prompt\_templates.md，包含：

会话Agent：需求澄清问法与输出 JSON (留出API接口)

拆分/报价Agent：任务分解、估时、缓冲 (留出API接口)

Agent A：OCR + Markdown + QC 报告  (留出API接口)

Agent B：TTS + VTT + QC 报告 (留出API接口)

审核官：自动质检与返修建议

7. 运行方式（最小可行示例）

启动 Orchestrator

cd orchestrator
uvicorn main:app --reload



启动前端

cd frontend
npm install \&\& npm run dev



配置 CrossMint 测试网

在 contracts/escrow.js 中填入 CrossMint API Key/Endpoint

node contracts/test\_escrow.js 测试合约创建与释放

启动 Agent A/B

cd agents/agentA\_ocr \&\& python run.py
cd agents/agentB\_tts \&\& python run.py

8. 开发里程碑建议

M1：MRD/Quote 流程 + 前端展示

M2：CrossMint 托管资金接口打通

M3：Orchestrator 状态机 + Agent A/B 最小可行实现

M4：打包交付 + 自动审核

M5：端到端测试（docs 中给出的样例）

---

## 🚀 在线体验

### 🌐 Streamlit Cloud部署版本
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

**一键体验**: 点击上方徽章直接访问在线版本，无需本地安装！

### 🔧 本地运行
```bash
# 1. 克隆项目
git clone https://github.com/your-username/ai-workflow-platform.git
cd ai-workflow-platform

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动Streamlit应用
streamlit run streamlit_app.py
```

### 🔑 API密钥配置
在侧边栏中直接配置各种AI服务的API密钥：
- **OpenAI GPT**: 需要OpenAI API密钥
- **DeepSeek**: 需要DeepSeek API密钥  
- **ElevenLabs TTS**: 需要ElevenLabs API密钥
- **本地模拟**: 无需API密钥，可直接体验

### 📱 功能特性
- ✅ **响应式界面**: 自适应桌面和移动设备
- ✅ **智能对话**: 支持多种大模型
- ✅ **图像OCR**: 上传图片提取文字
- ✅ **文本转语音**: 高质量语音合成
- ✅ **实时报价**: 动态生成项目报价
- ✅ **进度跟踪**: 可视化任务进展

## 📁 项目结构 (Streamlit版本)

```
AI-Workflow-Platform/
├── 📄 streamlit_app.py      # 主Streamlit应用 ⭐
├── 📄 requirements.txt      # Python依赖包
├── 📄 .gitignore           # Git忽略文件
├── 📁 .streamlit/          # Streamlit配置
│   ├── config.toml         # 主题和服务器配置
│   └── secrets.toml.example # API密钥配置示例
├── 📁 .github/             # GitHub Actions
│   └── workflows/
│       └── deploy.yml      # 自动部署配置
├── 📄 PROJECT_OVERVIEW.md   # 项目全景概览
├── 📄 readme.md            # 项目说明
└── 📁 legacy/              # 原版本文件 (保留)
    ├── frontend/           # 原前端SPA
    ├── orchestrator/       # 原后端API
    ├── agents/            # 原智能体服务
    └── start_project.*    # 原启动脚本
```

### 🔄 版本对比

| 特性 | 原版本 (多服务) | Streamlit版本 |
|------|----------------|--------------|
| 部署方式 | 需要3个服务器 | 单个应用 ✅ |
| GitHub部署 | 复杂配置 | 一键部署 ✅ |
| 维护成本 | 高 | 低 ✅ |
| 用户体验 | 需本地安装 | 在线访问 ✅ |
| API集成 | 完整支持 | 简化版本 |
| 扩展性 | 高 | 中等 |

