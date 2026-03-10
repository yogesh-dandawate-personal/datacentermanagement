/**
 * ReportPreview Component
 * Live preview of reports before sending
 */

import { Eye, Download, Send } from 'lucide-react'
import { Card } from './ui/Card'
import { Button } from './ui/Button'
import { Badge } from './ui/Badge'
import type { ReportPreview as ReportPreviewType } from '../services/api'

interface ReportPreviewProps {
  preview: ReportPreviewType | null
  loading?: boolean
}

export function ReportPreview({ preview, loading }: ReportPreviewProps) {
  if (loading) {
    return (
      <Card>
        <div className="p-12 text-center text-slate-400">
          <Eye className="w-12 h-12 mx-auto mb-3 opacity-50 animate-pulse" />
          <p>Generating preview...</p>
        </div>
      </Card>
    )
  }

  if (!preview) {
    return (
      <Card>
        <div className="p-12 text-center text-slate-500">
          <Eye className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No preview available</p>
          <p className="text-sm mt-1">Select a template to preview</p>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <Card>
        <div className="p-6 border-b border-slate-700/30">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold text-white">{preview.template_name}</h3>
              <p className="text-sm text-slate-400 mt-1">
                Generated {new Date(preview.generated_at).toLocaleString()}
              </p>
            </div>
            <div className="flex gap-2">
              <Badge variant="info" size="sm">{preview.total_pages} pages</Badge>
              <Badge variant="secondary" size="sm">{preview.file_size_kb} KB</Badge>
            </div>
          </div>
        </div>

        <div className="p-6 space-y-4">
          {preview.sections.map((section, index) => (
            <div key={index} className="border-b border-slate-700/30 pb-4 last:border-0">
              <h4 className="text-lg font-semibold text-white mb-2">{section.title}</h4>
              <div className="text-sm text-slate-300 bg-slate-800/30 p-4 rounded-lg">
                {typeof section.content === 'string' ? (
                  <p>{section.content}</p>
                ) : (
                  <pre className="whitespace-pre-wrap">{JSON.stringify(section.content, null, 2)}</pre>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="p-6 border-t border-slate-700/30 flex gap-3">
          <Button variant="outline" icon={<Download className="w-4 h-4" />}>
            Download PDF
          </Button>
          <Button variant="primary" icon={<Send className="w-4 h-4" />}>
            Send Now
          </Button>
        </div>
      </Card>
    </div>
  )
}
