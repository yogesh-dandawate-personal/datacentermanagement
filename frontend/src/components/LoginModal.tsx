import { X, Mail, Lock, ArrowRight, AlertCircle, CheckCircle } from 'lucide-react'
import { useState } from 'react'

interface LoginModalProps {
  onClose: () => void
}

interface FormErrors {
  name?: string
  email?: string
  password?: string
  submit?: string
}

// Validation helpers
const validateEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

const validatePassword = (password: string): boolean => {
  return password.length >= 6
}

export function LoginModal({ onClose }: LoginModalProps) {
  const [isSignUp, setIsSignUp] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [submitSuccess, setSubmitSuccess] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})

  // Validation function
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    if (isSignUp && !name.trim()) {
      newErrors.name = 'Name is required'
    }

    if (!email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!validateEmail(email)) {
      newErrors.email = 'Please enter a valid email address'
    }

    if (!password) {
      newErrors.password = 'Password is required'
    } else if (!validatePassword(password)) {
      newErrors.password = 'Password must be at least 6 characters'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrors({})

    if (!validateForm()) {
      return
    }

    setIsLoading(true)

    // Simulate API call
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Demo credentials check
      const isValidLogin = !isSignUp && email === 'demo@example.com' && password === 'password'
      const isValidSignUp = isSignUp && name && email && password

      if (isValidLogin || isValidSignUp) {
        setSubmitSuccess(true)
        // Close modal after success
        setTimeout(() => {
          onClose()
        }, 1500)
      } else if (!isSignUp) {
        setErrors({ submit: 'Invalid email or password. Try demo@example.com / password' })
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleToggleMode = () => {
    setIsSignUp(!isSignUp)
    setEmail('')
    setPassword('')
    setName('')
    setErrors({})
    setSubmitSuccess(false)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="relative w-full max-w-md bg-gradient-to-br from-slate-900 to-slate-950 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 hover:bg-slate-800 rounded-lg transition"
          aria-label="Close modal"
        >
          <X className="w-5 h-5 text-slate-400" />
        </button>

        <div className="p-6 sm:p-8">
          {/* Header */}
          <div className="text-center mb-6 sm:mb-8">
            <h2 className="text-2xl font-bold text-white mb-2">
              {isSignUp ? 'Create Account' : 'Welcome Back'}
            </h2>
            <p className="text-slate-400 text-sm">
              {isSignUp
                ? 'Join the ESG monitoring revolution'
                : 'Monitor your datacenter sustainability'}
            </p>
          </div>

          {/* Success Message */}
          {submitSuccess && (
            <div className="mb-6 p-4 bg-success-600/20 border border-success-600/50 rounded-lg flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-success-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-success-400 font-medium text-sm">
                  {isSignUp ? 'Account created successfully!' : 'Logged in successfully!'}
                </p>
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name Field (Sign Up Only) */}
            {isSignUp && (
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-slate-300 mb-2">
                  Full Name
                </label>
                <input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value)
                    if (errors.name) setErrors({ ...errors, name: undefined })
                  }}
                  placeholder="John Doe"
                  className={`w-full px-4 py-3 bg-slate-800/50 border rounded-lg text-white placeholder-slate-500 focus:outline-none transition ${
                    errors.name
                      ? 'border-danger-500/50 focus:border-danger-500'
                      : 'border-slate-700/50 focus:border-blue-500/50'
                  }`}
                  disabled={isLoading}
                />
                {errors.name && (
                  <p className="text-danger-400 text-xs mt-1 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" />
                    {errors.name}
                  </p>
                )}
              </div>
            )}

            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3.5 w-5 h-5 text-slate-500 pointer-events-none" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value)
                    if (errors.email) setErrors({ ...errors, email: undefined })
                  }}
                  placeholder="your@company.com"
                  className={`w-full pl-10 pr-4 py-3 bg-slate-800/50 border rounded-lg text-white placeholder-slate-500 focus:outline-none transition ${
                    errors.email
                      ? 'border-danger-500/50 focus:border-danger-500'
                      : 'border-slate-700/50 focus:border-blue-500/50'
                  }`}
                  disabled={isLoading}
                />
              </div>
              {errors.email && (
                <p className="text-danger-400 text-xs mt-1 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  {errors.email}
                </p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3.5 w-5 h-5 text-slate-500 pointer-events-none" />
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value)
                    if (errors.password) setErrors({ ...errors, password: undefined })
                  }}
                  placeholder="••••••••"
                  className={`w-full pl-10 pr-4 py-3 bg-slate-800/50 border rounded-lg text-white placeholder-slate-500 focus:outline-none transition ${
                    errors.password
                      ? 'border-danger-500/50 focus:border-danger-500'
                      : 'border-slate-700/50 focus:border-blue-500/50'
                  }`}
                  disabled={isLoading}
                />
              </div>
              {errors.password && (
                <p className="text-danger-400 text-xs mt-1 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  {errors.password}
                </p>
              )}
            </div>

            {/* Submit Error Message */}
            {errors.submit && (
              <div className="p-4 bg-danger-600/20 border border-danger-600/50 rounded-lg flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-danger-400 flex-shrink-0 mt-0.5" />
                <p className="text-danger-400 text-sm">{errors.submit}</p>
              </div>
            )}

            {/* Remember Me / Forgot Password */}
            {!isSignUp && (
              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2 text-slate-400 cursor-pointer hover:text-slate-300 transition">
                  <input type="checkbox" className="rounded" disabled={isLoading} />
                  Remember me
                </label>
                <a href="#" className="text-blue-400 hover:text-blue-300 transition">
                  Forgot password?
                </a>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || submitSuccess}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-slate-700 disabled:to-slate-800 disabled:cursor-not-allowed rounded-lg font-bold text-white flex items-center justify-center gap-2 transition mt-6"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                  {isSignUp ? 'Creating account...' : 'Signing in...'}
                </>
              ) : submitSuccess ? (
                <>
                  <CheckCircle className="w-4 h-4" />
                  {isSignUp ? 'Account Created' : 'Signed In'}
                </>
              ) : (
                <>
                  {isSignUp ? 'Create Account' : 'Sign In'}
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Toggle Sign Up / Sign In */}
          <div className="mt-6 text-center border-t border-slate-700/50 pt-6">
            <p className="text-slate-400 text-sm mb-2">
              {isSignUp
                ? 'Already have an account?'
                : "Don't have an account?"}
            </p>
            <button
              onClick={handleToggleMode}
              disabled={isLoading}
              className="text-blue-400 hover:text-blue-300 font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSignUp ? 'Sign In' : 'Create Account'}
            </button>
          </div>

          {/* Demo Credentials Hint */}
          {!isSignUp && (
            <div className="mt-4 p-3 bg-slate-800/30 border border-slate-700/30 rounded-lg text-xs text-slate-400">
              <p className="font-medium text-slate-300 mb-1">Demo Credentials:</p>
              <p>Email: <span className="text-blue-300 font-mono">demo@example.com</span></p>
              <p>Password: <span className="text-blue-300 font-mono">password</span></p>
            </div>
          )}

          {/* Social Login */}
          <div className="mt-8">
            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-700/50"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-slate-950 text-slate-400">Or continue with</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                disabled={isLoading}
                className="px-4 py-2 bg-slate-800/50 border border-slate-700/50 rounded-lg hover:border-slate-600 transition text-white text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Google
              </button>
              <button
                type="button"
                disabled={isLoading}
                className="px-4 py-2 bg-slate-800/50 border border-slate-700/50 rounded-lg hover:border-slate-600 transition text-white text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Microsoft
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
