import { ref, onUnmounted } from 'vue'
import type { Ref } from 'vue'
import type { WebSocketClient } from '@/types/websocket'

interface WebSocketOptions {
  url?: string
}

export function useWebSocket(options: WebSocketOptions = {}): WebSocketClient {
  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 3
  const reconnectTimeout = 1000
  let messageHandler: ((event: MessageEvent) => void) | null = null
  let errorHandler: ((event: Event) => void) | null = null
  let closeHandler: (() => void) | null = null

  const connect = async () => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const baseUrl = `${protocol}//${window.location.host}`
      const wsUrl = options.url ? `${baseUrl}${options.url}` : `${baseUrl}/ws`
      
      ws.value = new WebSocket(wsUrl)

      ws.value.onopen = () => {
        console.log('WebSocket connected')
        isConnected.value = true
        reconnectAttempts.value = 0
      }

      ws.value.onmessage = (event) => {
        messageHandler?.(event)
      }

      ws.value.onerror = (event) => {
        console.error('WebSocket error:', event)
        errorHandler?.(event)
      }

      ws.value.onclose = () => {
        console.log('WebSocket closed')
        isConnected.value = false
        closeHandler?.()

        // 尝试重连
        if (reconnectAttempts.value < maxReconnectAttempts) {
          reconnectAttempts.value++
          setTimeout(() => {
            console.log(`Attempting to reconnect (${reconnectAttempts.value}/${maxReconnectAttempts})...`)
            connect()
          }, reconnectTimeout * reconnectAttempts.value)
        }
      }

    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      errorHandler?.(new Event('error'))
    }
  }

  const disconnect = () => {
    if (ws.value && isConnected.value) {
      ws.value.close()
      isConnected.value = false
    }
  }

  const sendMessage = (message: string | object) => {
    if (!ws.value || !isConnected.value) {
      console.error('WebSocket is not connected')
      return
    }

    try {
      const data = typeof message === 'string' ? message : JSON.stringify(message)
      ws.value.send(data)
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  const onMessage = (callback: (event: MessageEvent) => void) => {
    messageHandler = callback
  }

  const onError = (callback: (event: Event) => void) => {
    errorHandler = callback
  }

  const onClose = (callback: () => void) => {
    closeHandler = callback
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    connect,
    disconnect,
    sendMessage,
    onMessage,
    onError,
    onClose
  }
}
