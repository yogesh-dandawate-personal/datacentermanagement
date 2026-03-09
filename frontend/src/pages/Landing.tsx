import { ArrowRight, Zap, TrendingUp, Shield, Globe, BarChart3, Leaf } from 'lucide-react'
import { useState } from 'react'
import { LoginModal } from '../components/LoginModal'

export function Landing() {
  const [showLogin, setShowLogin] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 backdrop-blur-md bg-slate-950/50 border-b border-blue-500/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Zap className="w-8 h-8 text-blue-400" />
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              iNetZero
            </span>
          </div>
          <div className="flex items-center gap-6">
            <button className="text-slate-300 hover:text-white transition">Platform</button>
            <button className="text-slate-300 hover:text-white transition">Features</button>
            <button className="text-slate-300 hover:text-white transition">Pricing</button>
            <button
              onClick={() => setShowLogin(true)}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition"
            >
              Sign In
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <div className="mb-8 inline-block px-4 py-2 bg-blue-500/10 border border-blue-500/30 rounded-full backdrop-blur">
            <span className="text-blue-300 text-sm font-semibold">🚀 Enterprise ESG Platform</span>
          </div>

          <h1 className="text-6xl md:text-7xl font-bold mb-6 leading-tight">
            <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-400 bg-clip-text text-transparent">
              Decarbonize Your
            </span>
            <br />
            <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Data Center Operations
            </span>
          </h1>

          <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto leading-relaxed">
            Real-time ESG monitoring, carbon tracking, and sustainability compliance for enterprise datacenters. Transform environmental challenges into competitive advantages.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <button
              onClick={() => setShowLogin(true)}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 rounded-xl font-bold flex items-center justify-center gap-2 transition group"
            >
              Get Started Free
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition" />
            </button>
            <button className="px-8 py-4 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl font-bold transition">
              Watch Demo
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <div className="p-6 bg-slate-800/30 backdrop-blur border border-slate-700/50 rounded-xl hover:border-blue-500/50 transition">
              <div className="text-3xl font-bold text-blue-400 mb-2">91+</div>
              <p className="text-slate-300">API Endpoints Ready</p>
            </div>
            <div className="p-6 bg-slate-800/30 backdrop-blur border border-slate-700/50 rounded-xl hover:border-blue-500/50 transition">
              <div className="text-3xl font-bold text-cyan-400 mb-2">28+</div>
              <p className="text-slate-300">Database Tables</p>
            </div>
            <div className="p-6 bg-slate-800/30 backdrop-blur border border-slate-700/50 rounded-xl hover:border-blue-500/50 transition">
              <div className="text-3xl font-bold text-blue-400 mb-2">100%</div>
              <p className="text-slate-300">Tests Passing</p>
            </div>
          </div>

          {/* Dashboard Preview - Glassmorphic */}
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl blur-3xl opacity-20"></div>
            <div className="relative bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
              <div className="bg-slate-900/50 rounded-lg p-6 space-y-4">
                <div className="h-2 bg-gradient-to-r from-blue-600 to-cyan-600 rounded w-1/4"></div>
                <div className="space-y-3">
                  <div className="h-2 bg-slate-700 rounded w-3/4"></div>
                  <div className="h-2 bg-slate-700 rounded w-1/2"></div>
                </div>
              </div>
              <p className="text-center text-slate-400 mt-4">Enterprise Dashboard Coming Soon</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 border-t border-slate-800">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-4 text-white">Powerful Features</h2>
          <p className="text-center text-slate-400 mb-16 max-w-2xl mx-auto">
            Everything you need to monitor, report, and optimize your datacenter's environmental impact
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: <BarChart3 className="w-8 h-8 text-blue-400" />,
                title: 'Real-Time Monitoring',
                desc: 'Live energy consumption and carbon emissions tracking'
              },
              {
                icon: <TrendingUp className="w-8 h-8 text-cyan-400" />,
                title: 'Compliance Reports',
                desc: 'Automated ESG compliance and regulatory reporting'
              },
              {
                icon: <Globe className="w-8 h-8 text-green-400" />,
                title: 'Carbon Accounting',
                desc: 'Accurate Scope 1, 2, 3 emissions calculation'
              },
              {
                icon: <Shield className="w-8 h-8 text-blue-400" />,
                title: 'Security First',
                desc: 'Enterprise-grade security and data protection'
              },
              {
                icon: <Leaf className="w-8 h-8 text-green-400" />,
                title: 'Sustainability Goals',
                desc: 'Track and manage ESG targets and KPIs'
              },
              {
                icon: <Zap className="w-8 h-8 text-yellow-400" />,
                title: 'Integration Ready',
                desc: 'Connect with your existing tools and systems'
              }
            ].map((feature, i) => (
              <div key={i} className="group p-6 bg-slate-800/30 backdrop-blur border border-slate-700/50 rounded-xl hover:border-blue-500/50 transition">
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
                <p className="text-slate-400 text-sm">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto bg-gradient-to-r from-blue-600/20 to-cyan-600/20 backdrop-blur border border-blue-500/30 rounded-2xl p-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Your Sustainability?
          </h2>
          <p className="text-slate-300 mb-8">
            Join enterprise datacenters reducing carbon footprint with iNetZero
          </p>
          <button
            onClick={() => setShowLogin(true)}
            className="px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-xl font-bold transition"
          >
            Start Free Trial Today
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-12 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Zap className="w-6 h-6 text-blue-400" />
                <span className="font-bold text-white">iNetZero</span>
              </div>
              <p className="text-slate-400 text-sm">Enterprise ESG Platform</p>
            </div>
            <div>
              <h3 className="font-bold text-white mb-4">Product</h3>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-white transition">Features</a></li>
                <li><a href="#" className="hover:text-white transition">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition">Security</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-white mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-white transition">About</a></li>
                <li><a href="#" className="hover:text-white transition">Blog</a></li>
                <li><a href="#" className="hover:text-white transition">Contact</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-white mb-4">Legal</h3>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-white transition">Privacy</a></li>
                <li><a href="#" className="hover:text-white transition">Terms</a></li>
                <li><a href="#" className="hover:text-white transition">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 pt-8 text-center text-slate-500 text-sm">
            <p>© 2026 iNetZero. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Login Modal */}
      {showLogin && <LoginModal onClose={() => setShowLogin(false)} />}
    </div>
  )
}
