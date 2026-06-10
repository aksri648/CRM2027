import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { ClerkProvider, SignedIn, SignedOut, useUser } from '@clerk/clerk-react'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Customers from './pages/Customers'
import Segments from './pages/Segments'
import Campaigns from './pages/Campaigns'
import CampaignDetail from './pages/CampaignDetail'
import AIStudio from './pages/AIStudio'
import Opportunities from './pages/Opportunities'
import AgentProposals from './pages/AgentProposals'
import ABTests from './pages/ABTests'
import Analytics from './pages/Analytics'
import PipelineMonitor from './pages/PipelineMonitor'
import Settings from './pages/Settings'
import Layout from './components/Layout'
import AICommandCentre from './components/AICommandCentre'

// Get Clerk publishable key from environment
const clerkPublishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY || 'pk_test_...'

function AppContent() {
  const [isAICommandCentreOpen, setIsAICommandCentreOpen] = useState(false)
  const { isSignedIn, user } = useUser()

  useEffect(() => {
    // Listen for AI Command Centre open event
    const handleOpenAICommandCentre = () => {
      setIsAICommandCentreOpen(true)
    }
    window.addEventListener('open-ai-command-centre', handleOpenAICommandCentre)
    return () => window.removeEventListener('open-ai-command-centre', handleOpenAICommandCentre)
  }, [])

  return (
    <Routes>
      <Route path="/login" element={
        <SignedIn>
          <Navigate to="/" replace />
        </SignedIn>
      } />
      
      <Route path="/" element={
        <SignedIn>
          <Layout />
        </SignedIn>
      }>
        <Route index element={<Dashboard />} />
        <Route path="customers" element={<Customers />} />
        <Route path="segments" element={<Segments />} />
        <Route path="campaigns" element={<Campaigns />} />
        <Route path="campaigns/:id" element={<CampaignDetail />} />
        <Route path="ai-studio" element={<AIStudio />} />
        <Route path="opportunities" element={<Opportunities />} />
        <Route path="proposals" element={<AgentProposals />} />
        <Route path="ab-tests" element={<ABTests />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="pipeline" element={<PipelineMonitor />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <ClerkProvider publishableKey={clerkPublishableKey}>
      <BrowserRouter>
        <SignedOut>
          <Login />
        </SignedOut>
        <SignedIn>
          <AppContent />
          <AICommandCentre 
            isOpen={false} 
            onClose={() => {}} 
          />
        </SignedIn>
      </BrowserRouter>
    </ClerkProvider>
  )
}

export default App