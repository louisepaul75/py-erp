"use client"

import { createContext, useEffect, useState, type ReactNode } from "react"

interface WebSocketMessage {
  type: string
  [key: string]: any
}

interface WebSocketContextType {
  isConnected: boolean
  sendMessage: (message: WebSocketMessage) => void
}

export const WebSocketContext = createContext<WebSocketContextType>({
  isConnected: false,
  sendMessage: () => {},
})

interface WebSocketProviderProps {
  children: ReactNode
}

// Custom event for simulating WebSocket messages
const WS_MESSAGE_EVENT = "mock-ws-message"

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    // Instead of connecting to a real WebSocket server, we'll simulate the connection
    const connectMockWebSocket = () => {
      console.log("Mock WebSocket connecting...")

      // Simulate connection delay
      setTimeout(() => {
        setIsConnected(true)
        console.log("Mock WebSocket connected")
      }, 500)
    }

    connectMockWebSocket()

    // Create a custom event listener for our mock WebSocket messages
    const handleMockMessage = (event: CustomEvent) => {
      const { detail } = event
      // Handle the mock WebSocket message
      console.log("Mock WebSocket message received:", detail)
    }

    // Add event listener for our custom event
    window.addEventListener(WS_MESSAGE_EVENT as any, handleMockMessage as EventListener)

    return () => {
      // Clean up
      setIsConnected(false)
      window.removeEventListener(WS_MESSAGE_EVENT as any, handleMockMessage as EventListener)
      console.log("Mock WebSocket disconnected")
    }
  }, [])

  const sendMessage = (message: WebSocketMessage) => {
    if (isConnected) {
      console.log("Mock WebSocket sending message:", message)

      // Simulate server processing delay
      setTimeout(() => {
        // Dispatch a custom event to simulate receiving a message
        const mockResponse = {
          type: "RESPONSE",
          originalMessage: message,
          timestamp: new Date().toISOString(),
        }

        const mockEvent = new CustomEvent(WS_MESSAGE_EVENT, {
          detail: mockResponse,
        })

        window.dispatchEvent(mockEvent)
      }, 300)
    }
  }

  return <WebSocketContext.Provider value={{ isConnected, sendMessage }}>{children}</WebSocketContext.Provider>
}

