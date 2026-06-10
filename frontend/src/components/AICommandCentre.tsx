import { useState, useEffect, useRef, useMemo } from 'react'
import { X, Send, Bot, Cpu, HardDrive, Activity } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuth } from '@clerk/clerk-react'
import { createApi } from '@/api/client'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

type SystemStatus = {
  worker_status: string
  queue_depth: number
  active_runs: number
} | null

interface AICommandCentreProps {
  isOpen: boolean
  onClose: () => void
}

export default function AICommandCentre({ isOpen, onClose }: AICommandCentreProps) {
  const { getToken } = useAuth()
  const api = useMemo(() => createApi(getToken), [getToken])

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Hello, I am the Xeno AI Command Centre. I can help you monitor system activity, generate campaigns, discover opportunities, or answer questions about your CRM. How can I assist you?",
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    worker_status: 'Healthy',
    queue_depth: 12,
    active_runs: 3
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isOpen) {
      loadSystemStatus()
      const interval = setInterval(loadSystemStatus, 10000)
      return () => clearInterval(interval)
    }
  }, [isOpen])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadSystemStatus = async () => {
    try {
      const response = await api.get('/agent/system-status')
      setSystemStatus(response.data)
    } catch (error) {
      console.error('Failed to load system status:', error)
      setSystemStatus(null)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Simulate AI response for demo
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      let responseContent = "I'm here to help! You can ask me about:\n\n"
      responseContent += "• System status and health\n"
      responseContent += "• Campaign performance\n"
      responseContent += "• Customer insights\n"
      responseContent += "• Creating new campaigns\n"
      responseContent += "• Discovering opportunities\n\n"
      responseContent += "What would you like to know?"

      const assistantMessage: Message = {
        id: `assistant_${Date.now()}`,
        role: 'assistant',
        content: responseContent,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative w-[680px] max-h-[80vh] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'var(--color-accent-teal)' }}>
              <Bot size={24} className="text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">AI Command Centre</h3>
              <p className="text-xs text-gray-500">System overview & assistant</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* System Status Bar */}
        <div className="flex items-center gap-4 p-4 bg-gray-50 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <Cpu size={16} className="text-gray-400" />
            <span className="text-sm text-gray-600">WORKER:</span>
            <span className="text-sm font-semibold text-green-600">{systemStatus?.worker_status}</span>
          </div>
          <div className="flex items-center gap-2">
            <HardDrive size={16} className="text-gray-400" />
            <span className="text-sm text-gray-600">QUEUE:</span>
            <span className="text-sm font-semibold text-gray-900">{systemStatus?.queue_depth}</span>
          </div>
          <div className="flex items-center gap-2">
            <Activity size={16} className="text-gray-400" />
            <span className="text-sm text-gray-600">ACTIVE RUNS:</span>
            <span className="text-sm font-semibold text-gray-900">{systemStatus?.active_runs}</span>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div 
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                  message.role === 'user' 
                    ? 'bg-[#0fd4b4] text-white rounded-br-md' 
                    : 'bg-gray-100 text-gray-900 rounded-bl-md'
                }`}
              >
                <p className="text-sm whitespace-pre-line">{message.content}</p>
                <div className={`text-xs mt-1 ${
                  message.role === 'user' ? 'text-white/70' : 'text-gray-400'
                }`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-100">
          <div className="flex items-center gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about system status, campaigns, or customers..."
              className="flex-1"
              disabled={isLoading}
            />
            <Button 
              style={{ backgroundColor: 'var(--color-accent-teal)' }}
              className="text-white"
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
            >
              <Send size={18} />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}