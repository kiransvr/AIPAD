import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchAuthJson } from '../services/api'

type ParSummary = {
  total_par: number
  par_30: number
  trend: Array<{ month: string; par: number }>
}

type NplSummary = {
  npl_ratio: number
  recovery_rate: number
}

type ParByRegion = {
  regions: Array<{ name: string; par: number; accounts: number; amount: number }>
}

function AnalyticsPage() {
  const [parSummary, setParSummary] = useState<ParSummary | null>(null)
  const [nplSummary, setNplSummary] = useState<NplSummary | null>(null)
  const [regional, setRegional] = useState<ParByRegion | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      fetchAuthJson<ParSummary>('/par/summary'),
      fetchAuthJson<NplSummary>('/npl/summary'),
      fetchAuthJson<ParByRegion>('/par/by-region'),
    ])
      .then(([parData, nplData, regionalData]) => {
        setParSummary(parData)
        setNplSummary(nplData)
        setRegional(regionalData)
      })
      .catch((err) => setError(String(err instanceof Error ? err.message : err)))
  }, [])

  const maxRegionPar = useMemo(() => {
    if (!regional?.regions?.length) {
      return 1
    }
    return Math.max(...regional.regions.map((item) => item.par), 1)
  }, [regional])

  return (
    <div className="container analytics-page">
      <header className="header analytics-header">
        <div>
          <p className="eyebrow">Analytics</p>
          <h1>Portfolio Intelligence</h1>
          <p className="subtitle">Live PAR and NPL analytics powered by backend endpoints.</p>
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
            <p>Overall portfolio-at-risk ratio.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">PAR 30</p>
            <h2>{parSummary ? `${parSummary.par_30.toFixed(1)}%` : '...'}</h2>
            <p>Early delinquency segment.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">NPL Ratio</p>
            <h2>{nplSummary ? `${nplSummary.npl_ratio.toFixed(1)}%` : '...'}</h2>
            <p>Non-performing portfolio ratio.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Recovery Rate</p>
            <h2>{nplSummary ? `${nplSummary.recovery_rate.toFixed(1)}%` : '...'}</h2>
            <p>Current reported recovery performance.</p>
          </article>
        </section>

        {error && <p className="status-text">{error}</p>}

        <section className="status-card analytics-detail-card">
          <h2>PAR by region</h2>
          <div className="live-table-wrap">
            <table className="live-table">
              <thead>
                <tr>
                  <th>Region</th>
                  <th>PAR %</th>
                  <th>Accounts</th>
                  <th>Portfolio</th>
                  <th>Relative Risk</th>
                </tr>
              </thead>
              <tbody>
                {regional?.regions?.map((region) => (
                  <tr key={region.name}>
                    <td>{region.name}</td>
                    <td>{region.par.toFixed(1)}%</td>
                    <td>{region.accounts}</td>
                    <td>{region.amount.toLocaleString()}</td>
                    <td>
                      <div className="bar-track">
                        <span
                          className="bar-fill"
                          style={{ width: `${Math.max((region.par / maxRegionPar) * 100, 8)}%` }}
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
          <h2>PAR trend snapshot</h2>
          <div className="mini-chart-grid">
            {parSummary?.trend?.map((point) => (
              <div key={point.month} className="mini-chart-item">
                <span>{point.month}</span>
                <strong>{point.par.toFixed(1)}%</strong>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}

export default AnalyticsPage
