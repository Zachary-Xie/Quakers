#!/bin/bash

# Agent B TTS 服务安装脚本

echo "🚀 开始安装 Agent B TTS 服务..."

# 检查Python版本
python_version=$(python3 --version 2>&1)
if [[ $? -ne 0 ]]; then
    echo "❌ 错误: 未找到Python3，请先安装Python3"
    exit 1
fi

echo "✅ 找到Python: $python_version"

# 创建虚拟环境（可选）
read -p "是否创建虚拟环境? (y/n): " create_venv
if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
fi

# 安装依赖
echo "📥 安装Python依赖..."
pip install -r requirements.txt

if [[ $? -eq 0 ]]; then
    echo "✅ 依赖安装成功"
else
    echo "❌ 依赖安装失败"
    exit 1
fi

# 创建必要的目录
echo "📁 创建目录..."
mkdir -p uploads outputs
echo "✅ 目录创建完成"

# 配置环境变量
echo "⚙️  配置环境变量..."
if [[ ! -f "config.env" ]]; then
    echo "请编辑 config.env 文件，设置您的 ElevenLabs API 密钥"
    echo "ELEVENLABS_API_KEY=your_api_key_here" > config.env
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "下一步："
echo "1. 编辑 config.env 文件，设置 ElevenLabs API 密钥"
echo "2. 运行: python run.py"
echo "3. 访问: http://localhost:8002/docs"
echo ""
echo "测试命令: python test_api.py"

