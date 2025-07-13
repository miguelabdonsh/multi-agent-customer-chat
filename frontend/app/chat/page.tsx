/**
 * Chat page for real-time messaging
 * Modern, professional design with enhanced UX
 */

'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Send, Bot, Wifi, WifiOff, Sparkles, MessageCircle, User, Clock } from 'lucide-react'
import { useChat } from '../hooks/useChat'
import { ChatMessage, ConnectionStatus } from '../types'

export default function ChatPage() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [isTyping, setIsTyping] = useState(false)
  const [messageCount, setMessageCount] = useState(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const { messages, connectionStatus, sendMessage, createSession, reconnect } = useChat(sessionId)
  
  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  
  // Track message count
  useEffect(() => {
    setMessageCount(messages.length)
  }, [messages])
  
  // Create session on mount
  useEffect(() => {
    const userId = 'user-' + Date.now()
    createSession(userId)
      .then(setSessionId)
      .catch(console.error)
  }, [createSession])
  
  // Enhanced typing indicator
  useEffect(() => {
    const lastMessage = messages[messages.length - 1]
    if (lastMessage && lastMessage.sender === 'user') {
      setIsTyping(true)
      const timer = setTimeout(() => setIsTyping(false), 1200 + Math.random() * 800)
      return () => clearTimeout(timer)
    }
  }, [messages])
  
  const handleReconnect = () => {
    reconnect()
  }
  
  const getConnectionStatusConfig = (status: ConnectionStatus) => {
    switch (status) {
      case 'connected':
        return {
          color: 'bg-green-500',
          text: 'Conectado',
          icon: <Wifi className="w-4 h-4" />
        }
      case 'connecting':
        return {
          color: 'bg-yellow-500',
          text: 'Conectando...',
          icon: <Wifi className="w-4 h-4 animate-pulse" />
        }
      case 'disconnected':
        return {
          color: 'bg-red-500',
          text: 'Desconectado',
          icon: <WifiOff className="w-4 h-4" />
        }
      default:
        return {
          color: 'bg-gray-500',
          text: 'Estado desconocido',
          icon: <WifiOff className="w-4 h-4" />
        }
    }
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('es-ES', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const statusConfig = getConnectionStatusConfig(connectionStatus)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl h-[90vh] flex flex-col rounded-2xl shadow-2xl overflow-hidden border border-blue-100 bg-white">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 shadow-lg rounded-t-2xl flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm border border-white/30">
                  <Bot className="w-8 h-8 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white animate-pulse"></div>
              </div>
              <div>
                <h1 className="text-2xl font-bold">
                  Asistente Virtual
                </h1>
                <p className="text-blue-100 text-sm flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Soporte inteligente 24/7
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="flex items-center gap-2 bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full border border-white/30">
                  <div className={`w-2 h-2 rounded-full ${statusConfig.color}`}></div>
                  {statusConfig.icon}
                  <span className="text-sm font-medium">{statusConfig.text}</span>
                </div>
                <div className="text-xs text-blue-100 mt-1">
                  {messageCount} mensajes
                </div>
              </div>
              
              {(connectionStatus === 'disconnected' || connectionStatus === 'error') && (
                <button
                  onClick={handleReconnect}
                  className="px-4 py-2 bg-white/20 text-white rounded-xl hover:bg-white/30 transition-all duration-200 backdrop-blur-sm border border-white/30"
                >
                  Reconectar
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto bg-gray-50 p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="p-8 bg-white/80 backdrop-blur-sm rounded-3xl border border-gray-200 shadow-lg">
                <MessageCircle className="w-16 h-16 text-blue-500 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                  ¡Bienvenido al chat!
                </h3>
                <p className="text-gray-600 mb-4">
                  Inicia una conversación con nuestro asistente virtual
                </p>
                <div className="text-sm text-gray-500">
                  Escribe tu mensaje abajo para comenzar
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <div
                  key={message.id || index}
                  className={`flex items-start gap-3 animate-fadeIn ${
                    message.sender === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.sender === 'bot' && (
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  )}
                  
                  <div className={`max-w-[70%] group ${message.sender === 'user' ? 'order-1' : ''}`}>
                    <div
                      className={`p-4 rounded-2xl shadow-sm border ${
                        message.sender === 'user'
                          ? 'bg-blue-500 text-white border-blue-500'
                          : 'bg-white text-gray-800 border-gray-200'
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>
                    </div>
                    
                    <div className={`flex items-center gap-2 mt-1 px-2 ${
                      message.sender === 'user' ? 'justify-end' : 'justify-start'
                    }`}>
                      <Clock className="w-3 h-3 text-gray-400" />
                      <span className="text-xs text-gray-500">
                        {formatTime(message.created_at)}
                      </span>
                      {message.metadata?.agent_name && (
                        <span className="text-xs text-blue-500 font-medium">
                          • {message.metadata.agent_name}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {message.sender === 'user' && (
                    <div className="w-8 h-8 bg-gray-500 rounded-full flex items-center justify-center flex-shrink-0">
                      <User className="w-5 h-5 text-white" />
                    </div>
                  )}
                </div>
              ))}
              
              {/* Typing Indicator */}
              {isTyping && (
                <div className="flex items-start gap-3 animate-fadeIn">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-200">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      <span className="text-sm text-gray-500 ml-2">Escribiendo...</span>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 bg-white p-4 flex-shrink-0">
          <div className="flex items-center gap-3 bg-gray-50 rounded-xl p-3 border border-gray-200 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20 transition-all">
            <MessageCircle className="w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Escribe tu mensaje aquí..."
              className="flex-1 bg-transparent text-gray-700 placeholder-gray-500 focus:outline-none"
              disabled={connectionStatus !== 'connected'}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  const target = e.target as HTMLInputElement
                  if (target.value.trim()) {
                    sendMessage(target.value)
                    target.value = ''
                  }
                }
              }}
            />
            <button
              onClick={(e) => {
                const input = e.currentTarget.previousElementSibling as HTMLInputElement
                if (input && input.value.trim()) {
                  sendMessage(input.value)
                  input.value = ''
                }
              }}
              disabled={connectionStatus !== 'connected'}
              className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
            <span>Presiona Enter para enviar</span>
            <span>Powered by AI Assistant</span>
          </div>
        </div>
      </div>
    </div>
  )
}