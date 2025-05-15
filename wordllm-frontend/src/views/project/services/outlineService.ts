/**
 * 大纲服务 - 处理大纲生成和编辑相关API
 */

// 生成大纲
export async function generateOutline(templateId: number, formData: FormData) {
  try {
    const response = await fetch('/api/outlines/generate', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`API错误: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('生成大纲失败:', error);
    throw error;
  }
}

// 重新生成大纲
export async function regenerateOutline(
  templateId: number, 
  preservedChapters: any[] = [], 
  requirement: string = '',
  inputFile?: File
) {
  try {
    const formData = new FormData();
    formData.append('template_id', templateId.toString());
    
    if (requirement) {
      formData.append('requirement', requirement);
    }
    
    if (preservedChapters.length > 0) {
      formData.append('preserved_chapters', JSON.stringify(preservedChapters));
    }
    
    if (inputFile) {
      formData.append('input_file', inputFile);
    }
    
    const response = await fetch('/api/outlines/regenerate', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`API错误: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('重新生成大纲失败:', error);
    throw error;
  }
}

// 生成子章节
export async function generateSubchapters(templateId: number, chapters: any[], inputFile?: File) {
  try {
    const formData = new FormData();
    formData.append('template_id', templateId.toString());
    formData.append('chapters', JSON.stringify(chapters));
    
    if (inputFile) {
      formData.append('input_file', inputFile);
    }
    
    const response = await fetch('/api/outlines/generate-subchapters', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`API错误: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('生成子章节失败:', error);
    throw error;
  }
}
