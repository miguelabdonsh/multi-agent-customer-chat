/**
 * TypeScript types for Multi-Agent Customer Chat
 * Minimal but complete type definitions
 */

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

export interface ChatMessage {
  id: string
  session_id: string
  sender: string
  content: string
  message_type: string
  created_at: string
  metadata: Record<string, any>
}

export interface WebSocketMessage {
  type: string
  data: Record<string, any>
  session_id?: string
}

export interface Session {
  id: string
  user_id: string
  status: string
  created_at: string
  metadata: Record<string, any>
}

export interface SessionCreate {
  user_id: string
  metadata?: Record<string, any>
} 