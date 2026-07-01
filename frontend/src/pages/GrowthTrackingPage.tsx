import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchAuthJson } from '../services/api'

type GrowthSummary = {
  ytd_growth: number
  active_accounts: number
  total_portfolio: number
  average_loan_size: number
  new_accounts_month: number
  growth_rate_monthly: number
}

type GrowthTrend = {
  monthly_trend: Array<{ month: string; accounts: number; portfolio: number }>
}

type ProductMix = {
  products: Array<{ name: string; accounts: number; portfolio: number; percentage: number }>
}

function GrowthTrackingPage() {
  const [summary, setSummary] = useState<GrowthSummary | null>(null)
  const [trend, setTrend] = useState<GrowthTrend | null>(null)
  const [mix, setMix] = useState<ProductMix | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      fetchAuthJson<GrowthSummary>('/growth/summary'),
      fetchAuthJson<GrowthTrend>('/growth/trend'),
      fetchAuthJson<ProductMix>('/growth/product-mix'),
    ])
      .then(([summaryData, trendData, mixData]) => {
        setSummary(summaryData)
        setTrend(trendData)
        setMix(mixData)
      })
      .catch((err) => setError(String(err instanceof Error ? err.message : err)))
  }, [])

  const maxProductShare = useMemo(() => {
    if (!mix?.products?.length) {
      return 1
    }
    return Math.max(...mix.products.map((item) => item.percentage), 1)
  }, [mix])

  return (
    <div className="container analytics-page">
      <header className="header analytics-header">
        <div>
          <p className="eyebrow">Performance</p>
          <h1>Growth Tracking</h1>
          <p className="subtitle">Live growth summary, trend evolution, and product-mix exposure.</p>
        </div>
        <Link className="back-link" to="/">
          Back to dashboard
        </Link>
      </header>

      <main className="main analytics-main">
        <section className="analytics-grid">
          <article className="analytics-metric-card">
            <p className="metric-label">YTD Growth</p>
            <h2>{summary ? `${summary.ytd_growth.toFixed(1)}%` : '...'}</h2>
            <p>Year-to-date portfolio expansion.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Active Accounts</p>
            <h2>{summary?.active_accounts ?? '...'}</h2>
            <p>Total active borrower accounts.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Total Portfolio</p>
            <h2>{summary ? summary.total_portfolio.toLocaleString() : '...'}</h2>
            <p>Current outstanding portfolio size.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Monthly Growth</p>
            <h2>{summary ? `${summary.growth_rate_monthly.toFixed(1)}%` : '...'}</h2>
            <p>Current monthly growth rate.</p>
          </article>
        </section>

        {error && <p className="status-text">{error}</p>}

        <section className="status-card analytics-detail-card">
          <h2>Growth trend</h2>
          <div className="mini-chart-grid">
            {trend?.monthly_trend?.map((point) => (
              <div key={point.month} className="mini-chart-item">
                <span>{point.month}</span>
                <strong>{point.accounts}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="status-card analytics-detail-card">
          <h2>Product mix</h2>
          <div className="live-table-wrap">
            <table className="live-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Accounts</th>
                  <th>Portfolio</th>
                  <th>Share %</th>
                  <th>Mix intensity</th>
                </tr>
              </thead>
              <tbody>
                {mix?.products?.map((product) => (
                  <tr key={product.name}>
                    <td>{product.name}</td>
                    <td>{product.accounts}</td>
                    <td>{product.portfolio.toLocaleString()}</td>
                    <td>{product.percentage.toFixed(1)}%</td>
                    <td>
                      <div className="bar-track">
                        <span
                          className="bar-fill"
                          style={{ width: `${Math.max((product.percentage / maxProductShare) * 100, 8)}%` }}
                        />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  )
}

export default GrowthTrackingPage
