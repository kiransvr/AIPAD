import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchAuthJson } from '../services/api'

type OfficerSummary = {
  officers: Array<{
    id: number
    name: string
    branch: string
    portfolio: number
    accounts: number
    par: number
    recovery_rate: number
  }>
  total_officers: number
  average_portfolio_size: number
  average_par: number
}

type OfficerLeaderboard = {
  leaderboard: Array<{
    rank: number
    name: string
    accounts: number
    recovery_rate: number
    npl_ratio: number
    score: number
  }>
}

function OfficerDashboardPage() {
  const [summary, setSummary] = useState<OfficerSummary | null>(null)
  const [leaderboard, setLeaderboard] = useState<OfficerLeaderboard | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      fetchAuthJson<OfficerSummary>('/officers/summary'),
      fetchAuthJson<OfficerLeaderboard>('/officers/leaderboard/productivity'),
    ])
      .then(([summaryData, leaderboardData]) => {
        setSummary(summaryData)
        setLeaderboard(leaderboardData)
      })
      .catch((err) => setError(String(err instanceof Error ? err.message : err)))
  }, [])

  return (
    <div className="container analytics-page">
      <header className="header analytics-header">
        <div>
          <p className="eyebrow">Operations</p>
          <h1>Officer Dashboard</h1>
          <p className="subtitle">Live productivity, quality, and portfolio load per officer.</p>
        </div>
        <Link className="back-link" to="/">
          Back to dashboard
        </Link>
      </header>

      <main className="main analytics-main">
        <section className="analytics-grid">
          <article className="analytics-metric-card">
            <p className="metric-label">Active Officers</p>
            <h2>{summary?.total_officers ?? '...'}</h2>
            <p>Officers tracked by the platform.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Average Portfolio</p>
            <h2>{summary ? summary.average_portfolio_size.toLocaleString() : '...'}</h2>
            <p>Average managed book per officer.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Average PAR</p>
            <h2>{summary ? `${summary.average_par.toFixed(1)}%` : '...'}</h2>
            <p>Average risk exposure by officer portfolio.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Top Score</p>
            <h2>{leaderboard?.leaderboard?.[0]?.score ?? '...'}</h2>
            <p>Current productivity leader score.</p>
          </article>
        </section>

        {error && <p className="status-text">{error}</p>}

        <section className="status-card analytics-detail-card">
          <h2>Officer summary</h2>
          <div className="live-table-wrap">
            <table className="live-table">
              <thead>
                <tr>
                  <th>Officer</th>
                  <th>Branch</th>
                  <th>Accounts</th>
                  <th>Portfolio</th>
                  <th>PAR %</th>
                  <th>Recovery %</th>
                </tr>
              </thead>
              <tbody>
                {summary?.officers?.map((officer) => (
                  <tr key={officer.id}>
                    <td>{officer.name}</td>
                    <td>{officer.branch}</td>
                    <td>{officer.accounts}</td>
                    <td>{officer.portfolio.toLocaleString()}</td>
                    <td>{officer.par.toFixed(1)}%</td>
                    <td>{officer.recovery_rate.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="status-card analytics-detail-card">
          <h2>Productivity leaderboard</h2>
          <div className="mini-chart-grid">
            {leaderboard?.leaderboard?.map((item) => (
              <div key={item.rank} className="mini-chart-item">
                <span>{`#${item.rank} ${item.name}`}</span>
                <strong>{item.score}</strong>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}

export default OfficerDashboardPage
