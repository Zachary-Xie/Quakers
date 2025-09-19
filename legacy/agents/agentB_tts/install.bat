@echo off
chcp 65001 >nul

echo 🚀 开始安装 Agent B TTS 服务...

REM 检查Python版本
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python，请先安装Python3
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set python_version=%%i
echo ✅ 找到Python: %python_version%

REM 创建虚拟环境（可选）
set /p create_venv="是否创建虚拟环境? (y/n): "
if /i "%create_venv%"=="y" (
    echo 📦 创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
)

REM 安装依赖
echo 📥 安装Python依赖...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo ✅ 依赖安装成功
) else (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

REM 创建必要的目录
echo 📁 创建目录...
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
echo ✅ 目录创建完成

REM 配置环境变量
echo ⚙️  配置环境变量...
if not exist "config.env" (
    echo 请编辑 config.env 文件，设置您的 ElevenLabs API 密钥
    echo ELEVENLABS_API_KEY=your_api_key_here > config.env
)

echo.
echo 🎉 安装完成！
echo.
echo 下一步：
echo 1. 编辑 config.env 文件，设置 ElevenLabs API 密钥
echo 2. 运行: python run.py
echo 3. 访问: http://localhost:8002/docs
echo.
echo 测试命令: python test_api.py
pause

