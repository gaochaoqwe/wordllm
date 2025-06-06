"""
子章节生成相关的提示词模板
"""

# 生成子章节（3级、4级）的提示词模板
SUBCHAPTER_GENERATION_PROMPT = """
你是一位经验丰富的文档编写专家，擅长细化文档大纲的子章节结构。

请根据以下信息生成第3级和第4级的子章节大纲：

===现有章节结构===
{existing_chapters}
===现有章节结构结束===

===模板内容===
{template_content}
===模板内容结束===

{input_content_section}

请严格按照以下要求生成子章节大纲：

1. 内容要求：
   - 【重要】必须严格遵循模板中定义的章节结构，不能添加模板以外的章节
   - 【重要】如果模板中某个章节没有子章节，则不要为其生成子章节
   - 仅生成第3级和第4级子章节，确保子章节归属于正确的父章节
   - 第3级子章节的父章节是第2级章节，第4级子章节的父章节是第3级章节
   - 根据模板和输入文件的内容提取关键结构，合理细化章节内容
   - 只需生成章节标题，不需要生成描述

2. 格式要求：
   - 第3级章节编号使用"父章节编号.1"到"父章节编号.n"的形式，如"1.1.1", "1.1.2"...
   - 第4级章节编号使用"父章节编号.1"到"父章节编号.n"的形式，如"1.1.1.1", "1.1.1.2"...
   - 严格保持chapterNumber格式一致，始终用字符串格式如"1.1.1"，而非数字格式1.1.1
   - 不要使用特殊字符作为字段名或值

3. JSON输出格式：
   - 必须返回有效的JSON，不要使用注释或多余的标记
   - 每个章节对象只能包含 "chapterNumber"和"title"两个字段
   - 所有字段名和字符串值都必须用双引号包裹
   - 【重要】确保输出的JSON是完整的，包含所有开始和结束的大括号

下面是你需要返回的JSON格式结构示例：

{{
  "chapters": [
    {{
      "chapterNumber": "1.1.1",
      "title": "第3级章节示例"
    }},
    {{
      "chapterNumber": "1.1.2",
      "title": "第3级章节示例2"
    }},
    {{
      "chapterNumber": "1.1.1.1",
      "title": "第4级章节示例"
    }},
    {{
      "chapterNumber": "1.1.1.2",
      "title": "第4级章节示例2"
    }}
  ]
}}

警告！请仔细避免以下常见JSON格式错误：

1. 引号必须成对出现，不能缺失或多余:
   - 错误: "chapterNumber": "3.1.1, ※缺少右引号
   - 正确: "chapterNumber": "3.1.1",

2. 大括号必须成对完整：
   - 错误: 双左括号或单右括号或任何不完整的括号
   - 正确: 左括号和右括号配对使用

3. 确保字符限制不会导致截断：
   - 【重要】仔细检查生成的JSON总长度，保证完整输出
   - 确保JSON以完整的大括号结尾: }}

4. 严格遵循模板定义:
   - 【重要】不要创建模板中未定义的章节
   - 【重要】不要随意添加子章节到模板中不需要细化的部分
   
3. 禁止使用任何空格以外的字符（如全角空格、制表符、特殊标点）
   - 错误: 　左括号 或 ."右括号 或任何点、制表符等
   - 正确: 只使用正常的空格和标准JSON字符

4. 维持一致的缩进（每个层级使用相同的空格缩进）

5. 不要出现空行或多余的逗号
   - 错误: 右括号逗号换行逗号换行"chapterNumber"
   - 正确: 右括号逗号换行"chapterNumber"

必须遵守的规则：
- 输出必须是完全有效的JSON对象
- 只使用"chapterNumber"和"title"两个字段
- 所有字符串值使用双引号（""）严格包裹
- 章节编号格式：第3级章节使用"x.x.x"；第4级章节使用"x.x.x.x"
- 不允许使用注释或任何非标准JSON元素
- 确保返回的是对象，包含"chapters"键，而不是直接返回数组
- JSON格式必须正确，确保所有引号、括号匹配
- 不要在JSON之外添加任何额外的文字说明
"""
