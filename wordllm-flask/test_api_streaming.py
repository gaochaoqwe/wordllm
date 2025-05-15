"""
测试流式大纲生成 API 端点

此脚本会直接发送 HTTP 请求到流式大纲生成 API 端点，
并处理流式响应，模拟前端的行为。
"""
import json
import logging
import requests
import sys

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API URL (假设Flask应用运行在本地5000端口)
API_URL = "http://localhost:5000/api/outlines/generate-streaming"

def test_streaming_api():
    """测试流式大纲生成 API"""
    print(f"开始测试流式大纲生成 API: {API_URL}\n")
    
    # 构造请求数据
    data = {
        "title": "在线学习平台",
        "description": "这是一个为学生和教师提供在线学习体验的平台，包括课程管理、学习进度跟踪等功能。",
        "templateId": "1",  # 假设模板ID为1
        "language": "zh-CN"
    }
    
    print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}\n")
    
    try:
        # 发送流式请求
        print("发送请求并接收流式响应...")
        response = requests.post(API_URL, json=data, stream=True)
        
        if response.status_code != 200:
            print(f"错误: 服务器返回状态码 {response.status_code}")
            print(response.text)
            return
        
        print("开始接收流式响应:")
        
        # 跟踪完整响应
        full_content = ""
        buffer = ""
        
        # 处理流式响应
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                # 直接打印接收到的内容，无需解码
                print(chunk, end="", flush=True)
                buffer += chunk
                
                # 尝试解析已收到的完整JSON
                if buffer.startswith('{"success":true,"streaming":true,"content":"'):
                    # 提取content部分
                    try:
                        json_start = buffer.find('{"success":true,"streaming":true,"content":"')
                        content_start = json_start + len('{"success":true,"streaming":true,"content":"')
                        content = buffer[content_start:]
                        
                        # 如果是完整JSON，最后应该有结束引号和大括号
                        if content.endswith('"}'):
                            content = content[:-2]  # 去掉结尾的"}
                            
                        # 反转义内容
                        content = content.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
                        full_content = content
                    except Exception as e:
                        print(f"\n解析错误: {str(e)}")
        
        print("\n\n完整处理后的响应内容:")
        print(full_content)
        
        # 尝试解析为JSON
        try:
            json_obj = json.loads(full_content)
            print("\nJSON解析成功:")
            print(json.dumps(json_obj, ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            print("\n警告: 响应内容不是有效的JSON格式")
            
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n测试完成。")

if __name__ == "__main__":
    test_streaming_api()
