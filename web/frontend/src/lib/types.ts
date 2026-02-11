export type Role = 'user' | 'assistant' | 'system'

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
  parameters?: Record<string, unknown>
  model?: string
  messages: Message[]
}

export interface VertexPromptExport {
  title?: string
  description?: string
  parameters?: Record<string, unknown>
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
  model?: string
  type?: string
}
