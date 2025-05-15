/**
 * 模板工具函数模块
 * 提供各种格式化和辅助函数
 */

/**
 * 格式化日期
 * @param dateStr 日期字符串
 * @returns 格式化后的日期字符串
 */
export function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  
  try {
    const date = new Date(dateStr)
    return date.toLocaleString()
  } catch (error) {
    console.error('日期格式化错误:', error)
    return dateStr || '-'
  }
}

/**
 * 格式化文件大小
 * @param size 文件大小(字节)
 * @returns 格式化后的文件大小
 */
export function formatFileSize(size?: number): string {
  if (size === undefined || size === null) return '-'
  
  try {
    if (size < 1024) {
      return `${size} B`
    } else if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(1)} KB`
    } else if (size < 1024 * 1024 * 1024) {
      return `${(size / (1024 * 1024)).toFixed(1)} MB`
    } else {
      return `${(size / (1024 * 1024 * 1024)).toFixed(1)} GB`
    }
  } catch (error) {
    console.error('文件大小格式化错误:', error)
    return size?.toString() || '-'
  }
}

/**
 * 安全获取对象属性
 * 避免在访问嵌套对象属性时出现错误
 * 
 * @param obj 目标对象
 * @param path 属性路径
 * @param defaultValue 默认值
 * @returns 属性值或默认值
 */
export function getProperty<T, D = undefined>(
  // 使用Record类型替代any
  obj: Record<string, unknown>, 
  path: string, 
  defaultValue?: D
): T | D {
  try {
    // 指定更准确的类型
    const travel = (regexp: RegExp, o: Record<string, unknown>): unknown =>
      String.prototype.split
        .call(path, regexp)
        .filter(Boolean)
        .reduce((res, key) => {
          // 判断是否可继续访问
          if (res === null || res === undefined) return res;
          // 处理对象和数组的情况
          if (typeof res === 'object') {
            return (res as Record<string, unknown>)[key];
          }
          return undefined;
        }, o);
    
    const result = travel(/[,[\]]+?/g, obj) || travel(/[,[\].]+?/g, obj);
    
    return (result === undefined || result === null ? defaultValue : result) as T | D;
  } catch (error) {
    return defaultValue as D;
  }
}
