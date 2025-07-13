/**
 * TypeScript types for Multi-Agent Customer Chat
 * Enhanced type definitions with improved structure
 */

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

export type MessageType = 'text' | 'system' | 'error' | 'typing' | 'image' | 'file'

export type SenderType = 'user' | 'bot' | 'agent' | 'system'

export interface ChatMessage {
  id: string
  session_id: string
  sender: SenderType
  content: string
  message_type: MessageType
  created_at: string
  metadata: {
    agent_id?: string
    agent_name?: string
    confidence?: number
    response_time?: number
    [key: string]: any
  }
}

export interface WebSocketMessage {
  type: 'message' | 'typing' | 'status' | 'error' | 'system' | 'chat'
  data: {
    message?: ChatMessage
    session_id?: string
    status?: ConnectionStatus
    error?: string
    content?: string
    metadata?: any
    [key: string]: any
  }
  session_id?: string
  timestamp?: string
}

export interface Session {
  id: string
  user_id: string
  status: 'active' | 'inactive' | 'ended'
  created_at: string
  updated_at?: string
  metadata: {
    user_agent?: string
    ip_address?: string
    initial_message?: string
    [key: string]: any
  }
}

export interface SessionCreate {
  user_id: string
  metadata?: {
    user_agent?: string
    initial_message?: string
    [key: string]: any
  }
}

export interface TypingIndicator {
  session_id: string
  sender: SenderType
  is_typing: boolean
  timestamp: string
}

export interface AgentInfo {
  id: string
  name: string
  type: 'primary' | 'specialist' | 'escalation'
  capabilities: string[]
  status: 'active' | 'busy' | 'offline'
}