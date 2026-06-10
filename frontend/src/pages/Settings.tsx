import { useState, useEffect } from 'react'
import { Globe, Bell, Bot, Send } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import api from '@/api/client'

interface AppSettings {
  platform_name: string
  timezone: string
  currency: string
  ai_model: string
  scan_schedule: string
  auto_approve: boolean
  telegram_token: string | null
  telegram_chat_id: string | null
  notif_telegram: boolean
  notif_campaign_complete: boolean
  notif_opportunities: boolean
  notif_weekly_digest: boolean
}

export default function Settings() {
  const [settings, setSettings] = useState<AppSettings>({
    platform_name: 'Xeno AI Campaign Studio',
    timezone: 'Asia/Kolkata',
    currency: 'INR',
    ai_model: 'GPT-5',
    scan_schedule: 'Daily at 6:00 AM',
    auto_approve: false,
    telegram_token: null,
    telegram_chat_id: null,
    notif_telegram: true,
    notif_campaign_complete: true,
    notif_opportunities: true,
    notif_weekly_digest: false
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const response = await api.get('/settings')
      setSettings(response.data)
    } catch (error) {
      console.error('Failed to load settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await api.put('/settings', settings)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (error) {
      console.error('Failed to save settings:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleTestTelegram = async () => {
    try {
      await api.post('/settings/test-telegram')
      alert('Test message sent successfully!')
    } catch (error) {
      console.error('Failed to test Telegram:', error)
      alert('Failed to send test message')
    }
  }

  const Toggle = ({ checked, onChange }: { checked: boolean; onChange: (checked: boolean) => void }) => (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
        checked ? 'bg-[#0fd4b4]' : 'bg-gray-200'
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          checked ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  )

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-500">Loading settings...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-3xl">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-sm text-gray-500 mt-1">Configure your platform preferences</p>
      </div>

      <div className="space-y-6">
        {/* General Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe size={18} />
              General
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="platform_name">Platform Name</Label>
              <Input
                id="platform_name"
                value={settings.platform_name}
                onChange={(e) => setSettings({ ...settings, platform_name: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="timezone">Default Timezone</Label>
                <select
                  id="timezone"
                  value={settings.timezone}
                  onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                  className="w-full h-10 px-3 border border-gray-200 rounded-lg text-sm"
                >
                  <option value="Asia/Kolkata">Asia/Kolkata (IST, UTC +5:30)</option>
                  <option value="UTC">UTC</option>
                  <option value="America/New_York">America/New_York (EST, UTC -5)</option>
                  <option value="Europe/London">Europe/London (GMT, UTC +0)</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="currency">Default Currency</Label>
                <select
                  id="currency"
                  value={settings.currency}
                  onChange={(e) => setSettings({ ...settings, currency: e.target.value })}
                  className="w-full h-10 px-3 border border-gray-200 rounded-lg text-sm"
                >
                  <option value="INR">INR (₹)</option>
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="GBP">GBP (£)</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell size={18} />
              Notifications
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-gray-900">Telegram Bot Notifications</div>
                <div className="text-sm text-gray-500">Receive proposal alerts via Telegram</div>
              </div>
              <Toggle
                checked={settings.notif_telegram}
                onChange={(checked) => setSettings({ ...settings, notif_telegram: checked })}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-gray-900">Campaign Completion Alerts</div>
                <div className="text-sm text-gray-500">Notify when campaigns finish sending</div>
              </div>
              <Toggle
                checked={settings.notif_campaign_complete}
                onChange={(checked) => setSettings({ ...settings, notif_campaign_complete: checked })}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-gray-900">AI Opportunity Alerts</div>
                <div className="text-sm text-gray-500">Get notified when new opportunities are discovered</div>
              </div>
              <Toggle
                checked={settings.notif_opportunities}
                onChange={(checked) => setSettings({ ...settings, notif_opportunities: checked })}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-gray-900">Weekly Digest Email</div>
                <div className="text-sm text-gray-500">Receive a weekly performance summary</div>
              </div>
              <Toggle
                checked={settings.notif_weekly_digest}
                onChange={(checked) => setSettings({ ...settings, notif_weekly_digest: checked })}
              />
            </div>
          </CardContent>
        </Card>

        {/* AI Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot size={18} />
              AI Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="ai_model">AI Model</Label>
                <select
                  id="ai_model"
                  value={settings.ai_model}
                  onChange={(e) => setSettings({ ...settings, ai_model: e.target.value })}
                  className="w-full h-10 px-3 border border-gray-200 rounded-lg text-sm"
                >
                  <option value="GPT-5">GPT-5 (Default)</option>
                  <option value="Claude Sonnet">Claude Sonnet</option>
                  <option value="Llama 3.3 70B">Llama 3.3 70B</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="scan_schedule">Autonomous Scanning Schedule</Label>
                <select
                  id="scan_schedule"
                  value={settings.scan_schedule}
                  onChange={(e) => setSettings({ ...settings, scan_schedule: e.target.value })}
                  className="w-full h-10 px-3 border border-gray-200 rounded-lg text-sm"
                >
                  <option value="Daily at 6:00 AM">Daily at 6:00 AM</option>
                  <option value="Every 6 hours">Every 6 hours</option>
                  <option value="Manual only">Manual only</option>
                </select>
              </div>
            </div>
            <div className="flex items-center justify-between pt-2">
              <div>
                <div className="font-medium text-gray-900">Auto-approve Low Risk Proposals</div>
                <div className="text-sm text-gray-500">Auto-approve proposals with confidence score {'>'} 95%</div>
              </div>
              <Toggle
                checked={settings.auto_approve}
                onChange={(checked) => setSettings({ ...settings, auto_approve: checked })}
              />
            </div>
          </CardContent>
        </Card>

        {/* Telegram Bot */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Send size={18} />
              Telegram Bot
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="telegram_token">Bot Token</Label>
              <Input
                id="telegram_token"
                type="password"
                value={settings.telegram_token || ''}
                onChange={(e) => setSettings({ ...settings, telegram_token: e.target.value || null })}
                placeholder="Enter your Telegram bot token"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="telegram_chat_id">Chat ID</Label>
              <Input
                id="telegram_chat_id"
                value={settings.telegram_chat_id || ''}
                onChange={(e) => setSettings({ ...settings, telegram_chat_id: e.target.value || null })}
                placeholder="Enter your Telegram chat ID"
              />
            </div>
            <Button variant="outline" onClick={handleTestTelegram}>
              Test Connection
            </Button>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-4">
          <Button variant="outline">Cancel</Button>
          <Button 
            style={{ backgroundColor: 'var(--color-accent-teal)' }} 
            className="text-white"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? 'Saving...' : saved ? 'Saved!' : 'Save Changes'}
          </Button>
        </div>
      </div>
    </div>
  )
}