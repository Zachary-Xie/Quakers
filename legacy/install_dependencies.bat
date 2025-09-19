@echo off
echo ========================================
echo   安装项目依赖包
echo ========================================
echo.

echo 安装Orchestrator依赖...
cd orchestrator
pip install -r requirements.txt
cd ..

echo.
echo 安装Agent B TTS依赖...
cd agents\agentB_tts
pip install -r requirements.txt
cd ..\..

echo.
echo ========================================
echo   依赖安装完成！
echo ========================================
echo.
echo 接下来请：
echo 1. 编辑 agents\agentB_tts\config.env 设置ElevenLabs API密钥
echo 2. 运行 start_project.bat 启动项目
echo.
pause
