/**
 * Chat page for real-time messaging
 * Minimal implementation with WebSocket connection
 */

'use client'

import { useState, useEffect, useRef } from 'react'
import { useChat } from '../hooks/useChat'
import { ChatMessage, ConnectionStatus } from '../types'

export default function ChatPage() {
  const [message, setMessage] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const { messages, connectionStatus, sendMessage, createSession, reconnect } = useChat(sessionId)
  
  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  
  // Create session on mount
  useEffect(() => {
    createSession('user-' + Date.now())
      .then(setSessionId)
      .catch(console.error)
  }, [createSession])
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && sessionId) {
      sendMessage(message)
      setMessage('')
    }
  }
  
  const handleReconnect = () => {
    if (reconnect) {
      reconnect()
    }
  }
  
  const getConnectionStatusColor = (status: ConnectionStatus): string => {
    switch (status) {
      case 'connected': return 'bg-green-500'
      case 'connecting': return 'bg-yellow-500'
      case 'disconnected': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }
  
  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm p-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold">Customer Chat</h1>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${getConnectionStatusColor(connectionStatus)}`}></div>
            <span className="text-sm text-gray-600 capitalize">{connectionStatus}</span>
          </div>
          {(connectionStatus === 'disconnected' || connectionStatus === 'error') && (
            <button
              onClick={handleReconnect}
              className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors"
            >
              Reconnect
            </button>
          )}
        </div>
      </div>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {connectionStatus === 'connecting' && (
          <div className="text-center text-gray-500 py-4">
            Connecting to chat...
          </div>
        )}
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                msg.sender === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-800'
              }`}
            >
              <p className="text-sm">{msg.content}</p>
              <p className="text-xs opacity-75 mt-1">
                {new Date(msg.created_at).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input */}
      <form onSubmit={handleSubmit} className="bg-white p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder={connectionStatus === 'connected' ? "Type your message..." : "Connecting..."}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={connectionStatus !== 'connected'}
          />
          <button
            type="submit"
            disabled={connectionStatus !== 'connected' || !message.trim()}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  )
} 