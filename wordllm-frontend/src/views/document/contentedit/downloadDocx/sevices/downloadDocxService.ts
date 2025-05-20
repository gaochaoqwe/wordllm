// 服务：处理 docx 下载相关的业务逻辑
import axios from 'axios';
import { ElMessage } from 'element-plus';

/**
 * 格式设置接口
 */
export interface ExportSettings {
  format: 'docx' | 'pdf' | 'txt';
  scope: 'all' | 'current';
  currentChapter?: number;
  margins?: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
  section_number_style?: {
    number_style: 'none' | 'chapter' | 'number';
  };
  level1_style?: {
    fontFamily: string;
    fontSize: string;
    alignment: string;
    bold: boolean;
    firstLineIndent: number;
    lineSpacing: number;
  };
  level2_style?: {
    fontFamily: string;
    fontSize: string;
    alignment: string;
    bold: boolean;
    firstLineIndent: number;
    lineSpacing: number;
  };
  level3_style?: {
    fontFamily: string;
    fontSize: string;
    alignment: string;
    bold: boolean;
    firstLineIndent: number;
    lineSpacing: number;
  };
  text_style?: {
    fontFamily: string;
    fontSize: string;
    alignment: string;
    bold: boolean;
    firstLineIndent: number;
    lineSpacing: number;
  };
}

/**
 * 下载文档
 * @param projectId 项目ID
 * @param settings 导出设置
 * @returns Promise
 */
export async function downloadDocx(projectId: number, settings: ExportSettings): Promise<boolean> {
  try {
    console.log('[downloadDocxService] 开始下载文档，参数:', settings);
    
    // 显示加载提示
    ElMessage.info('正在生成文档，请稍候...');
    
    // 调用后端API
    const response = await axios.post(
      `/api/projects/${projectId}/export`,
      settings,
      {
        responseType: 'blob' // 重要：接收二进制数据
      }
    );
    
    // 创建Blob对象
    const blob = new Blob([response.data], {
      type: getContentType(settings.format)
    });
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', getFileName(projectId, settings.format));
    document.body.appendChild(link);
    
    // 触发下载
    link.click();
    
    // 清理
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    // 显示成功提示
    ElMessage.success('文档下载成功');
    return true;
  } catch (error) {
    console.error('[downloadDocxService] 下载文档失败:', error);
    ElMessage.error('文档下载失败，请重试');
    return false;
  }
}

/**
 * 根据格式获取内容类型
 */
function getContentType(format: string): string {
  switch (format) {
    case 'docx':
      return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
    case 'pdf':
      return 'application/pdf';
    case 'txt':
      return 'text/plain';
    default:
      return 'application/octet-stream';
  }
}

/**
 * 获取文件名
 */
function getFileName(projectId: number, format: string): string {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
  return `项目文档_${projectId}_${timestamp}.${format}`;
}
