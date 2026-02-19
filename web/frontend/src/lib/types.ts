export type Role = 'user' | 'model'

export interface Message {
  id: string
  role: Role
  content: string
  createdAt: string
}

export interface Chat {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  systemInstruction?: string
  messages: Message[]
}

export interface VertexPromptExport {
  title?: string
  description?: string
  systemInstruction?: {
    parts?: Array<{
      text?: string
    }>
  }
  messages?: Array<{
    author?: string
    content?: {
      role?: string
      parts?: Array<{
        text?: string
        thought?: boolean
      }>
    }
  }>
  type?: string
}
