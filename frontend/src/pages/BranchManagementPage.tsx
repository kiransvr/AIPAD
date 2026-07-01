import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchAuthJson } from '../services/api'

type BranchSummary = {
  branches: Array<{
    id: number
    name: string
    manager_name: string
    par: number
    npl_ratio: number
    portfolio: number
    accounts: number
    recovery_rate: number
  }>
  total_portfolio: number
  average_par: number
  average_recovery: number
}

type BranchRanking = {
  ranking: Array<{
    rank: number
    branch: string
    par: number
    recovery_rate: number
    score: number
  }>
}

function BranchManagementPage() {
  const [summary, setSummary] = useState<BranchSummary | null>(null)
  const [ranking, setRanking] = useState<BranchRanking | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      fetchAuthJson<BranchSummary>('/branches/summary'),
      fetchAuthJson<BranchRanking>('/branches/ranking/performance'),
    ])
      .then(([summaryData, rankingData]) => {
        setSummary(summaryData)
        setRanking(rankingData)
      })
      .catch((err) => setError(String(err instanceof Error ? err.message : err)))
  }, [])

  const maxPar = useMemo(() => {
    if (!summary?.branches?.length) {
      return 1
    }
    return Math.max(...summary.branches.map((item) => item.par), 1)
  }, [summary])

  return (
    <div className="container analytics-page">
      <header className="header analytics-header">
        <div>
          <p className="eyebrow">Operations</p>
          <h1>Branch Management</h1>
          <p className="subtitle">Live branch performance and ranking with backend metrics.</p>
        </div>
        <Link className="back-link" to="/">
          Back to dashboard
        </Link>
      </header>

      <main className="main analytics-main">
        <section className="analytics-grid">
          <article className="analytics-metric-card">
            <p className="metric-label">Branch Count</p>
            <h2>{summary?.branches?.length ?? '...'}</h2>
            <p>Branches currently tracked.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Total Portfolio</p>
            <h2>{summary ? summary.total_portfolio.toLocaleString() : '...'}</h2>
            <p>Total book size across branches.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Average PAR</p>
            <h2>{summary ? `${summary.average_par.toFixed(1)}%` : '...'}</h2>
            <p>Average delinquency level.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Recovery Rate</p>
            <h2>{summary ? `${summary.average_recovery.toFixed(1)}%` : '...'}</h2>
            <p>Average branch recovery performance.</p>
          </article>
        </section>

        {error && <p className="status-text">{error}</p>}

        <section className="status-card analytics-detail-card">
          <h2>Branch performance table</h2>
          <div className="live-table-wrap">
            <table className="live-table">
              <thead>
                <tr>
                  <th>Branch</th>
                  <th>Manager</th>
                  <th>Accounts</th>
                  <th>PAR %</th>
                  <th>NPL %</th>
                  <th>Portfolio</th>
                  <th>PAR intensity</th>
                </tr>
              </thead>
              <tbody>
                {summary?.branches?.map((branch) => (
                  <tr key={branch.id}>
                    <td>{branch.name}</td>
                    <td>{branch.manager_name}</td>
                    <td>{branch.accounts}</td>
                    <td>{branch.par.toFixed(1)}%</td>
                    <td>{branch.npl_ratio.toFixed(1)}%</td>
                    <td>{branch.portfolio.toLocaleString()}</td>
                    <td>
                      <div className="bar-track">
                        <span
                          className="bar-fill"
                          style={{ width: `${Math.max((branch.par / maxPar) * 100, 8)}%` }}
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
          <h2>Performance ranking</h2>
          <div className="mini-chart-grid">
            {ranking?.ranking?.map((item) => (
              <div key={item.rank} className="mini-chart-item">
                <span>{`#${item.rank} ${item.branch}`}</span>
                <strong>{item.score}</strong>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}

export default BranchManagementPage
