#!/usr/bin/env python3
"""
Agent B TTS API 测试脚本
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('config.env')

# API配置
BASE_URL = "http://localhost:8002"
API_KEY = os.getenv('ELEVENLABS_API_KEY', '')

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_voices():
    """测试获取语音列表"""
    print("\n🎤 测试获取语音列表...")
    try:
        response = requests.get(f"{BASE_URL}/voices")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"可用语音数量: {len(data['voices'])}")
        for voice in data['voices'][:3]:  # 只显示前3个
            print(f"  - {voice['name']} ({voice['voice_id']})")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 获取语音列表失败: {e}")
        return False

def test_tts():
    """测试TTS功能"""
    print("\n🎵 测试TTS功能...")
    try:
        # 创建TTS任务
        tts_data = {
            "text": "你好，这是一个测试文本。Hello, this is a test text.",
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "language": "zh",
            "output_format": "mp3"
        }
        
        response = requests.post(f"{BASE_URL}/tts", json=tts_data)
        print(f"创建任务状态码: {response.status_code}")
        
        if response.status_code == 200:
            task_info = response.json()
            task_id = task_info['task_id']
            print(f"任务ID: {task_id}")
            
            # 轮询任务状态
            max_attempts = 30
            for attempt in range(max_attempts):
                status_response = requests.get(f"{BASE_URL}/task/{task_id}")
                if status_response.status_code == 200:
                    task_status = status_response.json()
                    print(f"任务状态: {task_status['status']} ({task_status['progress']}%)")
                    
                    if task_status['status'] == 'completed':
                        print(f"✅ TTS任务完成!")
                        print(f"音频URL: {task_status['audio_url']}")
                        print(f"VTT字幕URL: {task_status['vtt_url']}")
                        print(f"文件大小: {task_status['file_size']} bytes")
                        print(f"时长: {task_status['duration']} 秒")
                        
                        # 显示QC报告
                        if task_status.get('qc_report'):
                            qc = task_status['qc_report']
                            print(f"QC报告 - 总分: {qc['score']:.1f}")
                            print(f"  音频质量: {qc['audio_quality']:.1f}")
                            print(f"  文本准确性: {qc['text_accuracy']:.1f}")
                            print(f"  语音一致性: {qc['voice_consistency']:.1f}")
                            if qc['issues']:
                                print(f"  问题: {', '.join(qc['issues'])}")
                            if qc['recommendations']:
                                print(f"  建议: {', '.join(qc['recommendations'])}")
                        
                        return True
                    elif task_status['status'] == 'failed':
                        print(f"❌ TTS任务失败: {task_status.get('error_message', '未知错误')}")
                        return False
                    
                    time.sleep(1)
                else:
                    print(f"❌ 获取任务状态失败: {status_response.status_code}")
                    return False
            
            print("⏰ 任务超时")
            return False
        else:
            print(f"❌ 创建TTS任务失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TTS测试失败: {e}")
        return False

def test_batch_tts():
    """测试批量TTS功能"""
    print("\n📦 测试批量TTS功能...")
    try:
        batch_data = {
            "texts": [
                "这是第一个测试文本",
                "这是第二个测试文本", 
                "这是第三个测试文本"
            ],
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "language": "zh"
        }
        
        response = requests.post(f"{BASE_URL}/batch-tts", json=batch_data)
        print(f"批量任务状态码: {response.status_code}")
        
        if response.status_code == 200:
            batch_info = response.json()
            print(f"批量任务ID: {batch_info['batch_id']}")
            print(f"任务数量: {batch_info['total_tasks']}")
            print(f"任务ID列表: {batch_info['task_ids']}")
            return True
        else:
            print(f"❌ 创建批量任务失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 批量TTS测试失败: {e}")
        return False

def test_task_list():
    """测试任务列表"""
    print("\n📋 测试任务列表...")
    try:
        response = requests.get(f"{BASE_URL}/tasks")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"总任务数: {data['total']}")
            print(f"返回任务数: {len(data['tasks'])}")
            return True
        else:
            print(f"❌ 获取任务列表失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 任务列表测试失败: {e}")
        return False

def test_vtt_download():
    """测试VTT字幕下载"""
    print("\n📄 测试VTT字幕下载...")
    try:
        # 先创建一个TTS任务
        tts_data = {
            "text": "这是一个测试VTT字幕功能的文本。",
            "voice_id": "21m00Tcm4TlvDq8ikWAM"
        }
        
        response = requests.post(f"{BASE_URL}/tts", json=tts_data)
        if response.status_code == 200:
            task_id = response.json()['task_id']
            
            # 等待任务完成
            for _ in range(30):
                status = requests.get(f"{BASE_URL}/task/{task_id}").json()
                if status['status'] == 'completed':
                    break
                time.sleep(1)
            
            if status['status'] == 'completed':
                # 下载VTT文件
                vtt_response = requests.get(f"{BASE_URL}/task/{task_id}/vtt")
                if vtt_response.status_code == 200:
                    print(f"✅ VTT字幕下载成功")
                    vtt_content = vtt_response.text[:200]  # 显示前200字符
                    print(f"VTT内容预览: {vtt_content}...")
                    return True
                else:
                    print(f"❌ VTT下载失败: {vtt_response.status_code}")
                    return False
            else:
                print("❌ 任务未完成，无法测试VTT下载")
                return False
        else:
            print(f"❌ 创建TTS任务失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ VTT下载测试失败: {e}")
        return False

def test_qc_report():
    """测试QC报告获取"""
    print("\n📊 测试QC报告获取...")
    try:
        # 先创建一个TTS任务
        tts_data = {
            "text": "这是一个测试QC报告功能的文本内容。",
            "voice_id": "21m00Tcm4TlvDq8ikWAM"
        }
        
        response = requests.post(f"{BASE_URL}/tts", json=tts_data)
        if response.status_code == 200:
            task_id = response.json()['task_id']
            
            # 等待任务完成
            for _ in range(30):
                status = requests.get(f"{BASE_URL}/task/{task_id}").json()
                if status['status'] == 'completed':
                    break
                time.sleep(1)
            
            if status['status'] == 'completed':
                # 获取QC报告
                qc_response = requests.get(f"{BASE_URL}/task/{task_id}/qc-report")
                if qc_response.status_code == 200:
                    qc_report = qc_response.json()
                    print(f"✅ QC报告获取成功")
                    print(f"总分: {qc_report['score']:.1f}/100")
                    print(f"问题数量: {len(qc_report['issues'])}")
                    print(f"建议数量: {len(qc_report['recommendations'])}")
                    return True
                else:
                    print(f"❌ QC报告获取失败: {qc_response.status_code}")
                    return False
            else:
                print("❌ 任务未完成，无法测试QC报告")
                return False
        else:
            print(f"❌ 创建TTS任务失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ QC报告测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("🧪 开始Agent B TTS API测试")
    print("=" * 50)
    
    tests = [
        ("健康检查", test_health),
        ("语音列表", test_voices),
        ("TTS功能", test_tts),
        ("VTT字幕下载", test_vtt_download),
        ("QC报告获取", test_qc_report),
        ("批量TTS", test_batch_tts),
        ("任务列表", test_task_list)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
        print("-" * 30)
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过!")
    else:
        print("⚠️  部分测试失败，请检查服务状态")

if __name__ == "__main__":
    main()

