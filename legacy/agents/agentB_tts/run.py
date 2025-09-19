#!/usr/bin/env python3
"""
Agent B TTS 服务启动脚本
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

def main():
    # 加载环境变量
    load_dotenv('config.env')
    
    # 检查API密钥
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key or api_key == 'your_elevenlabs_api_key_here':
        print("⚠️  警告: 未设置ElevenLabs API密钥，服务将以模拟模式运行")
        print("   请设置环境变量 ELEVENLABS_API_KEY 或修改 config.env 文件")
    else:
        print("✅ ElevenLabs API密钥已配置")
    
    # 获取配置
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8002))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 启动Agent B TTS服务...")
    print(f"   地址: http://{host}:{port}")
    print(f"   调试模式: {debug}")
    print(f"   API文档: http://{host}:{port}/docs")
    
    # 启动服务
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

if __name__ == "__main__":
    main()

