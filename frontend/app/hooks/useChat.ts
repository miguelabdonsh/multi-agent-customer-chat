/**
 * Chat hook for WebSocket connection and message management
 * Minimal implementation with reconnection and state management
 */

'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { ChatMessage, ConnectionStatus, WebSocketMessage, Session, SessionCreate } from '../types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

export function useChat(sessionId: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected')
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttempts = useRef(0)
  
  // Create session via REST API
  const createSession = useCallback(async (userId: string): Promise<string> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId, metadata: {} }),
      })
      
      if (!response.ok) {
        throw new Error('Failed to create session')
      }
      
      const session: Session = await response.json()
      return session.id
    } catch (error) {
      console.error('Error creating session:', error)
      throw error
    }
  }, [])
  
  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    if (!sessionId || connectionStatus === 'connecting') return
    
    setConnectionStatus('connecting')
    
    const ws = new WebSocket(`${WS_BASE_URL}/ws/${sessionId}`)
    wsRef.current = ws
    
    ws.onopen = () => {
      setConnectionStatus('connected')
      reconnectAttempts.current = 0
      console.log('WebSocket connected')
    }
    
    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data)
        
        switch (message.type) {
          case 'chat':
            const chatMessage: ChatMessage = message.data as ChatMessage
            setMessages(prev => [...prev, chatMessage])
            break
          case 'history':
            const historyMessages: ChatMessage[] = message.data.messages || []
            setMessages(historyMessages)
            break
          case 'system':
            console.log('System message:', message.data)
            break
          case 'error':
            console.error('WebSocket error:', message.data)
            break
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }
    
    ws.onclose = () => {
      setConnectionStatus('disconnected')
      console.log('WebSocket disconnected')
      
      // Attempt reconnection
      if (reconnectAttempts.current < 5) {
        reconnectAttempts.current++
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log(`Reconnecting... (attempt ${reconnectAttempts.current})`)
          connectWebSocket()
        }, 2000 * reconnectAttempts.current)
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setConnectionStatus('error')
    }
  }, [sessionId, connectionStatus])
  
  // Send message via WebSocket
  const sendMessage = useCallback((content: string) => {
    if (!wsRef.current || connectionStatus !== 'connected') return
    
    const message: WebSocketMessage = {
      type: 'chat',
      data: { content, metadata: {} },
      session_id: sessionId || undefined,
    }
    
    wsRef.current.send(JSON.stringify(message))
  }, [connectionStatus, sessionId])
  
  // Connect when sessionId is available
  useEffect(() => {
    if (sessionId) {
      connectWebSocket()
    }
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [sessionId, connectWebSocket])
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [])
  
  return {
    messages,
    connectionStatus,
    sendMessage,
    createSession,
  }
} 