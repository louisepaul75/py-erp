"use client"

import type { ReactNode } from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { WebSocketProvider } from "@/components/goods-movement/websocket-provider"
import { HistoryProvider } from "@/components/goods-movement/history-context"
import { TimerProvider } from "@/components/timer/timer-context"
import { GlobalTimer } from "@/components/timer/global-timer"
import { PauseOverlay } from "@/components/timer/pause-overlay"
import { Toaster } from "@/components/ui/toaster"

// Create a client
const queryClient = new QueryClient()

interface ProvidersProps {
  children: ReactNode
}

export function Providers({ children }: ProvidersProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <WebSocketProvider>
        <HistoryProvider>
          <TimerProvider>
            {children}
            <GlobalTimer />
            <PauseOverlay />
            <Toaster />
          </TimerProvider>
        </HistoryProvider>
      </WebSocketProvider>
    </QueryClientProvider>
  )
}

