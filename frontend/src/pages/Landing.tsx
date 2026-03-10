import { ArrowRight, Zap, TrendingUp, Shield, Globe, BarChart3, Leaf, Check, ChevronDown, LayoutDashboard, Zap as Energy, FileText, ShoppingCart, Wallet, Activity, Settings as SettingsIcon, X, Building2, Database, TrendingDown, CheckCircle, MessageSquare, Landmark } from 'lucide-react'
import { useState } from 'react'
import { LoginModal } from '../components/LoginModal'
import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui'

export function Landing() {
  const [showLogin, setShowLogin] = useState(false)
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null)
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  interface Feature {
    icon: any
    label: string
    color: string
    description: string
    group?: 'platform' | 'marketplace' | 'admin'
  }

  const features: Feature[] = [
    // Core ESG Platform
    { icon: LayoutDashboard, label: 'Dashboard', color: 'text-blue-400', description: 'Real-time energy monitoring', group: 'platform' },
    { icon: Building2, label: 'Facilities', color: 'text-cyan-400', description: 'Site & asset management', group: 'platform' },
    { icon: Energy, label: 'Energy', color: 'text-yellow-400', description: 'Energy analytics & trends', group: 'platform' },
    { icon: Leaf, label: 'Carbon', color: 'text-green-500', description: 'Emissions calculations', group: 'platform' },
    { icon: TrendingDown, label: 'KPIs', color: 'text-orange-400', description: 'PUE, CUE, WUE metrics', group: 'platform' },
    { icon: Database, label: 'Evidence', color: 'text-indigo-400', description: 'Document repository', group: 'platform' },
    { icon: FileText, label: 'Reports', color: 'text-green-400', description: 'Compliance reports', group: 'platform' },
    { icon: CheckCircle, label: 'Approvals', color: 'text-pink-400', description: 'Workflow management', group: 'platform' },
    { icon: MessageSquare, label: 'Copilot', color: 'text-purple-400', description: 'AI assistant', group: 'platform' },

    // Carbon Marketplace
    { icon: ShoppingCart, label: 'Marketplace', color: 'text-cyan-400', description: 'Browse & trade credits', group: 'marketplace' },
    { icon: Landmark, label: 'Portfolio', color: 'text-emerald-400', description: 'Credit management', group: 'marketplace' },
    { icon: Activity, label: 'Trading', color: 'text-orange-400', description: 'Trade history & analytics', group: 'marketplace' },

    // Administration
    { icon: SettingsIcon, label: 'Settings', color: 'text-purple-400', description: 'Configuration & preferences', group: 'admin' },
  ]

  const groupLabels = {
    platform: '📊 ESG PLATFORM',
    marketplace: '🛍️ CARBON MARKETPLACE',
    admin: '⚙️ ADMINISTRATION'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex">
      {/* Left Sidebar Navigation */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-slate-900/80 backdrop-blur border-r border-slate-700/50 transition-all duration-300 fixed left-0 top-0 h-screen z-40 flex flex-col`}>
        {/* Sidebar Header */}
        <div className="h-20 flex items-center justify-between px-4 border-b border-slate-700/50">
          {sidebarOpen && (
            <div className="flex items-center gap-2">
              <Zap className="w-6 h-6 text-blue-400" />
              <span className="font-bold text-white text-sm">iNetZero</span>
            </div>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-slate-800 rounded-lg transition text-slate-400"
          >
            {sidebarOpen ? <X className="w-4 h-4" /> : <BarChart3 className="w-4 h-4" />}
          </button>
        </div>

        {/* Features List */}
        <nav className="flex-1 p-4 space-y-6 overflow-y-auto">
          {(['platform', 'marketplace', 'admin'] as const).map((group) => {
            const groupFeatures = features.filter(f => f.group === group)
            if (groupFeatures.length === 0) return null

            return (
              <div key={group}>
                {sidebarOpen && (
                  <div className="text-xs font-semibold text-slate-500 mb-3 px-1">
                    {groupLabels[group]}
                  </div>
                )}
                <div className="space-y-2">
                  {groupFeatures.map((feature) => {
                    const Icon = feature.icon
                    return (
                      <div
                        key={feature.label}
                        className="group relative"
                      >
                        <button
                          className="w-full flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-slate-800/50 transition text-slate-300 hover:text-white text-sm"
                          title={feature.label}
                        >
                          <Icon className={`w-5 h-5 ${feature.color} flex-shrink-0`} />
                          {sidebarOpen && (
                            <div className="flex-1 text-left">
                              <div className="font-medium">{feature.label}</div>
                              <div className="text-xs text-slate-400">{feature.description}</div>
                            </div>
                          )}
                        </button>
                        {!sidebarOpen && (
                          <div className="absolute left-20 top-0 bg-slate-800 text-white px-3 py-2 rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition pointer-events-none text-sm z-50">
                            {feature.label}
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
                {group !== 'admin' && sidebarOpen && (
                  <div className="mt-4 border-b border-slate-700/50" />
                )}
              </div>
            )
          })}
        </nav>

        {/* Sign In Button */}
        <div className="p-4 border-t border-slate-700/50">
          <Button
            onClick={() => setShowLogin(true)}
            className={`w-full ${sidebarOpen ? '' : 'p-2'} bg-blue-600 hover:bg-blue-700 text-white text-sm`}
          >
            {sidebarOpen ? '🚀 Sign In' : '→'}
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className={`${sidebarOpen ? 'ml-64' : 'ml-20'} w-full transition-all duration-300`}>
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 backdrop-blur-md bg-slate-950/50 border-b border-primary-500/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Zap className="w-8 h-8 text-primary-400" />
            <span className="text-2xl font-bold bg-gradient-to-r from-primary-400 to-secondary-400 bg-clip-text text-transparent">
              iNetZero
            </span>
          </div>
          <div className="hidden md:flex items-center gap-6">
            <a href="#features" className="text-slate-300 hover:text-white transition">Features</a>
            <a href="#pricing" className="text-slate-300 hover:text-white transition">Pricing</a>
            <a href="#faq" className="text-slate-300 hover:text-white transition">FAQ</a>
            <Button
              variant="primary"
              onClick={() => setShowLogin(true)}
            >
              Sign In
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-6xl mx-auto text-center">
          {/* Badge */}
          <div className="mb-8 inline-block px-4 py-2 bg-primary-500/10 border border-primary-500/30 rounded-full backdrop-blur">
            <span className="text-primary-300 text-sm font-semibold">🚀 Enterprise ESG Platform</span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            <span className="bg-gradient-to-r from-primary-400 via-secondary-400 to-primary-400 bg-clip-text text-transparent">
              Decarbonize Your
            </span>
            <br />
            <span className="bg-gradient-to-r from-secondary-400 via-primary-400 to-secondary-400 bg-clip-text text-transparent">
              Data Center Operations
            </span>
          </h1>

          {/* Subheading */}
          <p className="text-xl text-slate-300 mb-10 max-w-2xl mx-auto leading-relaxed">
            Real-time ESG monitoring, carbon tracking, and sustainability compliance for enterprise datacenters. Transform environmental challenges into competitive advantages.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Button
              variant="primary"
              size="lg"
              onClick={() => setShowLogin(true)}
              className="flex items-center justify-center gap-2 group"
            >
              Get Started Free
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition" />
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="flex items-center justify-center gap-2"
            >
              Watch Demo
            </Button>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
            <Card>
              <CardContent className="pt-6 text-center">
                <div className="text-4xl font-bold text-primary-400 mb-2">91+</div>
                <p className="text-slate-300 text-sm">API Endpoints</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6 text-center">
                <div className="text-4xl font-bold text-secondary-400 mb-2">58+</div>
                <p className="text-slate-300 text-sm">Database Tables</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6 text-center">
                <div className="text-4xl font-bold text-primary-400 mb-2">100%</div>
                <p className="text-slate-300 text-sm">Tests Passing</p>
              </CardContent>
            </Card>
          </div>

          {/* Hero Image Placeholder */}
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-primary-600 to-secondary-600 rounded-2xl blur-3xl opacity-20"></div>
            <div className="relative bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-12 shadow-2xl">
              <div className="bg-slate-900/50 rounded-lg p-6 space-y-4">
                <div className="h-2 bg-gradient-to-r from-primary-600 to-secondary-600 rounded w-1/4"></div>
                <div className="space-y-3">
                  <div className="h-2 bg-slate-700 rounded w-3/4"></div>
                  <div className="h-2 bg-slate-700 rounded w-1/2"></div>
                </div>
              </div>
              <p className="text-center text-slate-400 mt-6 text-sm">Enterprise Dashboard Preview</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 border-t border-slate-800">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Powerful Features</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Everything you need to monitor, report, and optimize your datacenter's environmental impact
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: <BarChart3 className="w-8 h-8 text-primary-400" />,
                title: 'Real-Time Monitoring',
                desc: 'Live energy consumption and carbon emissions tracking'
              },
              {
                icon: <TrendingUp className="w-8 h-8 text-secondary-400" />,
                title: 'Compliance Reports',
                desc: 'Automated ESG compliance and regulatory reporting'
              },
              {
                icon: <Globe className="w-8 h-8 text-success-400" />,
                title: 'Carbon Accounting',
                desc: 'Accurate Scope 1, 2, 3 emissions calculation'
              },
              {
                icon: <Shield className="w-8 h-8 text-primary-400" />,
                title: 'Security First',
                desc: 'Enterprise-grade security and data protection'
              },
              {
                icon: <Leaf className="w-8 h-8 text-success-400" />,
                title: 'Sustainability Goals',
                desc: 'Track and manage ESG targets and KPIs'
              },
              {
                icon: <Zap className="w-8 h-8 text-warning-400" />,
                title: 'Integration Ready',
                desc: 'Connect with your existing tools and systems'
              }
            ].map((feature, i) => (
              <Card key={i} className="group hover:border-primary-500/50">
                <CardContent className="pt-6">
                  <div className="mb-4">{feature.icon}</div>
                  <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
                  <p className="text-slate-400 text-sm">{feature.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-4 border-t border-slate-800">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">Simple, Transparent Pricing</h2>
            <p className="text-slate-400 mb-8">
              Choose the plan that's right for your organization
            </p>

            {/* Billing Toggle */}
            <div className="flex items-center justify-center gap-4">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-4 py-2 rounded-lg transition ${
                  billingCycle === 'monthly'
                    ? 'bg-primary-600 text-white'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('annual')}
                className={`px-4 py-2 rounded-lg transition ${
                  billingCycle === 'annual'
                    ? 'bg-primary-600 text-white'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Annual <span className="text-success-400 text-sm">(Save 20%)</span>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                name: 'Starter',
                price: billingCycle === 'monthly' ? '$99' : '$950',
                description: 'Perfect for getting started',
                features: [
                  'Up to 5 facilities',
                  'Real-time monitoring',
                  'Basic reports',
                  'Email support',
                  'API access',
                ]
              },
              {
                name: 'Professional',
                price: billingCycle === 'monthly' ? '$299' : '$2,870',
                description: 'For growing enterprises',
                features: [
                  'Unlimited facilities',
                  'Real-time monitoring',
                  'Advanced analytics',
                  'Compliance reports',
                  'Priority support',
                  'Custom integrations',
                  'Team collaboration',
                ],
                highlighted: true
              },
              {
                name: 'Enterprise',
                price: 'Custom',
                description: 'For large organizations',
                features: [
                  'Everything in Professional',
                  'Dedicated support',
                  'Custom SLA',
                  'On-premise option',
                  'Advanced security',
                  'Training & consulting',
                ]
              }
            ].map((plan, i) => (
              <Card
                key={i}
                className={plan.highlighted ? 'border-primary-500/50 ring-1 ring-primary-500/20 lg:scale-105' : ''}
              >
                <CardHeader>
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <span className="text-4xl font-bold text-white">{plan.price}</span>
                    {plan.price !== 'Custom' && (
                      <span className="text-slate-400 ml-2">/month</span>
                    )}
                  </div>

                  <ul className="space-y-3">
                    {plan.features.map((feature, j) => (
                      <li key={j} className="flex items-start gap-3">
                        <Check className="w-5 h-5 text-success-400 flex-shrink-0 mt-0.5" />
                        <span className="text-slate-300 text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <Button
                    variant={plan.highlighted ? 'primary' : 'outline'}
                    fullWidth
                    onClick={() => setShowLogin(true)}
                  >
                    Get Started
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 px-4 border-t border-slate-800">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Trusted by Enterprise Datacenters</h2>
            <p className="text-slate-400">
              Leading organizations use iNetZero to achieve their sustainability goals
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                quote: 'iNetZero helped us reduce our carbon footprint by 35% while improving operational efficiency.',
                author: 'Sarah Chen',
                role: 'VP of Operations, Global Tech Corp',
                company: 'Global Tech Corp'
              },
              {
                quote: 'The real-time monitoring and compliance reporting capabilities are invaluable for our regulatory requirements.',
                author: 'Michael Rodriguez',
                role: 'Sustainability Director, CloudServe Inc',
                company: 'CloudServe Inc'
              },
              {
                quote: 'Best investment in our ESG strategy. The ROI is clear with reduced energy costs and improved sustainability metrics.',
                author: 'Jennifer Liu',
                role: 'CTO, DataCenter Solutions',
                company: 'DataCenter Solutions'
              }
            ].map((testimonial, i) => (
              <Card key={i}>
                <CardContent className="pt-6">
                  <p className="text-slate-300 mb-4 text-sm italic">"{testimonial.quote}"</p>
                  <div className="border-t border-slate-700/30 pt-4">
                    <p className="text-white font-semibold text-sm">{testimonial.author}</p>
                    <p className="text-slate-400 text-xs">{testimonial.role}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 px-4 border-t border-slate-800">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">Frequently Asked Questions</h2>
            <p className="text-slate-400">
              Everything you need to know about iNetZero
            </p>
          </div>

          <div className="space-y-4">
            {[
              {
                question: 'How does iNetZero track carbon emissions?',
                answer: 'iNetZero uses industry-standard methodologies to calculate Scope 1, 2, and 3 emissions based on your energy consumption data, facility information, and operational metrics. We integrate with your existing monitoring systems for real-time data.'
              },
              {
                question: 'What integrations does iNetZero support?',
                answer: 'We support integrations with major cloud providers (AWS, Azure, GCP), energy management systems, and custom APIs. Our integration library continues to grow, and we offer custom integrations for enterprise clients.'
              },
              {
                question: 'How secure is my data?',
                answer: 'iNetZero implements enterprise-grade security with end-to-end encryption, regular security audits, SOC 2 compliance, and multi-factor authentication. Your data is stored in secure, redundant facilities with automatic backups.'
              },
              {
                question: 'Can I try iNetZero for free?',
                answer: 'Yes! We offer a free trial for 30 days with full access to all features. No credit card required to get started.'
              },
              {
                question: 'What kind of support do you offer?',
                answer: 'We offer email support for all plans, priority support for Professional plans, and dedicated support teams for Enterprise customers. We also provide comprehensive documentation and training resources.'
              },
              {
                question: 'Can I export my data?',
                answer: 'Absolutely. You can export all your data in multiple formats (CSV, JSON, PDF) at any time. We also provide API access for programmatic data retrieval and integration with your systems.'
              }
            ].map((item, i) => (
              <Card key={i}>
                <button
                  onClick={() => setExpandedFaq(expandedFaq === i ? null : i)}
                  className="w-full text-left p-6 flex items-center justify-between hover:bg-slate-800/30 transition"
                >
                  <h3 className="text-white font-semibold">{item.question}</h3>
                  <ChevronDown
                    className={`w-5 h-5 text-slate-400 transition-transform ${
                      expandedFaq === i ? 'rotate-180' : ''
                    }`}
                  />
                </button>
                {expandedFaq === i && (
                  <div className="px-6 pb-6 text-slate-400 text-sm border-t border-slate-700/30">
                    {item.answer}
                  </div>
                )}
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 px-4 border-t border-slate-800">
        <div className="max-w-4xl mx-auto bg-gradient-to-r from-primary-600/20 to-secondary-600/20 backdrop-blur border border-primary-500/30 rounded-2xl p-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Your Sustainability?
          </h2>
          <p className="text-slate-300 mb-8">
            Join enterprise datacenters reducing carbon footprint with iNetZero. Start your free 30-day trial today.
          </p>
          <Button
            variant="primary"
            size="lg"
            onClick={() => setShowLogin(true)}
          >
            Start Free Trial
          </Button>
        </div>
      </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-12 px-4 bg-slate-900/30">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Zap className="w-6 h-6 text-primary-400" />
                <span className="font-bold text-white">iNetZero</span>
              </div>
              <p className="text-slate-400 text-sm">Enterprise ESG Platform for Datacenters</p>
            </div>
            <div>
              <h3 className="font-bold text-white mb-4">Product</h3>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#features" className="hover:text-white transition">Features</a></li>
                <li><a href="#pricing" className="hover:text-white transition">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition">Security</a></li>
                <li><a href="#" className="hover:text-white transition">API Docs</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-white mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-white transition">About</a></li>
                <li><a href="#" className="hover:text-white transition">Blog</a></li>
                <li><a href="#" className="hover:text-white transition">Careers</a></li>
                <li><a href="#" className="hover:text-white transition">Contact</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-white mb-4">Legal</h3>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-white transition">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white transition">Cookie Policy</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 pt-8 text-center text-slate-500 text-sm">
            <p>© 2026 iNetZero. All rights reserved. | Enterprise ESG Platform</p>
          </div>
        </div>
      </footer>

      {/* Login Modal */}
      {showLogin && <LoginModal onClose={() => setShowLogin(false)} />}
    </div>
  )
}
