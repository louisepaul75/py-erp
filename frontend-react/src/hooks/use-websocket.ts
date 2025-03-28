"use client"

import { useContext, useEffect } from "react"
import { WebSocketContext } from "@/components/goods-movement/websocket-provider"

// Custom event name for simulating WebSocket messages
const WS_MESSAGE_EVENT = "mock-ws-message"

interface UseWebSocketOptions {
  onMessage?: (data: any) => void
}

export function useWebSocket({ onMessage }: UseWebSocketOptions = {}) {
  const { isConnected, sendMessage } = useContext(WebSocketContext)

  useEffect(() => {
    if (isConnected && onMessage) {
      // Set up message listener for our custom event
      const handleMockMessage = (event: CustomEvent) => {
        try {
          const data = event.detail
          onMessage(data)
        } catch (error) {
          console.error("Error handling mock WebSocket message:", error)
        }
      }

      // Add event listener for our custom event
      window.addEventListener(WS_MESSAGE_EVENT as any, handleMockMessage as EventListener)

      return () => {
        window.removeEventListener(WS_MESSAGE_EVENT as any, handleMockMessage as EventListener)
      }
    }
  }, [isConnected, onMessage])

  return {
    isConnected,
    sendMessage,
  }
}

