import type { Ref } from 'vue'

export interface WebSocketClient {
  isConnected: Ref<boolean>
  connect: () => Promise<void>
  disconnect: () => void
  send: (message: any) => Promise<void>
  onMessage: (callback: (event: MessageEvent) => void) => void
  onError: (callback: (event: Event) => void) => void
  onClose: (callback: () => void) => void
}
