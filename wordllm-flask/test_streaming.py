import json
import openai

# 从config.json读取配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 设置OpenAI API凭证
openai.api_key = config['openai']['OPENAI_API_KEY']
openai.api_base = config['openai']['OPENAI_API_BASE']

def test_streaming():
    print("开始测试流式输出...")
    print(f"使用模型: {config['openai']['OPENAI_MODEL_NAME']}")
    print(f"API基础URL: {openai.api_base}")
    
    try:
        # 创建流式请求
        response = openai.ChatCompletion.create(
            model=config['openai']['OPENAI_MODEL_NAME'],
            messages=[
                {"role": "system", "content": "你是一个专业的文档生成助手。"},
                {"role": "user", "content": "生成一个软件项目的简短大纲，包含5个一级标题。"}
            ],
            stream=True,
            temperature=0.7,
            max_tokens=500
        )
        
        # 按块接收并打印响应
        print("\n开始接收流式响应:")
        full_response = ""
        
        # 旧版API中的流式响应处理方式
        for chunk in response:
            if 'choices' in chunk and len(chunk['choices']) > 0:
                if 'delta' in chunk['choices'][0] and 'content' in chunk['choices'][0]['delta']:
                    content = chunk['choices'][0]['delta']['content']
                    if content:
                        full_response += content
                        print(content, end="", flush=True)  # 实时输出
        
        print("\n\n完整响应内容:")
        print(full_response)
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n测试完成。")

if __name__ == "__main__":
    test_streaming()
