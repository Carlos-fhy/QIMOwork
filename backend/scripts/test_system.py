#!/usr/bin/env python3
"""
江苏旅游知识库测试脚本
用于测试系统功能是否正常
"""

import sys
import asyncio
import requests
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_health_check():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过: {data['status']}")
            if 'vector_db' in data:
                print(f"📊 向量数据库文档数: {data['vector_db'].get('document_count', 0)}")
            return True
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_regions():
    """测试地区列表接口"""
    print("\n🌍 测试地区列表接口...")
    try:
        response = requests.get('http://localhost:5000/api/regions', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 地区列表获取成功，共 {len(data['regions'])} 个地区")
            print(f"📋 地区列表: {', '.join(data['regions'])}")
            return True
        else:
            print(f"❌ 地区列表获取失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 地区列表获取异常: {e}")
        return False

def test_chat():
    """测试普通问答接口"""
    print("\n💬 测试普通问答接口...")
    try:
        payload = {
            "question": "苏州有哪些著名景点？",
            "region": "all",
            "k": 3
        }
        
        response = requests.post(
            'http://localhost:5000/api/chat',
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ 普通问答测试成功")
                print(f"📝 回答长度: {len(data['answer'])} 字符")
                print(f"🔗 来源数量: {len(data.get('sources', []))}")
                print(f"💭 回答预览: {data['answer'][:100]}...")
                return True
            else:
                print(f"❌ 问答失败: {data.get('error', '未知错误')}")
                return False
        else:
            print(f"❌ 问答请求失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 问答测试异常: {e}")
        return False

def test_stream_chat():
    """测试流式问答接口"""
    print("\n🌊 测试流式问答接口...")
    try:
        import requests
        
        params = {
            "question": "扬州的美食有哪些？",
            "region": "all", 
            "k": 3
        }
        
        response = requests.get(
            'http://localhost:5000/api/chat/stream',
            params=params,
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ 流式连接建立成功")
            
            content_received = False
            sources_received = False
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]  # 移除 'data: ' 前缀
                        if data_str == '[DONE]':
                            break
                        try:
                            import json
                            data = json.loads(data_str)
                            if data.get('content'):
                                content_received = True
                            if data.get('done') and data.get('sources'):
                                sources_received = True
                                break
                        except json.JSONDecodeError:
                            continue
            
            if content_received:
                print("✅ 流式内容接收成功")
            if sources_received:
                print("✅ 来源信息接收成功")
                
            return content_received
        else:
            print(f"❌ 流式连接失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 流式测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 江苏旅游知识库系统测试")
    print("=" * 60)
    
    print("⏳ 等待服务启动...")
    time.sleep(2)
    
    test_results = []
    
    # 执行测试
    test_results.append(("健康检查", test_health_check()))
    test_results.append(("地区列表", test_regions()))
    test_results.append(("普通问答", test_chat()))
    test_results.append(("流式问答", test_stream_chat()))
    
    # 统计结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<12} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查系统配置。")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)