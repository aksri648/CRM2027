import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
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

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [isAICommandCentreOpen, setIsAICommandCentreOpen] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    setIsAuthenticated(!!token)
    setLoading(false)

    // Listen for AI Command Centre open event
    const handleOpenAICommandCentre = () => {
      setIsAICommandCentreOpen(true)
    }
    window.addEventListener('open-ai-command-centre', handleOpenAICommandCentre)
    return () => window.removeEventListener('open-ai-command-centre', handleOpenAICommandCentre)
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={
          isAuthenticated ? <Navigate to="/" replace /> : <Login setAuth={setIsAuthenticated} />
        } />
        
        <Route path="/" element={
          isAuthenticated ? <Layout /> : <Navigate to="/login" replace />
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

      {/* AI Command Centre Modal */}
      {isAuthenticated && (
        <AICommandCentre 
          isOpen={isAICommandCentreOpen} 
          onClose={() => setIsAICommandCentreOpen(false)} 
        />
      )}
    </BrowserRouter>
  )
}

export default App