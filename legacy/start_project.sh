#!/bin/bash

echo "========================================"
echo "   AI多智能体工作流平台启动脚本"
echo "========================================"
echo ""

echo "1. 启动后端Orchestrator服务器..."
cd orchestrator
gnome-terminal --title="Orchestrator" -- bash -c "python main.py; exec bash" 2>/dev/null || \
xterm -title "Orchestrator" -e "python main.py" 2>/dev/null || \
python main.py &
cd ..

echo ""
echo "2. 启动Agent B TTS服务器..."
cd agents/agentB_tts
gnome-terminal --title="Agent B TTS" -- bash -c "python main.py; exec bash" 2>/dev/null || \
xterm -title "Agent B TTS" -e "python main.py" 2>/dev/null || \
python main.py &
cd ../..

echo ""
echo "3. 启动前端服务器..."
cd frontend
gnome-terminal --title="Frontend" -- bash -c "python -m http.server 3000; exec bash" 2>/dev/null || \
xterm -title "Frontend" -e "python -m http.server 3000" 2>/dev/null || \
python -m http.server 3000 &
cd ..

echo ""
echo "========================================"
echo "   所有服务已启动！"
echo "========================================"
echo "   前端访问地址: http://localhost:3000"
echo "   后端API地址: http://localhost:8080"
echo "   Agent B地址: http://localhost:8002"
echo "========================================"
echo ""
echo "按任意键退出..."
read -n 1
