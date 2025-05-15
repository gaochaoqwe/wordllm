import SockJS from 'sockjs-client'
import { Client } from '@stomp/stompjs'
import { ref } from 'vue'

export class WebSocketService {
  private static instance: WebSocketService
  private client: Client | null = null
  private subscriptions: Map<string, { subscription: any; callback: (message: any) => void }> = new Map()
  
  isConnected = ref(false)

  private constructor() {
    this.initializeWebSocket()
  }

  static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService()
    }
    return WebSocketService.instance
  }

  private initializeWebSocket() {
    const url = import.meta.env.VITE_WS_URL || 'http://localhost:3001/api/ws'
    const wsUrl = new URL('/ws', url).toString()
    
    this.client = new Client({
      webSocketFactory: () => new SockJS(wsUrl),
      debug: (str) => {
        console.log('WebSocket Debug:', str)
      },
      reconnectDelay: 5000,
      heartbeatIncoming: 4000,
      heartbeatOutgoing: 4000,
      onConnect: () => {
        this.isConnected.value = true
        console.log('WebSocket Connected')
        // 重新订阅之前的主题
        this.subscriptions.forEach(({ callback }, topic) => {
          this.resubscribe(topic, callback)
        })
      },
      onDisconnect: () => {
        this.isConnected.value = false
        console.log('WebSocket Disconnected')
      },
      onStompError: (frame) => {
        console.error('WebSocket Error:', frame)
      }
    })

    this.client.activate()
  }

  private resubscribe(topic: string, callback: (message: any) => void) {
    if (!this.client || !this.client.connected) return

    try {
      const subscription = this.client.subscribe(topic, (message) => {
        try {
          const payload = JSON.parse(message.body)
          callback(payload)
        } catch (error) {
          console.error('Failed to parse message:', error)
        }
      })

      this.subscriptions.set(topic, { subscription, callback })
    } catch (error) {
      console.error('Failed to resubscribe:', error)
    }
  }

  subscribe(topic: string, callback: (message: any) => void): void {
    if (!this.client) {
      console.error('WebSocket client not initialized')
      return
    }

    // 如果已经订阅，先取消订阅
    this.unsubscribe(topic)

    if (this.client.connected) {
      this.resubscribe(topic, callback)
    } else {
      // 保存回调，等连接成功后重新订阅
      this.subscriptions.set(topic, { subscription: null, callback })
    }
  }

  unsubscribe(topic: string): void {
    const sub = this.subscriptions.get(topic)
    if (sub?.subscription) {
      sub.subscription.unsubscribe()
    }
    this.subscriptions.delete(topic)
  }

  send(destination: string, body: any): void {
    if (!this.client || !this.client.connected) {
      console.error('WebSocket not connected')
      return
    }

    try {
      this.client.publish({
        destination,
        body: JSON.stringify(body)
      })
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  disconnect(): void {
    if (this.client) {
      this.subscriptions.clear()
      this.client.deactivate()
    }
  }
}
