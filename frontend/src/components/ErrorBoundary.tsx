import { ReactNode, Component, ErrorInfo } from 'react'
import { AlertTriangle } from 'lucide-react'
import { Button } from './ui'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to external service here
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
    // Optionally reload the page
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="min-h-screen flex items-center justify-center bg-slate-950 px-4">
            <div className="max-w-md w-full">
              <div className="text-center">
                <div className="flex justify-center mb-4">
                  <AlertTriangle className="w-16 h-16 text-danger-400" />
                </div>
                <h1 className="text-2xl font-bold text-white mb-2">Something went wrong</h1>
                <p className="text-slate-400 mb-6">
                  An unexpected error occurred. Please try refreshing the page or contact support if the problem persists.
                </p>
                {this.state.error && (
                  <div className="mb-6 p-4 bg-danger-600/10 border border-danger-600/30 rounded-lg">
                    <p className="text-sm text-danger-300 font-mono text-left break-words">
                      {this.state.error.message}
                    </p>
                  </div>
                )}
                <div className="flex gap-2">
                  <Button variant="primary" className="flex-1" onClick={this.handleReset}>
                    Refresh Page
                  </Button>
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => (window.location.href = '/')}
                  >
                    Go Home
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )
      )
    }

    return this.props.children
  }
}
