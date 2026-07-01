import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchAuthJson } from '../services/api'

type InclusionSummary = {
  inclusion_score: number
  active_underserved: number
  rural_percentage: number
  women_entrepreneurs: number
}

type InclusionTrend = {
  trend: Array<{ month: string; score: number }>
  target_score: number
}

type GenderSummary = {
  male_percentage: number
  female_percentage: number
  other_percentage: number
  total_borrowers: number
}

type GenderPerformance = {
  by_gender: Array<{
    gender: string
    par: number
    recovery_rate: number
    npl_ratio: number
    accounts: number
  }>
}

function CompliancePage() {
  const [inclusionSummary, setInclusionSummary] = useState<InclusionSummary | null>(null)
  const [inclusionTrend, setInclusionTrend] = useState<InclusionTrend | null>(null)
  const [genderSummary, setGenderSummary] = useState<GenderSummary | null>(null)
  const [genderPerformance, setGenderPerformance] = useState<GenderPerformance | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      fetchAuthJson<InclusionSummary>('/inclusion/summary'),
      fetchAuthJson<InclusionTrend>('/inclusion/inclusion-index'),
      fetchAuthJson<GenderSummary>('/gender/summary'),
      fetchAuthJson<GenderPerformance>('/gender/performance-comparison'),
    ])
      .then(([inclusionData, trendData, genderData, genderPerfData]) => {
        setInclusionSummary(inclusionData)
        setInclusionTrend(trendData)
        setGenderSummary(genderData)
        setGenderPerformance(genderPerfData)
      })
      .catch((err) => setError(String(err instanceof Error ? err.message : err)))
  }, [])

  const maxPar = useMemo(() => {
    if (!genderPerformance?.by_gender?.length) {
      return 1
    }
    return Math.max(...genderPerformance.by_gender.map((item) => item.par), 1)
  }, [genderPerformance])

  return (
    <div className="container analytics-page">
      <header className="header analytics-header">
        <div>
          <p className="eyebrow">Governance</p>
          <h1>Compliance</h1>
          <p className="subtitle">Live inclusion and fairness indicators for compliance oversight.</p>
        </div>
        <Link className="back-link" to="/">
          Back to dashboard
        </Link>
      </header>

      <main className="main analytics-main">
        <section className="analytics-grid">
          <article className="analytics-metric-card">
            <p className="metric-label">Inclusion Score</p>
            <h2>{inclusionSummary ? inclusionSummary.inclusion_score.toFixed(1) : '...'}</h2>
            <p>Composite inclusion score.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Underserved Active</p>
            <h2>{inclusionSummary?.active_underserved ?? '...'}</h2>
            <p>Active underserved account holders.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Women Entrepreneurs</p>
            <h2>{inclusionSummary ? `${inclusionSummary.women_entrepreneurs.toFixed(1)}%` : '...'}</h2>
            <p>Share of women entrepreneurs.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Total Borrowers</p>
            <h2>{genderSummary?.total_borrowers ?? '...'}</h2>
            <p>Borrowers in gender distribution view.</p>
          </article>
        </section>

        {error && <p className="status-text">{error}</p>}

        <section className="status-card analytics-detail-card">
          <h2>Gender performance comparison</h2>
          <div className="live-table-wrap">
            <table className="live-table">
              <thead>
                <tr>
                  <th>Segment</th>
                  <th>Accounts</th>
                  <th>PAR %</th>
                  <th>NPL %</th>
                  <th>Recovery %</th>
                  <th>PAR intensity</th>
                </tr>
              </thead>
              <tbody>
                {genderPerformance?.by_gender?.map((item) => (
                  <tr key={item.gender}>
                    <td>{item.gender}</td>
                    <td>{item.accounts}</td>
                    <td>{item.par.toFixed(1)}%</td>
                    <td>{item.npl_ratio.toFixed(1)}%</td>
                    <td>{item.recovery_rate.toFixed(1)}%</td>
                    <td>
                      <div className="bar-track">
                        <span
                          className="bar-fill"
                          style={{ width: `${Math.max((item.par / maxPar) * 100, 8)}%` }}
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
          <h2>Inclusion trend</h2>
          <div className="mini-chart-grid">
            {inclusionTrend?.trend?.map((point) => (
              <div key={point.month} className="mini-chart-item">
                <span>{point.month}</span>
                <strong>{point.score.toFixed(1)}</strong>
              </div>
            ))}
            {inclusionTrend && (
              <div className="mini-chart-item">
                <span>Target</span>
                <strong>{inclusionTrend.target_score.toFixed(1)}</strong>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

export default CompliancePage
