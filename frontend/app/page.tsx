/**
 * Home page for Multi-Agent Customer Chat
 * Simple landing page with chat navigation
 */

import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md mx-auto text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Multi-Agent Customer Chat
        </h1>
        <p className="text-gray-600 mb-8">
          Real-time customer support with AI agents
        </p>
        <Link 
          href="/chat"
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Start Chat
        </Link>
      </div>
    </div>
  )
} 