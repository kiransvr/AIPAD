import { ChangeEvent, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

type UploadResponse = {
  status?: string
  message?: string
  filename?: string
  file_size_bytes?: number
  upload_id?: string
  summary?: Record<string, unknown>
  error?: string
  details?: Record<string, unknown>
}

const API_BASE = 'http://localhost:8000/api/v1/upload'

const getAuthHeaders = (): Record<string, string> => {
  const token = window.localStorage.getItem('ai-portfolio-token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

function UploadDataPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [response, setResponse] = useState<UploadResponse | null>(null)
  const [sampleTemplate, setSampleTemplate] = useState<Record<string, unknown> | null>(null)
  const [uploadStatus, setUploadStatus] = useState<Record<string, unknown> | null>(null)
  const [statusMessage, setStatusMessage] = useState('Select a CSV or Excel file to upload.')
  const sampleCsvUrl = '/sample-data/portfolio-upload-sample.csv'

  useEffect(() => {
    fetch(`${API_BASE}/sample`, {
      headers: {
        ...getAuthHeaders(),
      },
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Sample template unavailable (${res.status})`)
        }
        return res.json()
      })
      .then((data) => setSampleTemplate(data))
      .catch(() => setSampleTemplate(null))
  }, [])

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null
    setSelectedFile(file)
    setResponse(null)
    setStatusMessage(file ? `Selected ${file.name}` : 'Select a CSV or Excel file to upload.')
  }

  const handleUpload = async () => {
    const token = window.localStorage.getItem('ai-portfolio-token')

    if (!token) {
      setStatusMessage('Please sign in first so the upload can be authorized.')
      setResponse({ status: 'error', error: 'Missing access token. Please sign in again.' })
      return
    }

    if (!selectedFile) {
      setStatusMessage('Choose a file before uploading.')
      return
    }

    const formData = new FormData()
    formData.append('file', selectedFile)
    setIsUploading(true)
    setStatusMessage('Uploading file...')

    try {
      const res = await fetch(API_BASE, {
        method: 'POST',
        headers: {
          ...getAuthHeaders(),
        },
        body: formData,
      })

      const payload = (await res.json().catch(() => null)) as UploadResponse | null

      if (res.status === 401) {
        window.localStorage.removeItem('ai-portfolio-token')
        window.localStorage.removeItem('ai-portfolio-user')
        throw new Error('Session expired or invalid token. Please sign in again.')
      }

      if (res.status === 403) {
        throw new Error('Upload requires admin, risk, branch-manager, or loan-officer role.')
      }

      if (!res.ok) {
        throw new Error(payload?.error || payload?.message || `Upload failed with status ${res.status}`)
      }

      setResponse(payload)
      setStatusMessage('Upload completed successfully.')
      await fetchUploadStatus()
    } catch (error) {
      const message = String(error instanceof Error ? error.message : error)
      setResponse({ status: 'error', error: message })
      setStatusMessage('Upload failed.')
    } finally {
      setIsUploading(false)
    }
  }

  const fetchUploadStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/status`, {
        headers: {
          ...getAuthHeaders(),
        },
      })

      const payload = (await res.json().catch(() => null)) as Record<string, unknown> | null

      if (!res.ok || !payload) {
        return
      }

      setUploadStatus(payload)
    } catch {
      // Keep UI non-blocking if status fetch fails.
    }
  }

  const templateFields = sampleTemplate?.template && typeof sampleTemplate.template === 'object'
    ? Object.entries(sampleTemplate.template as Record<string, unknown>)
    : []

  const templateInstructions = Array.isArray(sampleTemplate?.instructions)
    ? (sampleTemplate.instructions as string[])
    : []

  const templateDescriptions = sampleTemplate?.field_descriptions && typeof sampleTemplate.field_descriptions === 'object'
    ? Object.entries(sampleTemplate.field_descriptions as Record<string, unknown>)
    : []

  const uploadSummary = response?.summary && typeof response.summary === 'object'
    ? (response.summary as Record<string, unknown>)
    : null

  return (
    <div className="container analytics-page">
      <header className="header analytics-header">
        <div>
          <p className="eyebrow">Ingestion</p>
          <h1>Upload Data</h1>
          <p className="subtitle">Upload CSV or Excel files to validate and analyze portfolio data.</p>
        </div>
        <Link className="back-link" to="/">
          Back to dashboard
        </Link>
      </header>

      <main className="main analytics-main">
        <section className="status-card analytics-detail-card">
          <h2>Upload file</h2>
          <p className="status-text">{statusMessage}</p>

          <div className="upload-panel">
            <input
              className="upload-input"
              type="file"
              accept=".csv,.xls,.xlsx"
              onChange={handleFileChange}
            />
            <button className="upload-button" onClick={handleUpload} disabled={isUploading}>
              {isUploading ? 'Uploading...' : 'Upload to backend'}
            </button>
            <button className="upload-button upload-button-secondary" onClick={fetchUploadStatus} disabled={isUploading}>
              Check upload status
            </button>
          </div>

          <div className="upload-actions">
            <a className="upload-secondary-link" href={sampleCsvUrl} download>
              Download sample CSV
            </a>
            <span className="upload-secondary-note">Use this file to test the upload flow immediately.</span>
          </div>

          {selectedFile && <p className="upload-hint">Selected file: {selectedFile.name}</p>}

          {response && (
            <div className="upload-result-grid">
              <article className="upload-result-card">
                <span className="metric-label">Status</span>
                <h3>{response.status ?? 'unknown'}</h3>
                <p>{response.message || response.error || 'Upload response received from backend.'}</p>
              </article>
              <article className="upload-result-card">
                <span className="metric-label">File</span>
                <h3>{response.filename ?? selectedFile?.name ?? 'Unknown file'}</h3>
                <p>{response.file_size_bytes ? `${response.file_size_bytes} bytes` : 'File size not available'}</p>
              </article>
              {uploadSummary && (
                <article className="upload-result-card">
                  <span className="metric-label">Accounts</span>
                  <h3>{String(uploadSummary.total_accounts ?? uploadSummary.rows_processed ?? 'n/a')}</h3>
                  <p>Rows validated by the backend.</p>
                </article>
              )}
            </div>
          )}

          {response && (
            <details className="upload-details">
              <summary>View raw backend response</summary>
              <pre className="debug-info upload-response">{JSON.stringify(response, null, 2)}</pre>
            </details>
          )}

          {uploadStatus && (
            <details className="upload-details" open>
              <summary>Latest upload status</summary>
              <pre className="debug-info upload-response">{JSON.stringify(uploadStatus, null, 2)}</pre>
            </details>
          )}
        </section>

        <section className="status-card analytics-detail-card">
          <h2>Sample template</h2>
          <p className="status-text">The backend exposes a sample template for required upload columns.</p>

          <div className="sample-template-grid">
            <div className="sample-template-card">
              <h3>Required template</h3>
              <div className="template-pill-list">
                {templateFields.map(([key, value]) => (
                  <span key={key} className="template-pill">
                    {key}: {String(value)}
                  </span>
                ))}
              </div>
            </div>

            <div className="sample-template-card">
              <h3>Instructions</h3>
              <ul className="sample-list">
                {templateInstructions.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="sample-template-card sample-template-card-wide">
              <h3>Field guide</h3>
              <div className="field-guide-grid">
                {templateDescriptions.map(([field, description]) => (
                  <div key={field} className="field-guide-item">
                    <strong>{field}</strong>
                    <p>{String(description)}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {!sampleTemplate && <p className="status-text">Loading template...</p>}
        </section>
      </main>
    </div>
  )
}

export default UploadDataPage
