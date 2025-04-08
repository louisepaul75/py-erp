"use client"

import { useState, useEffect, useCallback } from "react"

interface TimerOptions {
  maxPauses?: number
  initialTime?: number
  initialPauses?: number
  onPauseExhausted?: () => void
}

export function useTimer(options: TimerOptions = {}) {
  const { maxPauses = 3, initialTime = 0, initialPauses = 0, onPauseExhausted } = options

  const [elapsedTime, setElapsedTime] = useState(initialTime)
  const [isRunning, setIsRunning] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [pausesUsed, setPausesUsed] = useState(initialPauses)
  const [startTime, setStartTime] = useState<number | null>(null)
  const [pauseStartTime, setPauseStartTime] = useState<number | null>(null)

  // Start the timer
  const start = useCallback(() => {
    if (!isRunning) {
      setIsRunning(true)
      setIsPaused(false)
      setStartTime(Date.now() - elapsedTime)
    }
  }, [isRunning, elapsedTime])

  // Pause the timer
  const pause = useCallback(() => {
    if (isRunning && !isPaused) {
      if (pausesUsed >= maxPauses) {
        onPauseExhausted?.()
        return false
      }

      setIsPaused(true)
      setPauseStartTime(Date.now())
      setPausesUsed((prev) => prev + 1)
      return true
    }
    return false
  }, [isRunning, isPaused, pausesUsed, maxPauses, onPauseExhausted])

  // Resume the timer after pause
  const resume = useCallback(() => {
    if (isPaused) {
      setIsPaused(false)
      setPauseStartTime(null)
    }
  }, [isPaused])

  // Reset the timer to initial state
  const reset = useCallback(() => {
    setElapsedTime(0)
    setIsRunning(false)
    setIsPaused(false)
    setPausesUsed(0)
    setStartTime(null)
    setPauseStartTime(null)
  }, [])

  // Set the timer to a specific time
  const setTime = useCallback(
    (time: number) => {
      setElapsedTime(time)
      if (isRunning && !isPaused) {
        setStartTime(Date.now() - time)
      }
    },
    [isRunning, isPaused],
  )

  // Set the number of pauses used
  const setPauses = useCallback((pauses: number) => {
    setPausesUsed(pauses)
  }, [])

  // Update elapsed time when timer is running
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null

    if (isRunning && !isPaused) {
      interval = setInterval(() => {
        if (startTime) {
          setElapsedTime(Date.now() - startTime)
        }
      }, 10)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [isRunning, isPaused, startTime])

  // Format time for display
  const formatTime = (time: number = elapsedTime) => {
    const hours = Math.floor(time / 3600000)
    const minutes = Math.floor((time % 3600000) / 60000)
    const seconds = Math.floor((time % 60000) / 1000)
    const milliseconds = Math.floor((time % 1000) / 10)

    return {
      hours,
      minutes,
      seconds,
      milliseconds,
      formatted: `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`,
    }
  }

  return {
    elapsedTime,
    isRunning,
    isPaused,
    pausesUsed,
    remainingPauses: maxPauses - pausesUsed,
    start,
    pause,
    resume,
    reset,
    setTime,
    setPauses,
    formatTime,
  }
} 