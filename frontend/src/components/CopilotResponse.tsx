/**
 * Copilot Response Component
 * Displays response message with citations
 */

import { Citation } from '../types/copilot'
import { CitationCard } from './CitationCard'

interface CopilotResponseProps {
  message: string
  citations?: Citation[]
  confidence?: number
  error?: string
  onCitationNavigate?: (link: string) => void
}

export function CopilotResponse({
  message,
  citations = [],
  confidence,
  error,
  onCitationNavigate
}: CopilotResponseProps) {
  return (
    <div className="space-y-4">
      {/* Response Message */}
      <div className="prose prose-sm dark max-w-none">
        <p className="text-slate-100 leading-relaxed">{message}</p>
      </div>

      {/* Confidence Score */}
      {confidence !== undefined && !error && (
        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400">Confidence:</span>
          <div className="flex-1 max-w-xs bg-slate-700/50 rounded-full h-2">
            <div
              className={`
                h-full rounded-full transition-all
                ${confidence >= 0.8
                  ? 'bg-green-500'
                  : confidence >= 0.6
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
                }
              `}
              style={{ width: `${confidence * 100}%` }}
              role="progressbar"
              aria-valuenow={Math.round(confidence * 100)}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label="Response confidence"
            />
          </div>
          <span className="text-slate-300 font-medium">
            {Math.round(confidence * 100)}%
          </span>
        </div>
      )}

      {/* Citations Section */}
      {citations.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
            Citations ({citations.length})
          </h4>
          <div className="space-y-2">
            {citations.map(citation => (
              <CitationCard
                key={citation.id}
                citation={citation}
                onNavigate={onCitationNavigate}
              />
            ))}
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
          <p className="text-xs text-red-200">
            <span className="font-semibold">Error:</span> {error}
          </p>
        </div>
      )}

      {/* No Citations Warning */}
      {!error && citations.length === 0 && confidence && confidence < 0.6 && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
          <p className="text-xs text-yellow-200">
            <span className="font-semibold">Limited confidence:</span> This response may not be fully accurate.
            Consider verifying with source data.
          </p>
        </div>
      )}
    </div>
  )
}
