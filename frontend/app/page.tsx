/**
 * Home page - redirects directly to chat
 * No landing page, straight to the chat interface
 */

import { redirect } from 'next/navigation'

export default function Home() {
  redirect('/chat')
}