#!/usr/bin/env python3
"""
启动Orchestrator服务器
"""

import uvicorn
import os

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8080))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"🚀 启动Orchestrator服务器...")
    print(f"📍 地址: http://{host}:{port}")
    print(f"🔧 调试模式: {debug}")
    
    uvicorn.run("main:app", host=host, port=port, reload=debug)
