import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchAuthJson } from '../services/api'

type ParSummary = {
  total_par: number
  par_30: number
  par_60: number
  par_90: number
  par_180_plus: number
}

type NplSummary = {
  npl_count: number
  npl_amount: number
  npl_ratio: number
  recovery_rate: number
}

type NplByStage = {
  stages: Array<{ stage: string; count: number; amount: number; percentage: number }>
}

type Collections = {
  pipeline: Array<{ stage: string; count: number; recovery_amount: number }>
  total_recovered: number
}

function RiskManagementPage() {
  const [parSummary, setParSummary] = useState<ParSummary | null>(null)
  const [nplSummary, setNplSummary] = useState<NplSummary | null>(null)
  const [stageData, setStageData] = useState<NplByStage | null>(null)
  const [collections, setCollections] = useState<Collections | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      fetchAuthJson<ParSummary>('/par/summary'),
      fetchAuthJson<NplSummary>('/npl/summary'),
      fetchAuthJson<NplByStage>('/npl/by-stage'),
      fetchAuthJson<Collections>('/npl/collections'),
    ])
      .then(([parData, nplData, stagePayload, collectionsPayload]) => {
        setParSummary(parData)
        setNplSummary(nplData)
        setStageData(stagePayload)
        setCollections(collectionsPayload)
      })
      .catch((err) => setError(String(err instanceof Error ? err.message : err)))
  }, [])

  const maxStagePct = useMemo(() => {
    if (!stageData?.stages?.length) {
      return 1
    }
    return Math.max(...stageData.stages.map((item) => item.percentage), 1)
  }, [stageData])

  return (
    <div className="container analytics-page">
      <header className="header analytics-header">
        <div>
          <p className="eyebrow">Risk</p>
          <h1>Risk Management</h1>
          <p className="subtitle">Live risk exposure, delinquency staging, and collections pipeline.</p>
        </div>
        <Link className="back-link" to="/">
          Back to dashboard
        </Link>
      </header>

      <main className="main analytics-main">
        <section className="analytics-grid">
          <article className="analytics-metric-card">
            <p className="metric-label">Total PAR</p>
            <h2>{parSummary ? `${parSummary.total_par.toFixed(1)}%` : '...'}</h2>
            <p>Portfolio-at-risk overall ratio.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">NPL Ratio</p>
            <h2>{nplSummary ? `${nplSummary.npl_ratio.toFixed(1)}%` : '...'}</h2>
            <p>Current non-performing loan share.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">NPL Count</p>
            <h2>{nplSummary?.npl_count ?? '...'}</h2>
            <p>Total delinquent accounts.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Recovered</p>
            <h2>{collections ? collections.total_recovered.toLocaleString() : '...'}</h2>
            <p>Total value recovered in pipeline.</p>
          </article>
        </section>

        {error && <p className="status-text">{error}</p>}

        <section className="status-card analytics-detail-card">
          <h2>NPL by stage</h2>
          <div className="live-table-wrap">
            <table className="live-table">
              <thead>
                <tr>
                  <th>Stage</th>
                  <th>Count</th>
                  <th>Amount</th>
                  <th>Share %</th>
                  <th>Intensity</th>
                </tr>
              </thead>
              <tbody>
                {stageData?.stages?.map((stage) => (
                  <tr key={stage.stage}>
                    <td>{stage.stage}</td>
                    <td>{stage.count}</td>
                    <td>{stage.amount.toLocaleString()}</td>
                    <td>{stage.percentage.toFixed(1)}%</td>
                    <td>
                      <div className="bar-track">
                        <span
                          className="bar-fill"
                          style={{ width: `${Math.max((stage.percentage / maxStagePct) * 100, 8)}%` }}
                        />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="status-card analytics-detail-card">
          <h2>Collections pipeline</h2>
          <div className="mini-chart-grid">
            {collections?.pipeline?.map((item) => (
              <div key={item.stage} className="mini-chart-item">
                <span>{item.stage}</span>
                <strong>{item.count}</strong>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}

export default RiskManagementPage
