import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api',  // 添加 /api 前缀
  timeout: 15000,
  withCredentials: true
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const requestInfo = {
      method: config.method,
      url: config.url,
      baseURL: config.baseURL,
      params: config.params,
      data: config.data,
      headers: config.headers,
      timeout: config.timeout
    }
    console.log('请求详情:', requestInfo)
    return config
  },
  (error) => {
    console.error('请求配置错误:', {
      message: error.message,
      config: error.config
    })
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    console.log('响应成功:', {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
      data: response.data,
      config: {
        url: response.config.url,
        method: response.config.method,
        params: response.config.params
      }
    })

    // 如果是下载文件，直接返回响应
    if (response.config.responseType === 'blob') {
      return response
    }

    // 直接返回响应数据
    return response.data
  },
  (error) => {
    console.error('响应错误:', {
      message: error.message,
      response: {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      },
      request: {
        url: error.config?.url,
        method: error.config?.method,
        params: error.config?.params
      }
    })

    // 处理错误响应
    const message = error.response?.data?.message || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
