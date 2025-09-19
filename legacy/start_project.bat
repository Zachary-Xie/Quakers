@echo off
echo ========================================
echo   AI多智能体工作流平台启动脚本
echo ========================================
echo.

echo 1. 启动后端Orchestrator服务器...
cd orchestrator
start "Orchestrator" cmd /k "python main.py"
cd ..

echo.
echo 2. 启动Agent B TTS服务器...
cd agents\agentB_tts
start "Agent B TTS" cmd /k "python main.py"
cd ..\..

echo.
echo 3. 启动前端服务器...
cd frontend
start "Frontend" cmd /k "python -m http.server 3000"
cd ..

echo.
echo ========================================
echo   所有服务已启动！
echo ========================================
echo   前端访问地址: http://localhost:3000
echo   后端API地址: http://localhost:8080
echo   Agent B地址: http://localhost:8002
echo ========================================
echo.
pause
