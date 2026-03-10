/**
 * ReportTemplates Component
 * Template management for customizable reports
 */

import { useState } from 'react'
import { FileText, Plus, Edit2, Trash2 } from 'lucide-react'
import { Button } from './ui/Button'
import { Card } from './ui/Card'
import { Input } from './ui/Input'
import { Textarea } from './ui/Textarea'
import { Select } from './ui/Select'
import { Badge } from './ui/Badge'
import { Dialog } from './ui/Dialog'
import { Checkbox } from './ui/Checkbox'
import type { ReportTemplate, CreateReportTemplate } from '../services/api'

interface ReportTemplatesProps {
  templates: ReportTemplate[]
  onCreate: (data: CreateReportTemplate) => Promise<void>
  onUpdate: (id: string, data: Partial<ReportTemplate>) => Promise<void>
  onDelete: (id: string) => Promise<void>
}

const availableSections = [
  'Executive Summary',
  'Emissions Overview',
  'Energy Consumption',
  'Renewable Energy',
  'Compliance Status',
  'Sustainability Goals',
  'Recommendations',
  'Data Tables',
  'Charts & Visualizations',
]

export function ReportTemplates({ templates, onCreate, onUpdate, onDelete }: ReportTemplatesProps) {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editing, setEditing] = useState<ReportTemplate | null>(null)
  const [formData, setFormData] = useState<Partial<CreateReportTemplate>>({
    name: '',
    description: '',
    type: 'ESG',
    sections: [],
  })

  const handleSubmit = async () => {
    if (!formData.name || !formData.type) return

    try {
      if (editing) {
        await onUpdate(editing.id, formData as Partial<ReportTemplate>)
      } else {
        await onCreate(formData as CreateReportTemplate)
      }
      closeModal()
    } catch (error) {
      console.error('Failed to save template:', error)
    }
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setEditing(null)
    setFormData({ name: '', description: '', type: 'ESG', sections: [] })
  }

  const handleEdit = (template: ReportTemplate) => {
    setEditing(template)
    setFormData({
      name: template.name,
      description: template.description,
      type: template.type,
      sections: template.sections,
    })
    setIsModalOpen(true)
  }

  const toggleSection = (section: string) => {
    const sections = formData.sections || []
    const newSections = sections.includes(section)
      ? sections.filter((s) => s !== section)
      : [...sections, section]
    setFormData({ ...formData, sections: newSections })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Report Templates</h2>
          <p className="text-sm text-slate-400 mt-1">Manage reusable report templates</p>
        </div>
        <Button variant="primary" onClick={() => setIsModalOpen(true)} icon={<Plus className="w-4 h-4" />}>
          New Template
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map((template) => (
          <Card key={template.id} className="hover:border-blue-500/50 transition">
            <div className="p-6">
              <div className="flex items-start justify-between mb-3">
                <FileText className="w-8 h-8 text-blue-400" />
                <Badge variant="primary" size="sm">{template.type}</Badge>
              </div>

              <h3 className="text-lg font-semibold text-white mb-2">{template.name}</h3>
              <p className="text-sm text-slate-400 mb-4 line-clamp-2">{template.description}</p>

              <div className="mb-4">
                <p className="text-xs text-slate-500 mb-2">{template.sections.length} sections</p>
                <div className="flex flex-wrap gap-1">
                  {template.sections.slice(0, 3).map((section, idx) => (
                    <Badge key={idx} variant="secondary" size="sm">{section}</Badge>
                  ))}
                  {template.sections.length > 3 && (
                    <Badge variant="secondary" size="sm">+{template.sections.length - 3}</Badge>
                  )}
                </div>
              </div>

              <div className="flex gap-2 pt-4 border-t border-slate-700/30">
                <Button variant="ghost" size="sm" onClick={() => handleEdit(template)} icon={<Edit2 className="w-4 h-4" />}>
                  Edit
                </Button>
                <Button variant="ghost" size="sm" onClick={() => onDelete(template.id)} icon={<Trash2 className="w-4 h-4" />} className="text-red-400">
                  Delete
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Dialog open={isModalOpen} onClose={closeModal} title={editing ? 'Edit Template' : 'Create Template'}>
        <div className="space-y-4">
          <Input
            label="Template Name"
            placeholder="Quarterly ESG Report"
            value={formData.name || ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />

          <Textarea
            label="Description"
            placeholder="Comprehensive quarterly ESG report..."
            value={formData.description || ''}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={3}
          />

          <Select
            label="Report Type"
            value={formData.type || 'ESG'}
            onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
            options={[
              { value: 'ESG', label: 'ESG Report' },
              { value: 'Compliance', label: 'Compliance Report' },
              { value: 'Energy', label: 'Energy Report' },
              { value: 'Custom', label: 'Custom Report' },
            ]}
            required
          />

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-3">Report Sections</label>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {availableSections.map((section) => (
                <div key={section} className="flex items-center gap-3 p-2 hover:bg-slate-800/30 rounded">
                  <Checkbox
                    checked={(formData.sections || []).includes(section)}
                    onChange={() => toggleSection(section)}
                  />
                  <span className="text-sm text-slate-300">{section}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={closeModal} fullWidth>Cancel</Button>
            <Button variant="primary" onClick={handleSubmit} fullWidth>
              {editing ? 'Save Changes' : 'Create Template'}
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  )
}
