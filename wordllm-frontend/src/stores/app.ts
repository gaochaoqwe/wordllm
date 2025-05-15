import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 全局加载状态
  const loading = ref(false)
  
  // 用户信息
  const userInfo = ref<{
    id: number
    username: string
    token: string
  } | null>(null)

  // 设置加载状态
  function setLoading(status: boolean) {
    loading.value = status
  }

  // 设置用户信息
  function setUserInfo(info: typeof userInfo.value) {
    userInfo.value = info
  }

  // 清除用户信息
  function clearUserInfo() {
    userInfo.value = null
  }

  return {
    loading,
    userInfo,
    setLoading,
    setUserInfo,
    clearUserInfo
  }
}) 