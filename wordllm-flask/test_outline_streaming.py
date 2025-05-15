"""
测试大纲流式生成功能

此脚本直接调用修改后的 ModelCaller 和生成大纲的函数，
不依赖于HTTP请求，直接验证后端流式输出功能是否正常。
"""
import json
import sys
import logging
from app.services.ai.model_caller import ModelCaller
from openai import OpenAI

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 从config.json读取配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 新版API创建OpenAI客户端
openai_client = OpenAI(
    api_key=config['openai']['OPENAI_API_KEY'], 
    base_url=config['openai']['OPENAI_API_BASE']
)

def test_outline_streaming():
    """测试大纲流式生成功能"""
    print(f"开始测试大纲流式生成...\n")
    print(f"使用模型: {config['openai']['OPENAI_MODEL_NAME']}")
    print(f"API基础URL: {openai_client.base_url}\n")
    
    # 构建用于测试的提示词
    prompt = """
    我需要一份软件项目文档大纲，该项目是一个在线学习平台。
    请为这个项目生成一个详细的文档大纲，包含至少5个主要章节和相应的子章节。
    """
    
    try:
        print("正在调用模型生成大纲内容（流式输出）...\n")
        
        # 调用 ModelCaller 的流式方法，传入新版客户端对象
        response_stream = ModelCaller.call_model_streaming(
            openai_client,  # 新版SDK的客户端对象
            config['openai']['OPENAI_MODEL_NAME'], 
            prompt
        )
        
        print("----- 开始接收流式响应 -----")
        full_response = ""
        
        # 处理新版OpenAI API的流式响应
        for chunk in response_stream:
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    # 实时输出到控制台
                    print(content, end="", flush=True)
        
        print("\n\n----- 流式响应结束 -----")
        print("\n完整响应内容:")
        print(full_response)
        
        # 尝试解析JSON
        try:
            json_response = json.loads(full_response)
            print("\nJSON解析成功:")
            print(json.dumps(json_response, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("\n警告: 响应内容不是有效的JSON格式")
            
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n测试完成。")

if __name__ == "__main__":
    test_outline_streaming()
