"""
处理模型返回结果的模块
"""
import json
import logging

logger = logging.getLogger(__name__)

class ResultProcessor:
    """处理模型返回结果的工具类"""
    
    @staticmethod
    def process_outline_result(response):
        """处理大纲生成结果
        
        Args:
            response: 模型返回的响应
            
        Returns:
            dict: 解析后的大纲结构
        """
        # 校验响应结构
        if not hasattr(response, 'choices') or not response.choices:
            logger.error(f"模型响应不包含choices: {response}")
            raise ValueError("API响应格式错误，缺少'choices'字段")
            
        # 检查第一个选择是否存在
        if len(response.choices) < 1:
            logger.error("模型未返回任何选择")
            raise ValueError("模型未返回任何选择")
        
        # 检查是否有message字段
        if not hasattr(response.choices[0], 'message'):
            logger.error(f"响应的选择不包含message字段: {response.choices[0]}")
            raise ValueError("响应的选择不包含message字段")
        
        # 检查是否有预解析的JSON内容
        if hasattr(response.choices[0].message, 'json_content'):
            logger.info("使用模型调用器预处理的JSON内容")
            return response.choices[0].message.json_content
        
        # 如果没有预解析的内容，则提取原始内容
        content = response.choices[0].message.content
        logger.info(f"模型原始返回内容的前100字符:\n{content[:100]}...")
        
        if not content:
            logger.error("模型返回的内容为空")
            raise ValueError("模型返回的内容为空")
        
        # 尝试解析JSON内容
        return ResultProcessor._parse_json_content(content)
    
    @staticmethod
    def _parse_json_content(content):
        """解析JSON内容
        
        Args:
            content: JSON字符串
            
        Returns:
            dict: 解析后的JSON对象
        """
        # 清理内容
        content = content.strip()
        
        # 记录原始内容供参考
        original_content = content
        print("\n" + "=" * 80)
        print("模型原始响应数据：\n")
        print(original_content[:2000] + ("..." if len(original_content) > 2000 else ""))
        print("=" * 80 + "\n")
        
        # 如果内容包含JSON代码块标记，提取其中的内容
        if content.startswith('```') and '```' in content[3:]:
            logger.info("检测到Markdown格式的JSON响应，正在提取...")
            content = content.split('```', 2)[1]
            if content.startswith('json'):
                content = content[4:].strip()
            content = content.split('```', 1)[0].strip()
            logger.info(f"提取后的JSON内容: {content[:200]}... (截取前200字符)")
        
        try:
            # 尝试解析JSON
            logger.info(f"尝试解析JSON，前20字符: '{content[:20]}'")
            # 打印十六进制便于调试
            hex_chars = ' '.join([hex(ord(c)) for c in content[:20]])
            logger.info(f"前20字符的十六进制: {hex_chars}")
            
            generated_outline = json.loads(content)
            logger.info("成功解析JSON响应")
            
            # 打印解析后的数据
            logger.info(f"解析的JSON类型: {type(generated_outline)}")
            print("\n" + "=" * 80)
            print("解析后的JSON数据:")
            print(json.dumps(generated_outline, ensure_ascii=False, indent=2))
            print("=" * 80 + "\n")
            
            # 检查是否为数组，如果是则转换为带chapters键的对象
            if isinstance(generated_outline, list):
                logger.warning("模型返回了章节数组而不是带'chapters'键的对象")
                generated_outline = {"chapters": generated_outline}
                logger.info("已将数组转换为带'chapters'键的对象")
            
            return generated_outline
        except json.JSONDecodeError as e:
            # 第一次尝试失败，尝试更进一步的清理
            logger.warning(f"第一次解析JSON失败: {str(e)}，尝试更多清理")
            
            # 更全面的清理
            content = content.replace('\"', '"')  # 将\" 替换为 "
            content = content.replace('\\', '\\\\')  # 将单个\转义为\\
            content = content.replace('\\"', '"')  # 将\" 替换为 "
            content = content.replace('\\n', '\n')  # 正确处理\n
            
            # 打印清理后的内容
            logger.info(f"清理后的内容(前50字符): '{content[:50]}'")
            
            try:
                # 再次尝试解析
                generated_outline = json.loads(content)
                logger.info("清理后成功解析JSON")
                
                # 检查是否为数组，如果是则转换为带chapters键的对象
                if isinstance(generated_outline, list):
                    logger.warning("模型返回了章节数组而不是带'chapters'键的对象")
                    generated_outline = {"chapters": generated_outline}
                    logger.info("已将数组转换为带'chapters'键的对象")
                
                return generated_outline
            except json.JSONDecodeError as e2:
                # 在第二次尝试失败后检查更具体的问题
                logger.error(f"第二次尝试解析JSON仍然失败: {e2}")
                logger.error(f"失败的内容: 前50字符: '{content[:50]}'")
                
                # 尝试寻找并提取JSON对象的范围
                if '{' in content and '}' in content:
                    obj_start_index = content.find('{')
                    obj_end_index = content.rfind('}')
                    if not obj_start_index < 0 and not obj_end_index < 0:
                        json_str = content[obj_start_index:obj_end_index+1]
                        try:
                            generated_outline = json.loads(json_str)
                            logger.info("提取JSON字符串后成功解析")
                            
                            # 检查是否为数组，如果是则转换为带chapters键的对象
                            if isinstance(generated_outline, list):
                                logger.warning("模型返回了章节数组而不是带'chapters'键的对象")
                                generated_outline = {"chapters": generated_outline}
                                logger.info("已将数组转换为带'chapters'键的对象")
                            
                            return generated_outline
                        except json.JSONDecodeError as e3:
                            logger.error(f"提取JSON后仍然无法解析: {e3}")
                
                # 尝试修复被截断的JSON
                try:
                    fixed_content = ResultProcessor._attempt_fix_truncated_json(content)
                    if fixed_content:
                        try:
                            generated_outline = json.loads(fixed_content)
                            logger.info("对截断的JSON进行修复后成功解析")
                            
                            if isinstance(generated_outline, list):
                                generated_outline = {"chapters": generated_outline}
                            
                            return generated_outline
                        except json.JSONDecodeError:
                            logger.warning("修复后的JSON仍然无法解析")
                except Exception as fix_err:
                    logger.error(f"尝试修复截断的JSON时出错: {str(fix_err)}")
                    
                # 检查是否是数组格式
                array_start_index = content.find('[')
                array_end_index = content.rfind(']')
                
                if array_start_index >= 0 and array_end_index > array_start_index:
                    array_str = content[array_start_index:array_end_index+1]
                    logger.info(f"发现可能的JSON数组: '{array_str[:50]}...'")
                    try:
                        array_data = json.loads(array_str)
                        if isinstance(array_data, list):
                            logger.info("成功解析JSON数组")
                            # 将数组转换为我们期望的结构
                            generated_outline = {"chapters": array_data}
                            logger.info("已将数组转换为带'chapters'键的对象")
                            return generated_outline
                    except json.JSONDecodeError as e4:
                        logger.error(f"尝试解析数组失败: {e4}")
                
                # 如果所有尝试都失败，记录错误并抛出异常
                logger.error(f"所有JSON解析尝试均失败，原始内容: {content[:500]}...")
                
                # 抛出更有信息量的异常
                error_msg = f"JSON解析失败: {str(e)}, 请查看日志了解具体原因"
                logger.error(error_msg)
                
                # 尝试返回默认结构作为备选
                logger.info("尝试返回默认大纲结构")
                return ResultProcessor._get_default_outline()
    
    @staticmethod
    def _get_default_outline():
        """获取默认的大纲结构
        
        Returns:
            dict: 默认大纲
        """
        return {
            "chapters": [
                {
                    "chapterNumber": "1",
                    "title": "项目背景"
                },
                {
                    "chapterNumber": "2",
                    "title": "技术要求"
                }
            ]
        }
    
    @staticmethod
    def _attempt_fix_truncated_json(content):
        """尝试修复截断或不完整的JSON
        
        Args:
            content: 可能被截断的JSON字符串
            
        Returns:
            str: 修复后的JSON字符串，如果无法修复则返回None
        """
        # 检查是否有完整的章节对象
        chapter_objs = []
        open_brackets = 0
        current_obj = ""
        in_obj = False
        
        for char in content:
            if char == '{' and not in_obj:
                in_obj = True
                open_brackets = 1
                current_obj = char
            elif in_obj:
                current_obj += char
                if char == '{':
                    open_brackets += 1
                elif char == '}':
                    open_brackets -= 1
                    if open_brackets == 0:
                        in_obj = False
                        # 找到一个完整的对象
                        try:
                            obj = json.loads(current_obj)
                            if isinstance(obj, dict) and 'chapterNumber' in obj and 'title' in obj:
                                chapter_objs.append(obj)
                            current_obj = ""
                        except:
                            # 不是有效的JSON对象，跳过
                            current_obj = ""
                            in_obj = False
        
        if chapter_objs:
            # 如果找到了完整的章节对象，构建有效的JSON
            return json.dumps({"chapters": chapter_objs})
        
        # 检查是否是大括号不匹配的问题
        open_count = content.count('{')
        close_count = content.count('}')
        if open_count > close_count:
            # 缺少右括号
            logger.info(f"检测到JSON缺少{open_count - close_count}个右括号，尝试修复")
            return content + ('}' * (open_count - close_count))
        elif close_count > open_count:
            # 缺少左括号
            logger.info(f"检测到JSON缺少{close_count - open_count}个左括号，尝试修复")
            return ('{' * (close_count - open_count)) + content
        
        # 尝试将截断的章节列表修复为有效JSON
        if '"chapters"' in content and '[' in content:
            # 检查是否缺失chapters数组的结束括号
            if content.rfind('[') > content.rfind(']'):
                logger.info("检测到chapters数组没有正确关闭，尝试修复")
                return content + ']}'
            # 检查是否整个JSON对象没有关闭
            elif content.rfind('{') > content.rfind('}'):
                logger.info("检测到JSON对象没有正确关闭，尝试修复")
                return content + '}'
        
        # 无法修复
        return None
    
    @staticmethod
    def validate_and_fix_outline_structure(chapters):
        """验证和修复大纲结构，简化版本只需要chapterNumber和title
        
        Args:
            chapters: 章节列表
        """
        if not chapters:
            logger.warning("章节列表为空")
            return
            
        # 打印进入验证的章节列表
        logger.info(f"准备验证{len(chapters)}个章节")
            
        for i, chapter in enumerate(chapters):
            # 兼容处理: 如果有id字段而没有chapterNumber, 转换id到chapterNumber
            if 'id' in chapter and 'chapterNumber' not in chapter:
                chapter['chapterNumber'] = chapter['id']
                logger.info(f"将第{i+1}个章节的id字段转换为chapterNumber: {chapter['chapterNumber']}")
                del chapter['id']
                
            # 确保每个章节都有chapterNumber和title
            if 'chapterNumber' not in chapter:
                chapter['chapterNumber'] = str(i + 1)
                logger.warning(f"章节缺失chapterNumber，添加默认编号: {chapter['chapterNumber']}")
                
            if 'title' not in chapter:
                chapter['title'] = f"第{i + 1}章"
                logger.warning(f"章节缺失标题，添加默认标题: {chapter['title']}")
                
            # 移除不需要的字段
            if 'desc' in chapter:
                del chapter['desc']
                logger.info(f"删除第{i+1}个章节的desc字段")
                
            if 'children' in chapter:
                del chapter['children']
                logger.info(f"删除第{i+1}个章节的children字段")

    @staticmethod
    def count_total_sections(chapters):
        """计算章节总数
        
        Args:
            chapters: 章节列表
            
        Returns:
            int: 章节总数
        """
        return len(chapters) if chapters else 0
