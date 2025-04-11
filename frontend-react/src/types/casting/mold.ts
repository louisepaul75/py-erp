export interface Article {
  id: string
  number: string
  name: string
  imageUrl: string
}

export interface Mold {
  id: string
  number: string
  articles: Article[]
  castCount: number
  selectedArticleId?: string
}

export interface Session {
  id: string
  userId: string
  userName: string
  workplace: string
  molds: Mold[]
  startTime: number
  pauseCount: number
  maxPauses: number
  isPaused: boolean
  elapsedTime: number
  centrifugeMachines: number
  lastActive: number
}

export interface User {
  id: string
  name: string
} 