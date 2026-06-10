import { useState } from 'react'
import { Send, Bot, Sparkles } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import api from '../api/client'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function AIAssistant() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hi! I\'m your AI assistant for Xeno CRM. I can help you with:\n\n• Creating customer segments\n• Writing campaign messages\n• Analyzing campaign performance\n• Recommending the best channels\n\nWhat would you like help with today?'
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!input.trim()) return
    
    const userMessage = { role: 'user' as const, content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await api.post('/ai/chat', {
        message: input,
        context: {}
      })
      setMessages(prev => [...prev, { role: 'assistant', content: response.data.response }])
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }])
    } finally {
      setLoading(false)
    }
  }

  const quickActions = [
    { label: 'Suggest a segment for re-engagement', prompt: 'Create a segment for customers who haven\'t purchased in 60 days' },
    { label: 'Write a welcome message', prompt: 'Write a welcome message for new customers' },
    { label: 'Analyze recent campaigns', prompt: 'Analyze the performance of my recent campaigns' },
    { label: 'Best channel for high-value customers', prompt: 'What\'s the best channel to reach high-value customers?' },
  ]

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Sparkles className="text-primary" />
          AI Assistant
        </h1>
        <p className="text-gray-600 dark:text-gray-400">Get intelligent help for your marketing campaigns</p>
      </div>

      {/* Quick Actions */}
      <div className="mb-4 flex flex-wrap gap-2">
        {quickActions.map((action) => (
          <Button
            key={action.label}
            variant="outline"
            size="sm"
            onClick={() => setInput(action.prompt)}
          >
            {action.label}
          </Button>
        ))}
      </div>

      {/* Chat Messages */}
      <Card className="flex-1 flex flex-col">
        <CardContent className="flex-1 p-4 overflow-y-auto">
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div key={index} className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : ''}`}>
                {message.role === 'assistant' && (
                  <div className="p-2 bg-primary/10 rounded-full h-fit">
                    <Bot className="text-primary" size={20} />
                  </div>
                )}
                <div className={`max-w-[70%] px-4 py-3 rounded-xl ${
                  message.role === 'user' 
                    ? 'bg-primary text-primary-foreground' 
                    : 'bg-muted text-foreground'
                }`}>
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-3">
                <div className="p-2 bg-primary/10 rounded-full">
                  <Bot className="text-primary" size={20} />
                </div>
                <div className="bg-muted px-4 py-3 rounded-xl">
                  <p className="text-muted-foreground">Thinking...</p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
        
        {/* Input */}
        <div className="p-4 border-t">
          <div className="flex gap-2">
            <Input
              placeholder="Ask me anything about your CRM..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              disabled={loading}
            />
            <Button onClick={handleSend} disabled={loading || !input.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}