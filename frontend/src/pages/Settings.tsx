import { Bell, Lock, Key, Zap, Users, CreditCard, LogOut, Save } from 'lucide-react'
import { useState } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter, Button, Input, Toggle, Badge } from '../components/ui'

export function Settings() {
  const [activeTab, setActiveTab] = useState('profile')
  const [formData, setFormData] = useState({
    fullName: 'John Doe',
    email: 'john@company.com',
    company: 'iNetZero Corp',
    timezone: 'UTC-8',
  })

  const tabs = [
    { id: 'profile', label: 'Profile', icon: Users },
    { id: 'organization', label: 'Organization', icon: Zap },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Lock },
    { id: 'api', label: 'API Keys', icon: Key },
    { id: 'billing', label: 'Billing', icon: CreditCard },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-slate-400">Manage your account and preferences</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex flex-wrap gap-2 border-b border-slate-700/30 pb-4">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg transition-colors
                ${isActive
                  ? 'bg-primary-600/20 text-primary-400 border border-primary-500/30'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/30'
                }
              `}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm font-medium">{tab.label}</span>
            </button>
          )
        })}
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Personal Information</CardTitle>
              <CardDescription>Update your account details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                label="Full Name"
                value={formData.fullName}
                onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                placeholder="John Doe"
              />
              <Input
                label="Email Address"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="john@company.com"
              />
              <Input
                label="Company"
                value={formData.company}
                onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                placeholder="iNetZero Corp"
              />
              <Input
                label="Timezone"
                value={formData.timezone}
                onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
              />
            </CardContent>
            <CardFooter>
              <Button variant="outline">Cancel</Button>
              <Button variant="primary">
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}

      {/* Organization Tab */}
      {activeTab === 'organization' && (
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Organization Settings</CardTitle>
              <CardDescription>Manage your organization</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input label="Organization Name" placeholder="iNetZero Corp" />
              <Input label="Organization ID" placeholder="org_12345" disabled />
              <Input label="Support Email" placeholder="support@company.com" />
              <Input label="Industry" placeholder="Data Center Operations" />
            </CardContent>
            <CardFooter>
              <Button variant="outline">Cancel</Button>
              <Button variant="primary">Save Changes</Button>
            </CardFooter>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Team Members</CardTitle>
              <CardDescription>Manage team access and permissions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: 'John Doe', email: 'john@company.com', role: 'Admin', status: 'Active' },
                  { name: 'Jane Smith', email: 'jane@company.com', role: 'Editor', status: 'Active' },
                  { name: 'Mike Johnson', email: 'mike@company.com', role: 'Viewer', status: 'Invited' },
                ].map((member, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg">
                    <div>
                      <p className="text-white font-medium">{member.name}</p>
                      <p className="text-xs text-slate-400">{member.email}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={member.status === 'Active' ? 'success' : 'warning'} size="sm">
                        {member.status}
                      </Badge>
                      <span className="text-xs text-slate-400">{member.role}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Email Notifications</CardTitle>
              <CardDescription>Manage what notifications you receive</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Toggle
                label="Daily Energy Reports"
                description="Receive daily summaries of energy consumption"
                defaultChecked
              />
              <Toggle
                label="Alert Notifications"
                description="Get notified when thresholds are exceeded"
                defaultChecked
              />
              <Toggle
                label="Weekly Digest"
                description="Receive weekly ESG performance summaries"
                defaultChecked
              />
              <Toggle
                label="Compliance Alerts"
                description="Get notified of compliance-related issues"
                defaultChecked
              />
            </CardContent>
          </Card>
        </div>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Password</CardTitle>
              <CardDescription>Change your password regularly to keep your account secure</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input label="Current Password" type="password" placeholder="••••••••" />
              <Input label="New Password" type="password" placeholder="••••••••" />
              <Input label="Confirm Password" type="password" placeholder="••••••••" />
            </CardContent>
            <CardFooter>
              <Button variant="outline">Cancel</Button>
              <Button variant="primary">Update Password</Button>
            </CardFooter>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Two-Factor Authentication</CardTitle>
              <CardDescription>Add an extra layer of security to your account</CardDescription>
            </CardHeader>
            <CardContent className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">2FA Status</p>
                <p className="text-sm text-slate-400">Not enabled</p>
              </div>
              <Button variant="primary">Enable 2FA</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Active Sessions</CardTitle>
              <CardDescription>Manage your active login sessions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { browser: 'Chrome on macOS', ip: '192.168.1.100', lastActive: 'Just now', current: true },
                  { browser: 'Safari on iOS', ip: '192.168.1.101', lastActive: '2 hours ago', current: false },
                  { browser: 'Firefox on Windows', ip: '192.168.1.102', lastActive: '1 day ago', current: false },
                ].map((session, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg">
                    <div>
                      <p className="text-white font-medium text-sm">{session.browser}</p>
                      <p className="text-xs text-slate-400">{session.ip} • {session.lastActive}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {session.current && (
                        <Badge variant="success" size="sm">Current</Badge>
                      )}
                      {!session.current && (
                        <Button variant="ghost" size="sm">Revoke</Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* API Keys Tab */}
      {activeTab === 'api' && (
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>API Keys</CardTitle>
              <CardDescription>Manage API keys for programmatic access</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: 'Production API Key', key: 'sk_live_••••••••••••••••', created: '3 months ago', lastUsed: '2 hours ago' },
                  { name: 'Development API Key', key: 'sk_test_••••••••••••••••', created: '2 months ago', lastUsed: '1 day ago' },
                ].map((apiKey, i) => (
                  <div key={i} className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/30">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-white font-medium">{apiKey.name}</p>
                      <Button variant="ghost" size="sm">Copy</Button>
                    </div>
                    <p className="text-sm text-slate-400 font-mono mb-3">{apiKey.key}</p>
                    <div className="flex items-center justify-between text-xs text-slate-500">
                      <span>Created {apiKey.created}</span>
                      <span>Last used {apiKey.lastUsed}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
            <CardFooter>
              <Button variant="primary">Generate New Key</Button>
            </CardFooter>
          </Card>
        </div>
      )}

      {/* Billing Tab */}
      {activeTab === 'billing' && (
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Billing Information</CardTitle>
              <CardDescription>Manage your billing details and subscription</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-slate-800/30 rounded-lg">
                <p className="text-sm text-slate-400 mb-2">Current Plan</p>
                <p className="text-xl font-bold text-white mb-1">Professional</p>
                <p className="text-sm text-slate-400">$299/month • Renews December 9, 2026</p>
              </div>
              <Input label="Billing Email" placeholder="billing@company.com" />
              <Input label="Card Holder Name" placeholder="John Doe" />
            </CardContent>
            <CardFooter>
              <Button variant="outline">Change Plan</Button>
              <Button variant="primary">Update Billing</Button>
            </CardFooter>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Billing History</CardTitle>
              <CardDescription>View your past invoices and payments</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {[
                  { date: 'Dec 9, 2025', amount: '$299.00', status: 'Paid', invoice: '#INV-0012' },
                  { date: 'Nov 9, 2025', amount: '$299.00', status: 'Paid', invoice: '#INV-0011' },
                  { date: 'Oct 9, 2025', amount: '$299.00', status: 'Paid', invoice: '#INV-0010' },
                ].map((billing, i) => (
                  <div key={i} className="flex items-center justify-between p-3 text-sm">
                    <div>
                      <p className="text-white font-medium">{billing.date}</p>
                      <p className="text-xs text-slate-400">{billing.invoice}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-white font-medium">{billing.amount}</span>
                      <Badge variant="success" size="sm">{billing.status}</Badge>
                      <Button variant="ghost" size="sm">Download</Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Danger Zone */}
      <Card className="border-danger-500/30 bg-danger-500/5">
        <CardHeader>
          <CardTitle className="text-danger-400">Danger Zone</CardTitle>
          <CardDescription>Irreversible actions</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-danger-500/10 border border-danger-500/20 rounded-lg">
            <p className="text-white font-medium mb-2">Sign out all devices</p>
            <p className="text-sm text-danger-300 mb-4">This will sign you out of all devices and sessions</p>
            <Button variant="danger" size="sm">
              <LogOut className="w-4 h-4 mr-2" />
              Sign out all devices
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
