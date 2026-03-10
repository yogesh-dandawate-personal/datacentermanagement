/**
 * Emissions Data Entry Page
 * Submit activity data manually or upload CSV/Excel files
 */

import { useState } from 'react'
import { Card, Button, Alert, Spinner, Dialog, Badge, Input } from '@/components/ui'
import { useActivityDataSubmission, useEmissionsSources } from '@/hooks/useEmissions'
import { Upload, Plus, CheckCircle, AlertCircle, FileUp } from 'lucide-react'

export default function DataEntry() {
  const orgId = 'default-org' // Should come from user context
  const { sources } = useEmissionsSources(orgId)

  // Manual entry state
  const [manualMode, setManualMode] = useState<'single' | 'batch'>('single')
  const [selectedSource, setSelectedSource] = useState('')
  const [timestamp, setTimestamp] = useState('')
  const [activityValue, setActivityValue] = useState('')
  const [activityUnit, setActivityUnit] = useState('kWh')
  const [submitted, setSubmitted] = useState(false)

  // Batch file state
  const [dragActive, setDragActive] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [uploadedData, setUploadedData] = useState<any[] | null>(null)

  // API calls
  const { submitSingle, uploadBatch, loading, error } = useActivityDataSubmission(orgId)

  // Handle manual submission
  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedSource || !timestamp || !activityValue) {
      alert('Please fill in all required fields')
      return
    }

    try {
      await submitSingle(selectedSource, timestamp, parseFloat(activityValue), activityUnit)
      setSubmitted(true)

      // Reset form
      setTimeout(() => {
        setSelectedSource('')
        setTimestamp('')
        setActivityValue('')
        setSubmitted(false)
      }, 2000)
    } catch (err) {
      console.error('Error submitting data:', err)
    }
  }

  // Handle drag and drop
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(e.type === 'dragenter' || e.type === 'dragover')
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      const file = files[0]
      if (file.type === 'text/csv' || file.name.endsWith('.csv') || file.type === 'application/vnd.ms-excel') {
        setUploadedFile(file)
        await parseAndPreviewFile(file)
      } else {
        alert('Please upload a CSV or Excel file')
      }
    }
  }

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      const file = files[0]
      setUploadedFile(file)
      await parseAndPreviewFile(file)
    }
  }

  const parseAndPreviewFile = async (file: File) => {
    const text = await file.text()
    const lines = text.split('\n')
    const headers = lines[0].split(',').map((h) => h.trim())

    // Preview first 5 data rows
    const preview = lines.slice(1, 6).map((line) => {
      const values = line.split(',').map((v) => v.trim())
      const row: any = {}
      headers.forEach((header, index) => {
        row[header] = values[index]
      })
      return row
    })

    setUploadedData(preview)
  }

  const handleBatchUpload = async () => {
    if (!uploadedFile) {
      alert('Please select a file')
      return
    }

    try {
      await uploadBatch(uploadedFile, selectedSource || undefined)
      alert('File uploaded successfully!')
      setUploadedFile(null)
      setUploadedData(null)
    } catch (err) {
      console.error('Error uploading file:', err)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Activity Data Entry</h1>
        <p className="text-slate-400 mt-1">Submit emissions activity data manually or via file upload</p>
      </div>

      {/* Mode Selector */}
      <div className="flex gap-3">
        <Button
          variant={manualMode === 'single' ? 'primary' : 'outline'}
          onClick={() => setManualMode('single')}
        >
          <Plus className="w-4 h-4" />
          Manual Entry
        </Button>
        <Button
          variant={manualMode === 'batch' ? 'primary' : 'outline'}
          onClick={() => setManualMode('batch')}
        >
          <Upload className="w-4 h-4" />
          Batch Upload
        </Button>
      </div>

      {error && (
        <Alert variant="error">
          <AlertCircle className="w-5 h-5" />
          {error}
        </Alert>
      )}

      {submitted && (
        <Alert variant="success">
          <CheckCircle className="w-5 h-5" />
          Activity data submitted successfully!
        </Alert>
      )}

      {/* Single Entry Form */}
      {manualMode === 'single' && (
        <Card>
          <h2 className="text-xl font-semibold mb-6">Submit Single Reading</h2>

          <form onSubmit={handleManualSubmit} className="space-y-4">
            {/* Emission Source */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Emission Source <span className="text-red-400">*</span>
              </label>
              <select
                value={selectedSource}
                onChange={(e) => setSelectedSource(e.target.value)}
                className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
              >
                <option value="">Select a source...</option>
                {sources.map((source) => (
                  <option key={source.id} value={source.id}>
                    {source.source_name} ({source.source_type})
                  </option>
                ))}
              </select>
            </div>

            {/* Date/Time */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Date & Time <span className="text-red-400">*</span>
              </label>
              <input
                type="datetime-local"
                value={timestamp}
                onChange={(e) => setTimestamp(e.target.value)}
                className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
              />
            </div>

            {/* Activity Value */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Activity Value <span className="text-red-400">*</span>
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={activityValue}
                  onChange={(e) => setActivityValue(e.target.value)}
                  placeholder="e.g., 150.5"
                  className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Unit of Measure</label>
                <select
                  value={activityUnit}
                  onChange={(e) => setActivityUnit(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
                >
                  <option value="kWh">kWh</option>
                  <option value="therms">Therms</option>
                  <option value="gallons">Gallons</option>
                  <option value="kg">kg</option>
                  <option value="metric_tons">Metric Tons</option>
                </select>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex gap-3 pt-4">
              <Button type="submit" variant="primary" disabled={loading}>
                {loading ? <Spinner /> : <Plus className="w-4 h-4" />}
                {loading ? 'Submitting...' : 'Submit Reading'}
              </Button>
            </div>
          </form>

          {/* Reference Info */}
          <div className="mt-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
            <h3 className="font-medium text-sm mb-2">Tips:</h3>
            <ul className="text-sm text-slate-400 space-y-1">
              <li>✓ All fields are required</li>
              <li>✓ Activity value must be positive</li>
              <li>✓ Use ISO 8601 format for timestamps</li>
              <li>✓ Unit of measure should match the emission source</li>
            </ul>
          </div>
        </Card>
      )}

      {/* Batch Upload */}
      {manualMode === 'batch' && (
        <Card>
          <h2 className="text-xl font-semibold mb-6">Batch File Upload</h2>

          {/* Drop Zone */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition ${
              dragActive ? 'border-blue-500 bg-blue-500/10' : 'border-slate-700 bg-slate-800/50'
            }`}
          >
            {!uploadedFile ? (
              <>
                <FileUp className="w-12 h-12 text-slate-400 mx-auto mb-3" />
                <h3 className="font-medium mb-2">Drag and drop your CSV file</h3>
                <p className="text-sm text-slate-400 mb-4">or</p>
                <label className="cursor-pointer">
                  <Button variant="outline" asChild>
                    <span>Choose File</span>
                  </Button>
                  <input
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </label>
                <p className="text-xs text-slate-500 mt-4">
                  Supported formats: CSV, Excel (XLSX, XLS)
                </p>
              </>
            ) : (
              <>
                <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-3" />
                <h3 className="font-medium mb-2">{uploadedFile.name}</h3>
                <p className="text-sm text-slate-400 mb-4">
                  {(uploadedFile.size / 1024).toFixed(2)} KB
                </p>
                <Button
                  variant="outline"
                  onClick={() => {
                    setUploadedFile(null)
                    setUploadedData(null)
                  }}
                >
                  Change File
                </Button>
              </>
            )}
          </div>

          {/* File Preview */}
          {uploadedData && uploadedData.length > 0 && (
            <div className="mt-6">
              <h3 className="font-medium mb-3">Preview (first 5 rows)</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-700">
                      {Object.keys(uploadedData[0]).map((key) => (
                        <th key={key} className="text-left py-2 px-3 font-medium text-slate-300">
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {uploadedData.map((row, idx) => (
                      <tr key={idx} className="border-b border-slate-700/50">
                        {Object.values(row).map((value, colIdx) => (
                          <td key={colIdx} className="py-2 px-3 text-slate-400">
                            {String(value)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Upload Controls */}
          {uploadedFile && (
            <div className="mt-6 flex gap-3">
              <Button
                variant="primary"
                onClick={handleBatchUpload}
                disabled={loading}
              >
                {loading ? <Spinner /> : <Upload className="w-4 h-4" />}
                {loading ? 'Uploading...' : 'Upload File'}
              </Button>
            </div>
          )}

          {/* CSV Format Guide */}
          <div className="mt-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
            <h3 className="font-medium text-sm mb-3">CSV Format Requirements</h3>
            <p className="text-xs text-slate-400 mb-3">Expected columns:</p>
            <div className="bg-slate-900/50 p-3 rounded font-mono text-xs overflow-x-auto">
              <div>emissions_source_id, timestamp, activity_value, activity_unit</div>
              <div className="text-slate-500 mt-2">
                Example:
                <br />
                {`550e8400-e29b-41d4-a716-446655440000, 2026-03-10T14:30:00Z, 150.5, kWh`}
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
