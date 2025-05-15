/**
 * 文档服务 - 处理文档内容生成和编辑相关API
 */

// 获取项目信息，包括模板ID
async function getProjectInfo(projectId: string | number) {
  try {
    console.log(`【API调用】获取项目ID=${projectId}的信息`);
    const response = await fetch(`/api/projects/${projectId}`);
    
    if (!response.ok) {
      throw new Error(`获取项目信息失败: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('【API调用】获取项目信息成功:', result);
    return result;
  } catch (error) {
    console.error('【API调用】获取项目信息失败:', error);
    throw error;
  }
}

// 生成章节内容
export async function generateChapterContent(templateIdParam: number|string|null, chapter: Record<string, unknown>) {
  console.log('【API调用】生成章节内容 - 开始', { templateIdParam, chapter });
  
  // 转换章节格式，确保字段名称符合后端要求
  const preparedChapter = {
    ...chapter,
    chapter_number: chapter.chapterNumber || chapter.chapter_number || '',
    id: chapter.id || chapter.chapterNumber || '',
    title: chapter.title || '未命名章节',
    project_id: chapter.project_id || chapter.projectId
  };
  
  try {
    // 先获取项目信息和模板ID
    let templateId = templateIdParam;
    const projectId = preparedChapter.project_id;
    
    // 如果没有templateId但有projectId，则从项目信息中获取
    if ((!templateId || templateId === 'null' || templateId === 'undefined') && projectId) {
      console.log(`【API调用】模板ID未提供，从项目信息中获取，项目ID:${projectId}`);
      try {
        const projectInfo = await getProjectInfo(projectId);
        if (projectInfo.success && projectInfo.data && projectInfo.data.template_id) {
          templateId = projectInfo.data.template_id;
          console.log(`【API调用】成功从项目获取模板ID: ${templateId}`);
        } else {
          console.warn('【API调用】项目信息中无模板ID:', projectInfo);
        }
      } catch (err) {
        console.error('【API调用】获取项目模板ID失败:', err);
      }
    }
    
    // 再次检查templateId是否存在
    if (!templateId) {
      throw new Error('无法获取模板ID，请先选择模板');
    }
    
    // 确保templateId为数字
    const numericTemplateId = typeof templateId === 'string' ? parseInt(templateId) : templateId;
    
    // 构建请求体
    const requestBody = {
      template_id: numericTemplateId,
      project_id: projectId,
      chapter_number: preparedChapter.chapter_number,
      chapters: [preparedChapter]
    };
    
    console.log('【API调用】请求数据:', JSON.stringify(requestBody));
    
    // 发送请求
    const response = await fetch('/api/documents/generate-content', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });
    
    console.log('【API调用】响应状态:', response.status, response.statusText);
    
    if (!response.ok) {
      throw new Error(`API错误: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    console.log('【API调用】响应数据:', result);
    return result;
  } catch (error) {
    console.error('【API调用】生成章节内容失败:', error);
    throw error;
  }
}

// 生成所有章节内容
export async function generateAllContent(templateIdParam: number|string|null, chapters: Record<string, unknown>[]) {
  try {
    if (!chapters || chapters.length === 0) {
      throw new Error('未提供章节数据');
    }
    
    // 获取项目ID
    const projectId = chapters[0].project_id || chapters[0].projectId;
    if (!projectId) {
      throw new Error('章节数据中未包含项目ID');
    }
    
    // 先获取项目信息和模板ID
    let templateId = templateIdParam;
    
    // 如果没有templateId，则从项目信息中获取
    if ((!templateId || templateId === 'null' || templateId === 'undefined') && projectId) {
      console.log(`【API调用】批量生成内容：模板ID未提供，从项目信息中获取，项目ID:${projectId}`);
      try {
        const projectInfo = await getProjectInfo(projectId);
        if (projectInfo.success && projectInfo.data && projectInfo.data.template_id) {
          templateId = projectInfo.data.template_id;
          console.log(`【API调用】成功从项目获取模板ID: ${templateId}`);
        } else {
          console.warn('【API调用】项目信息中无模板ID:', projectInfo);
        }
      } catch (err) {
        console.error('【API调用】获取项目模板ID失败:', err);
      }
    }
    
    // 再次检查templateId是否存在
    if (!templateId) {
      throw new Error('无法获取模板ID，请先选择模板');
    }
    
    // 确保templateId为数字
    const numericTemplateId = typeof templateId === 'string' ? parseInt(templateId) : templateId;
    
    const response = await fetch('/api/documents/generate-content', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        template_id: numericTemplateId,
        project_id: projectId,
        chapters: chapters
      })
    });
    
    if (!response.ok) {
      throw new Error(`API错误: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('生成所有内容失败:', error);
    throw error;
  }
}

// 与AI助手聊天
export async function chatWithAI(templateId: number, chapter: Record<string, unknown>, messages: unknown[]) {
  try {
    const response = await fetch('/api/documents/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        template_id: templateId,
        chapter: chapter,
        messages: messages
      })
    });
    
    if (!response.ok) {
      throw new Error(`AI聊天API错误: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('AI聊天请求失败:', error);
    throw error;
  }
}

// 保存文档内容
export async function saveDocumentContent(documentId: number, contents: Record<string, unknown>) {
  // 这是一个简化的实现，实际项目中可能需要真正的后端保存功能
  console.log('保存文档内容:', documentId, contents);
  
  // 模拟成功响应
  return Promise.resolve({
    success: true,
    data: {
      documentId,
      saved: true,
      timestamp: new Date().toISOString()
    }
  });
}
