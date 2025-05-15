"""
负责调用AI模型的模块
"""
import os
import logging
import json
import openai
import re  # 用于正则表达式处理

# 只在文件顶部初始化一次logger，统一名称为wordllm
logger = logging.getLogger("wordllm")
if not logger.hasHandlers():
    handler = logging.FileHandler("wordllm.log", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class ModelCaller:
    """负责调用AI模型的工具类"""
    
    # 类变量，用于存储最后一次的原始响应(用于调试)
    _last_raw_response = None
    
    @staticmethod
    def call_model_streaming(client, model, prompt, system_prompt=None):
        """使用流式响应调用OpenAI模型生成文本
        
        Args:
            client: OpenAI客户端
            model: 模型名称
            prompt: 用户提示词
            system_prompt: 系统提示词，默认为None
            
        Returns:
            iterator: 生成器对象，用于流式返回内容
        """
        logger.info(f"【DEBUG】即将流式请求大模型 {model}，prompt内容如下：\n{prompt}\n【END PROMPT】")

        if not system_prompt:
            system_prompt = "你是一个专业的文档结构规划专家，擅长根据模板和输入需求生成合适的标书章节大纲。请用JSON格式返回结果。"

        # 强化系统提示词，确保返回JSON
        enhanced_system_prompt = """你是一个专业的文档结构规划专家，擅长根据模板和输入需求生成合适的标书章节大纲。

你的响应必须是一个有效的JSON对象，包含一个"chapters"数组，每个章节的格式需要遵循以下规则：
1. 所有章节只包含"chapterNumber"和"title"两个字段
2. 所有字段名和值必须用双引号包裹
3. 章节编号使用字符串格式，如"1"，"2"，而不是数字格式
4. 一级章节编号用数字，如"1"，"2"；二级章节编号用"父章节.序号"格式，如"1.1"，"1.2"等
5. 严格确保JSON格式正确，所有括号和引号都要匹配

不要在JSON外添加任何注释或解释。

示例格式:
{"chapters": [
  {"chapterNumber": "1", "title": "项目概述"},
  {"chapterNumber": "1.1", "title": "项目背景"},
  {"chapterNumber": "2", "title": "技术方案"}
]}
"""
        
        # 打印将要发送的提示词摘要（日志中）
        logger.info(f"系统提示词: {enhanced_system_prompt[:100]}...")
        logger.info(f"用户提示词(前100字符): {prompt[:100]}...")
        
        try:
            # 检查并初始化 OpenAI 客户端对象
            if client is None:
                from openai import OpenAI
                import json
                import os
                
                # 使用项目根目录的绝对路径找到配置文件
                # 当前脚本在 app/services/ai/model_caller.py
                # 需要上码3级目录才能到项目根目录
                current_dir = os.path.dirname(os.path.abspath(__file__))
                root_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
                config_path = os.path.join(root_dir, 'config.json')
                
                logger.info(f"尝试从 {config_path} 读取配置")
                
                # 读取配置文件
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                client = OpenAI(
                    api_key=config['openai']['OPENAI_API_KEY'],
                    base_url=config['openai']['OPENAI_API_BASE']
                )
                
                logger.info(f"OpenAI 客户端初始化成功，使用 API 基础 URL: {config['openai']['OPENAI_API_BASE']}")
                
                # 全局配置OpenAI，为了兼容性
                import openai
                openai.api_key = config['openai']['OPENAI_API_KEY']
                openai.api_base = config['openai']['OPENAI_API_BASE']
            
            # 新版 OpenAI SDK (1.0.0+) 流式调用方式
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": enhanced_system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                stream=True  # 启用流式响应
            )
            
            logger.info("流式模型调用已启动")
            
            # 返回响应流
            return response
        except Exception as e:
            logger.error(f"流式调用错误: {str(e)}")
            logger.exception(e)  # 输出完整堆栈跟踪
            raise
    
    @staticmethod
    def call_model(client, model, prompt, system_prompt=None):
        """调用OpenAI模型生成文本
        
        Args:
            client: OpenAI客户端
            model: 模型名称
            prompt: 用户提示词
            system_prompt: 系统提示词，默认为None
            
        Returns:
            dict: 模型返回的结果
        """
        logger.info(f"【DEBUG】即将请求大模型 {model}，prompt内容如下：\n{prompt}\n【END PROMPT】")

        if not system_prompt:
            system_prompt = "你是一个专业的文档结构规划专家，擅长根据模板和输入需求生成合适的标书章节大纲。请用JSON格式返回结果。"

        # 捕获模型请求异常
        try:
            # 这里假设 client 是已经用 config 初始化好的 openai 客户端
            # response = client.chat.completions.create(...)
            logger.info(f"【DEBUG】已成功发起模型请求，参数: model={model}")
        except Exception as e:
            logger.error(f"模型请求异常: model={model}, prompt={prompt}, error={e}")
            raise
        
        # 打印完整的请求数据（根据用户要求）
        print("\n" + "=" * 80)
        print("\u539f始请求数据：")
        print("\u7cfb统提示词: \n" + system_prompt)
        print("\n\u7528户提示词: \n" + prompt)
        print("=" * 80 + "\n")
        
        # 使用强化的系统提示词，确保返回JSON
        logger.info("使用强化系统提示词调用API")
        
        # 强化系统提示词，确保返回JSON
        enhanced_system_prompt = """你是一个专业的文档结构规划专家，擅长根据模板和输入需求生成合适的标书章节大纲。

你的响应必须是一个有效的JSON对象，包含一个"chapters"数组，每个章节的格式需要遵循以下规则：
1. 所有章节只包含"chapterNumber"和"title"两个字段
2. 所有字段名和值必须用双引号包裹
3. 章节编号使用字符串格式，如"1"，"2"，而不是数字格式
4. 一级章节编号用数字，如"1"，"2"；二级章节编号用"父章节.序号"格式，如"1.1"，"1.2"等
5. 严格确保JSON格式正确，所有括号和引号都要匹配

不要在JSON外添加任何注释或解释。

示例格式:
{"chapters": [
  {"chapterNumber": "1", "title": "项目概述"},
  {"chapterNumber": "1.1", "title": "项目背景"},
  {"chapterNumber": "2", "title": "技术方案"}
]}
"""
        # 打印将要发送的提示词摘要（日志中）
        logger.info(f"系统提示词: {enhanced_system_prompt[:100]}...")
        logger.info(f"用户提示词(前100字符): {prompt[:100]}...")
        
        # 调用API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        logger.info("模型调用成功")
        
        # 打印响应详情以便调试
        logger.info(f"响应对象类型: {type(response)}")
        
        # 检查响应的选择
        if hasattr(response, 'choices') and response.choices:
            logger.info(f"选择数量: {len(response.choices)}")
            
            if len(response.choices) > 0 and hasattr(response.choices[0], 'message'):
                content = response.choices[0].message.content
                # 存储原始响应用于调试
                ModelCaller._last_raw_response = content
                
                # 打印完整的原始响应（根据用户要求）
                print("\n" + "=" * 80)
                print("\u6a21型原始响应数据：")
                print(content)
                print("=" * 80 + "\n")
                
                logger.info(f"原始响应内容的前50字符: '{content[:50]}'")
                logger.info(f"原始响应内容的总长度: {len(content)}")
                
                # 将完整原始响应写入日志，帮助调试
                logger.debug(f"完整原始响应:\n{content}")
                
                # 检测并清理无效的JSON转义字符
                cleaned_content = ModelCaller._fix_invalid_json_escape(content)
                if cleaned_content != content:
                    logger.info("清理了无效的JSON转义字符")

                # 新增：根据调用场景判断是否需要JSON解析
                # 如果prompt或调用方要求返回纯文本（如文档内容生成），则直接返回字符串
                # 这里假定有一个全局变量或上下文可判断场景（如通过参数传递），此处用简单判断
                if '\\n' in cleaned_content or '\\r' in cleaned_content or cleaned_content.strip().startswith('#'):
                    # 可能是markdown或纯文本，不做JSON解析
                    logger.info("检测到内容为纯文本或Markdown，跳过JSON解析，直接返回字符串内容")
                    response.choices[0].message.json_content = cleaned_content
                else:
                    # 尝试解析JSON
                    try:
                        result = json.loads(cleaned_content)
                        logger.info("成功解析JSON")
                        if "chapters" not in result and isinstance(result, list):
                            logger.warning("模型返回了一个数组而不是带'chapters'键的对象")
                            result = {"chapters": result}
                            logger.info("已将数组转换为带'chapters'键的对象")
                        response.choices[0].message.json_content = result
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON解析失败: {str(e)}, 尝试更多修复方法...")
                        fixed_content = ModelCaller._attempt_json_fix(cleaned_content)
                        if fixed_content != cleaned_content:
                            logger.info("已应用额外的JSON修复")
                            try:
                                result = json.loads(fixed_content)
                                logger.info("修复后成功解析JSON")
                                response.choices[0].message.json_content = result
                            except json.JSONDecodeError as e2:
                                logger.error(f"修复后仍然无法解析JSON: {str(e2)}")
            else:
                logger.warning("未找到有效的响应内容")
        else:
            logger.warning("响应对象不包含选择")
        
        return response
    
    @staticmethod
    def _fix_invalid_json_escape(content):
        """修复JSON中的无效转义字符
        
        Args:
            content: 原始内容
            
        Returns:
            str: 修复后的内容
        """
        # 去除开头和结尾的空白字符
        content = content.strip()
        
        # 常见的无效转义字符模式
        invalid_escapes = [
            r'\[^"\\bfnrtu]',  # 无效的转义序列，如 \k
        ]
        
        # 替换无效转义
        for pattern in invalid_escapes:
            content = re.sub(pattern, lambda m: m.group(0).replace('\\', '\\\\'), content)
        
        return content
    
    @staticmethod
    def _attempt_json_fix(content):
        """尝试修复损坏的JSON
        
        Args:
            content: 原始内容
            
        Returns:
            str: 修复后的内容
        """
        # 清理标记语言代码块
        if content.startswith('```') and '```' in content[3:]:
            # 清理Markdown代码块
            parts = content.split('```')
            if len(parts) >= 3:
                # 提取代码块内容
                content = parts[1]
                if content.lstrip().startswith('json'):
                    content = content[4:].strip()
        
        # 如果内容不以'{'(对象)或'['(数组)开头，尝试找到这些字符
        if not content.lstrip().startswith('{') and not content.lstrip().startswith('['):
            # 找到第一个花括号或方括号
            obj_start = content.find('{')
            arr_start = content.find('[')
            
            if obj_start >= 0 and (arr_start < 0 or obj_start < arr_start):
                content = content[obj_start:]
            elif arr_start >= 0:
                content = content[arr_start:]
        
        # 确保 JSON 结束时匹配正确
        if content.count('{') > content.count('}'):
            # 添加缺失的右括号
            content += '}' * (content.count('{') - content.count('}'))
        elif content.count('[') > content.count(']'):
            # 添加缺失的右方括号
            content += ']' * (content.count('[') - content.count(']'))
        
        return content
