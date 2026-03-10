/**
 * Citation Card Component
 * Displays citation details with expandable information
 */

import { useState, useCallback } from 'react'
import { ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'
import { Citation } from '../types/copilot'
import { Button } from './ui/Button'
import { Card, CardContent } from './ui/Card'

interface CitationCardProps {
  citation: Citation
  onNavigate?: (link: string) => void
}

const citationTypeColors = {
  metric: 'border-blue-500/30 bg-blue-500/5',
  report: 'border-purple-500/30 bg-purple-500/5',
  evidence: 'border-green-500/30 bg-green-500/5',
  document: 'border-amber-500/30 bg-amber-500/5'
}

const citationTypeLabels = {
  metric: 'Metric',
  report: 'Report',
  evidence: 'Evidence',
  document: 'Document'
}

export function CitationCard({ citation, onNavigate }: CitationCardProps) {
  const [expanded, setExpanded] = useState(false)

  const handleNavigate = useCallback(() => {
    if (citation.link) {
      if (onNavigate) {
        onNavigate(citation.link)
      } else {
        window.open(citation.link, '_blank')
      }
    }
  }, [citation.link, onNavigate])

  const typeColor = citationTypeColors[citation.type] || citationTypeColors.document
  const typeLabel = citationTypeLabels[citation.type] || 'Citation'

  return (
    <Card
      className={`
        border ${typeColor}
        hover:border-opacity-60 transition-all cursor-pointer
        mb-2
      `}
    >
      <CardContent className="p-3">
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-start gap-3 focus:outline-none focus:ring-2 focus:ring-primary-500/50 rounded"
          aria-expanded={expanded}
        >
          <div className="flex-1 text-left">
            <div className="flex items-center gap-2">
              <span className="inline-block text-xs font-semibold px-2 py-1 rounded bg-slate-700/50 text-slate-300">
                {typeLabel}
              </span>
              {citation.confidence && (
                <span
                  className={`
                    text-xs font-medium px-2 py-1 rounded
                    ${citation.confidence >= 0.8
                      ? 'bg-green-500/20 text-green-300'
                      : citation.confidence >= 0.6
                      ? 'bg-yellow-500/20 text-yellow-300'
                      : 'bg-red-500/20 text-red-300'
                    }
                  `}
                  aria-label={`Confidence: ${Math.round(citation.confidence * 100)}%`}
                >
                  {Math.round(citation.confidence * 100)}%
                </span>
              )}
            </div>

            <h4 className="font-semibold text-slate-100 mt-2 text-sm">
              {citation.name}
            </h4>

            {citation.value !== undefined && (
              <p className="text-slate-300 text-sm mt-1">
                <span className="font-medium text-primary-400">
                  {citation.value}
                </span>
                {citation.unit && (
                  <span className="ml-1 text-slate-400">{citation.unit}</span>
                )}
              </p>
            )}

            {citation.description && !expanded && (
              <p className="text-slate-400 text-xs mt-1 line-clamp-2">
                {citation.description}
              </p>
            )}
          </div>

          <div className="flex-shrink-0 mt-1">
            {expanded ? (
              <ChevronUp className="w-4 h-4 text-slate-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-slate-400" />
            )}
          </div>
        </button>

        {expanded && (
          <div className="mt-3 pt-3 border-t border-slate-700/30">
            {citation.description && (
              <div className="mb-3">
                <p className="text-xs text-slate-400 font-medium mb-1">Description</p>
                <p className="text-sm text-slate-300">{citation.description}</p>
              </div>
            )}

            {citation.source && (
              <div className="mb-3">
                <p className="text-xs text-slate-400 font-medium mb-1">Source</p>
                <p className="text-sm text-slate-300">{citation.source}</p>
              </div>
            )}

            {citation.date && (
              <div className="mb-3">
                <p className="text-xs text-slate-400 font-medium mb-1">Date</p>
                <p className="text-sm text-slate-300">
                  {new Date(citation.date).toLocaleDateString()}
                </p>
              </div>
            )}

            {citation.owner && (
              <div className="mb-3">
                <p className="text-xs text-slate-400 font-medium mb-1">Owner</p>
                <p className="text-sm text-slate-300">{citation.owner}</p>
              </div>
            )}

            {citation.link && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleNavigate}
                className="w-full mt-3 text-xs"
                aria-label={`Navigate to ${citation.name}`}
              >
                <ExternalLink className="w-3.5 h-3.5 mr-2" />
                View Source
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
