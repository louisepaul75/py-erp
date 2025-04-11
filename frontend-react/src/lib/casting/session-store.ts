import type { Session } from "@/types/casting/mold"

// Simulates a database for sessions
const sessions: Record<string, Session> = {}

// Creates a new session
export function createSession(session: Session): Session {
  sessions[session.id] = session
  saveSessionToLocalStorage(session)
  return session
}

// Updates an existing session
export function updateSession(sessionId: string, updates: Partial<Session>): Session | null {
  try {
    if (!sessions[sessionId]) {
      const loadedSession = loadSessionFromLocalStorage(sessionId)
      if (loadedSession) {
        sessions[sessionId] = loadedSession
      } else {
        return null
      }
    }

    sessions[sessionId] = {
      ...sessions[sessionId],
      ...updates,
      lastActive: Date.now(),
    }

    saveSessionToLocalStorage(sessions[sessionId])
    return sessions[sessionId]
  } catch (error) {
    console.error("Failed to update session:", error)
    return null
  }
}

// Gets a session by ID
export function getSession(sessionId: string): Session | null {
  if (sessions[sessionId]) {
    return sessions[sessionId]
  }

  // Try to load from localStorage if not in memory
  return loadSessionFromLocalStorage(sessionId)
}

// Gets all sessions for a user
export function getUserSessions(userId: string): Session[] {
  // First get sessions from memory
  const memorySessions = Object.values(sessions).filter((session) => session.userId === userId)

  // Then try to load any additional sessions from localStorage
  try {
    const keys = Object.keys(localStorage)
    const sessionKeys = keys.filter((key) => key.startsWith("casting_session_"))

    const allSessions: Session[] = [...memorySessions]
    const sessionIds = new Set(memorySessions.map((s) => s.id))

    sessionKeys.forEach((key) => {
      const sessionData = localStorage.getItem(key)
      if (sessionData) {
        try {
          const session = JSON.parse(sessionData) as Session
          if (session.userId === userId && !sessionIds.has(session.id)) {
            allSessions.push(session)
            sessions[session.id] = session // Add to memory cache
          }
        } catch (e) {
          console.error("Failed to parse session data:", e)
        }
      }
    })

    return allSessions
  } catch (error) {
    console.error("Failed to load sessions from localStorage:", error)
    return memorySessions
  }
}

// Deletes a session
export function deleteSession(sessionId: string): boolean {
  try {
    if (sessions[sessionId]) {
      delete sessions[sessionId]
    }

    removeSessionFromLocalStorage(sessionId)
    return true
  } catch (error) {
    console.error("Failed to delete session:", error)
    return false
  }
}

// Saves a session to localStorage
function saveSessionToLocalStorage(session: Session) {
  try {
    localStorage.setItem(`casting_session_${session.id}`, JSON.stringify(session))
  } catch (error) {
    console.error("Failed to save session to localStorage:", error)
  }
}

// Loads a session from localStorage
function loadSessionFromLocalStorage(sessionId: string): Session | null {
  try {
    const sessionData = localStorage.getItem(`casting_session_${sessionId}`)
    if (sessionData) {
      return JSON.parse(sessionData) as Session
    }
    return null
  } catch (error) {
    console.error("Failed to load session from localStorage:", error)
    return null
  }
}

// Removes a session from localStorage
function removeSessionFromLocalStorage(sessionId: string) {
  try {
    localStorage.removeItem(`casting_session_${sessionId}`)
  } catch (error) {
    console.error("Failed to remove session from localStorage:", error)
  }
}

// Loads all sessions from localStorage
export function loadSessionsFromLocalStorage() {
  try {
    const keys = Object.keys(localStorage)
    const sessionKeys = keys.filter((key) => key.startsWith("casting_session_"))

    sessionKeys.forEach((key) => {
      const sessionData = localStorage.getItem(key)
      if (sessionData) {
        try {
          const session = JSON.parse(sessionData) as Session
          sessions[session.id] = session
        } catch (e) {
          console.error("Failed to parse session data:", e)
        }
      }
    })
  } catch (error) {
    console.error("Failed to load sessions from localStorage:", error)
  }
}

// Initializes the session store
export function initSessionStore() {
  loadSessionsFromLocalStorage()
} 