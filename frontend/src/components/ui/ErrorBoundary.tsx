import { Component, ReactNode } from 'react'
import { AlertCircle } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error) {
    console.error('Error caught by boundary:', error)
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="p-6 bg-danger-500/5 border border-danger-500/20 rounded-lg">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-danger-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-medium text-danger-400 mb-1">Something went wrong</h3>
              <p className="text-sm text-danger-300">
                {this.state.error?.message || 'An unexpected error occurred'}
              </p>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
