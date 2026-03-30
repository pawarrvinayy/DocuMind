export interface Document {
  id: number
  filename: string
  created_at: string
}

export interface Source {
  page: number
  excerpt: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  streaming?: boolean
}
