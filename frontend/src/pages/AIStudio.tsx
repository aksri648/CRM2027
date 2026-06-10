import { useState, useEffect, useRef, useMemo } from 'react'
import { Sparkles, Send, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useAuth } from '@clerk/clerk-react'
import { createApi } from '@/api/client'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface SegmentProposal {
  id: string
  name: string
  description: string
  customer_count: number
  filter_rules: any[]
}

interface MessageProposal {
  id: string
  channel: string
  message: string
}

interface CampaignProposal {
  id: string
  name: string
  segment: SegmentProposal
  channel: string
  message: string
}

type ProposalType = SegmentProposal | MessageProposal | CampaignProposal | null

const suggestions = [
  'Loyal Customers',
  'Inactive High-Value Customers',
  'Reactivation Prospects',
  'VIP Segment',
  'New Customers'
]

export default function AIStudio() {
  const { getToken } = useAuth()
  const api = useMemo(() => createApi(getToken), [getToken])

  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentProposal, setCurrentProposal] = useState<ProposalType>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (text?: string) => {
    const messageText = text || input
    if (!messageText.trim() || isLoading) return

    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: messageText,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setCurrentProposal(null)

    try {
      // Call the real AI API to generate a campaign proposal
      const response = await api.post('/ai/generate-proposal', {
        prompt: messageText
      })
      
      const { proposal, message } = response.data
      
      const assistantMessage: Message = {
        id: `assistant_${Date.now()}`,
        role: 'assistant',
        content: message || `I've analyzed your request and created a campaign proposal. Here are the details:`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, assistantMessage])

      // Show the campaign proposal from AI
      if (proposal) {
        setCurrentProposal(proposal)
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage: Message = {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error generating your proposal. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    handleSend(`Create a campaign for ${suggestion}`)
  }

  const handleLaunchCampaign = async () => {
    const proposal = currentProposal as CampaignProposal
    if (proposal) {
      try {
        await api.post('/campaigns', {
          name: proposal.name,
          channel: proposal.channel,
          message_template: proposal.message,
          status: 'draft'
        })
        alert('Campaign created successfully!')
        setCurrentProposal(null)
      } catch (error) {
        console.error('Failed to create campaign:', error)
        alert('Failed to create campaign. Please try again.')
      }
    }
  }

  const renderProposal = () => {
    if (!currentProposal) return null

    if ('segment' in currentProposal) {
      const proposal = currentProposal as CampaignProposal
      return (
        <Card className="mt-4 border-l-4 border-l-[#0fd4b4]">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-semibold text-gray-900">Campaign Summary</h4>
              <span className={`badge channel-${proposal.channel}`}>
                {proposal.channel}
              </span>
            </div>
            
            <div className="space-y-3">
              <div>
                <span className="text-xs text-gray-500 uppercase">Segment</span>
                <p className="text-sm font-medium">{proposal.segment.name} ({proposal.segment.customer_count} customers)</p>
              </div>
              
              <div>
                <span className="text-xs text-gray-500 uppercase">Message</span>
                <p className="text-sm text-gray-600 italic">"{proposal.message}"</p>
              </div>
            </div>

            <div className="flex items-center gap-2 mt-4">
              <Button 
                style={{ backgroundColor: 'var(--color-accent-teal)' }}
                className="text-white"
                onClick={handleLaunchCampaign}
              >
                <Check size={16} className="mr-1" />
                Launch Campaign
              </Button>
              <Button variant="outline">
                Edit
              </Button>
            </div>
          </CardContent>
        </Card>
      )
    }

    return null
  }

  return (
    <div className="flex flex-col h-[calc(100vh-64px)]">
      {/* Header */}
      <div className="p-6 border-b border-gray-100">
        <h1 className="text-2xl font-bold text-gray-900">AI Campaign Studio</h1>
        <p className="text-sm text-gray-500 mt-1">Describe your marketing goal and let AI build the campaign</p>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 ? (
          /* Empty State */
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-full bg-[#0fd4b4]/10 flex items-center justify-center mb-4 animate-pulse">
              <Sparkles size={32} className="text-[#0fd4b4]" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              What marketing goal would you like to achieve?
            </h2>
            <p className="text-gray-500 max-w-lg mb-6">
              Describe your objective and Xeno AI will generate a complete campaign strategy including audience, channels, messaging, and A/B tests.
            </p>
            
            {/* Suggestions */}
            <div className="flex flex-wrap justify-center gap-2 mb-8">
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full text-sm font-medium transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Messages */
          <div className="space-y-4">
            {messages.map((message) => (
              <div 
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div 
                  className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                    message.role === 'user' 
                      ? 'bg-[#0fd4b4] text-white rounded-br-md' 
                      : 'bg-gray-100 text-gray-900 rounded-bl-md'
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
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
            
            {renderProposal()}
            
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-6 border-t border-gray-100 bg-white">
        <div className="flex items-center gap-3 max-w-4xl mx-auto">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Describe your marketing goal..."
            className="flex-1"
            disabled={isLoading}
          />
          <Button 
            style={{ backgroundColor: 'var(--color-accent-teal)' }}
            className="text-white"
            onClick={() => handleSend()}
            disabled={isLoading || !input.trim()}
          >
            <Send size={18} />
          </Button>
        </div>
      </div>
    </div>
  )
}