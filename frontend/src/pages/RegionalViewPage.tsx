import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import type { LatLngBoundsExpression } from 'leaflet'
import { CircleMarker, MapContainer, Polygon, TileLayer, Tooltip, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { fetchAuthJson } from '../services/api'

type Heatmap = {
  regions: Array<{
    name: string
    par: number
    npl_ratio: number
    risk_level: string
    accounts: number
    portfolio: number
  }>
}

type RiskZones = {
  zones: Array<{ zone: string; par_range: string; regions: string[]; accounts: number }>
}

type MapData = {
  country: string
  source: string
  point_count: number
  points: Array<{
    name: string
    country: string
    lat: number
    lng: number
    accounts: number
    portfolio: number
    par: number
    npl_ratio: number
    risk_level: string
  }>
}

type GeoCoord = { lng: number; lat: number }

const COUNTRY_OUTLINES: Record<string, GeoCoord[]> = {
  ethiopia: [
    { lng: 33.0, lat: 14.9 },
    { lng: 35.2, lat: 14.4 },
    { lng: 37.2, lat: 14.8 },
    { lng: 39.4, lat: 14.5 },
    { lng: 41.8, lat: 13.9 },
    { lng: 43.0, lat: 12.2 },
    { lng: 43.2, lat: 10.7 },
    { lng: 43.3, lat: 8.6 },
    { lng: 42.8, lat: 6.5 },
    { lng: 41.8, lat: 4.9 },
    { lng: 40.2, lat: 3.5 },
    { lng: 38.8, lat: 3.4 },
    { lng: 36.8, lat: 4.3 },
    { lng: 35.1, lat: 4.4 },
    { lng: 34.1, lat: 5.6 },
    { lng: 34.0, lat: 7.9 },
    { lng: 34.2, lat: 10.0 },
    { lng: 34.1, lat: 12.0 },
    { lng: 33.0, lat: 14.9 },
  ],
}

const getCountryOutline = (country: string): GeoCoord[] => {
  const key = country.trim().toLowerCase()
  return COUNTRY_OUTLINES[key] ?? []
}

const FALLBACK_MAP_DATA: MapData = {
  country: 'Ethiopia',
  source: 'fallback',
  point_count: 6,
  points: [
    { name: 'Addis Ababa', country: 'Ethiopia', lat: 8.9806, lng: 38.7578, accounts: 1860, portfolio: 3250000000, par: 7.8, npl_ratio: 2.4, risk_level: 'low' },
    { name: 'Oromia', country: 'Ethiopia', lat: 8.7347, lng: 39.2923, accounts: 2410, portfolio: 2980000000, par: 11.4, npl_ratio: 3.5, risk_level: 'high' },
    { name: 'Amhara', country: 'Ethiopia', lat: 11.592, lng: 37.3881, accounts: 1640, portfolio: 2070000000, par: 10.8, npl_ratio: 3.2, risk_level: 'medium' },
    { name: 'Sidama', country: 'Ethiopia', lat: 6.957, lng: 38.4764, accounts: 980, portfolio: 1310000000, par: 9.7, npl_ratio: 2.9, risk_level: 'medium' },
    { name: 'Tigray', country: 'Ethiopia', lat: 13.4969, lng: 39.4753, accounts: 870, portfolio: 1040000000, par: 13.1, npl_ratio: 4.4, risk_level: 'high' },
    { name: 'Dire Dawa', country: 'Ethiopia', lat: 9.6009, lng: 41.8501, accounts: 690, portfolio: 920000000, par: 10.2, npl_ratio: 3.1, risk_level: 'medium' },
  ],
}

const riskColor = (riskLevel: string) => {
  const level = String(riskLevel ?? '').toLowerCase()
  if (level === 'high') {
    return '#c81e1e'
  }
  if (level === 'medium') {
    return '#d97706'
  }
  return '#0f766e'
}

const toFiniteNumber = (value: unknown, fallback = 0): number => {
  const parsed = typeof value === 'number' ? value : Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

function FitMapToBounds({ bounds }: { bounds: LatLngBoundsExpression }) {
  const map = useMap()

  useEffect(() => {
    map.fitBounds(bounds, { padding: [28, 28], maxZoom: 8 })
  }, [bounds, map])

  return null
}

function RegionalViewPage() {
  const [heatmap, setHeatmap] = useState<Heatmap | null>(null)
  const [zones, setZones] = useState<RiskZones | null>(null)
  const [mapData, setMapData] = useState<MapData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [mapError, setMapError] = useState<string | null>(null)

  useEffect(() => {
    Promise.allSettled([
      fetchAuthJson<Heatmap>('/regional/heatmap'),
      fetchAuthJson<RiskZones>('/regional/risk-zones'),
    ]).then(([heatmapResult, zoneResult]) => {
      if (heatmapResult.status === 'fulfilled') {
        setHeatmap(heatmapResult.value)
      }

      if (zoneResult.status === 'fulfilled') {
        setZones(zoneResult.value)
      }

      if (heatmapResult.status === 'rejected' && zoneResult.status === 'rejected') {
        const reason = heatmapResult.reason ?? zoneResult.reason
        setError(String(reason instanceof Error ? reason.message : reason))
      }
    })

    fetchAuthJson<MapData>('/regional/map-data')
      .then((payload) => {
        setMapData(payload)
        setMapError(null)
      })
      .catch((err) => setMapError(String(err instanceof Error ? err.message : err)))
  }, [])

  const maxPar = useMemo(() => {
    if (!heatmap?.regions?.length) {
      return 1
    }
    return Math.max(...heatmap.regions.map((item) => item.par), 1)
  }, [heatmap])

  const highRiskCount = heatmap?.regions?.filter((item) => item.risk_level === 'high').length ?? 0
  const totalAccounts = heatmap?.regions?.reduce((sum, item) => sum + item.accounts, 0) ?? 0

  const effectiveMapData = useMemo(() => {
    if (mapData?.points?.length) {
      return mapData
    }
    return FALLBACK_MAP_DATA
  }, [mapData])

  const countryOutline = useMemo(() => getCountryOutline(effectiveMapData.country), [effectiveMapData.country])

  const normalizedPoints = useMemo(() => {
    return effectiveMapData.points
      .map((point) => {
        const lat = toFiniteNumber(point.lat, 0)
        const lng = toFiniteNumber(point.lng, 0)
        const accounts = Math.max(0, toFiniteNumber(point.accounts, 0))
        const par = toFiniteNumber(point.par, 0)

        if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
          return null
        }

        return {
          ...point,
          lat,
          lng,
          accounts,
          par,
          color: riskColor(point.risk_level),
        }
      })
      .filter((point): point is NonNullable<typeof point> => point !== null)
  }, [effectiveMapData.points])

  const countryOutlinePositions = useMemo(() => {
    return countryOutline
      .map((coord) => [toFiniteNumber(coord.lat, 0), toFiniteNumber(coord.lng, 0)] as [number, number])
      .filter((coord) => Number.isFinite(coord[0]) && Number.isFinite(coord[1]))
  }, [countryOutline])

  const mapCenter = useMemo<[number, number]>(() => {
    if (!normalizedPoints.length) {
      return [9.145, 40.4897]
    }
    const latAvg = normalizedPoints.reduce((sum, point) => sum + point.lat, 0) / normalizedPoints.length
    const lngAvg = normalizedPoints.reduce((sum, point) => sum + point.lng, 0) / normalizedPoints.length
    return [latAvg, lngAvg]
  }, [normalizedPoints])

  const mapBounds = useMemo<LatLngBoundsExpression>(() => {
    const positions: [number, number][] = [
      ...normalizedPoints.map((point) => [point.lat, point.lng] as [number, number]),
      ...countryOutlinePositions,
    ]

    if (positions.length === 0) {
      return [[6.5, 34.0], [14.8, 43.3]]
    }

    if (positions.length === 1) {
      const lat = positions[0][0]
      const lng = positions[0][1]
      return [[lat - 1.2, lng - 1.2], [lat + 1.2, lng + 1.2]]
    }

    return positions
  }, [countryOutlinePositions, normalizedPoints])

  return (
    <div className="container analytics-page">
      <header className="header analytics-header">
        <div>
          <p className="eyebrow">Geography</p>
          <h1>Regional View</h1>
          <p className="subtitle">Live regional risk heatmap and zone segmentation.</p>
        </div>
        <Link className="back-link" to="/">
          Back to dashboard
        </Link>
      </header>

      <main className="main analytics-main">
        <section className="analytics-grid">
          <article className="analytics-metric-card">
            <p className="metric-label">Regions</p>
            <h2>{heatmap?.regions?.length ?? '...'}</h2>
            <p>Regions currently evaluated.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">High-Risk Regions</p>
            <h2>{highRiskCount}</h2>
            <p>Regions tagged as high risk.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Total Accounts</p>
            <h2>{totalAccounts || '...'}</h2>
            <p>Borrower accounts represented.</p>
          </article>
          <article className="analytics-metric-card">
            <p className="metric-label">Risk Zones</p>
            <h2>{zones?.zones?.length ?? '...'}</h2>
            <p>Risk-segmentation buckets.</p>
          </article>
        </section>

        {error && <p className="status-text">{error}</p>}

        <section className="status-card analytics-detail-card">
          <h2>Country map</h2>
          <p className="status-text">
            Showing map points for <strong>{effectiveMapData.country}</strong> ({effectiveMapData.source} data).
          </p>

          <div className="map-summary-strip">
            <div className="mini-chart-item">
              <span>Detected country</span>
              <strong>{effectiveMapData.country}</strong>
            </div>
            <div className="mini-chart-item">
              <span>Map points</span>
              <strong>{effectiveMapData.point_count}</strong>
            </div>
            <div className="mini-chart-item">
              <span>Source</span>
              <strong>{effectiveMapData.source}</strong>
            </div>
          </div>

          <div className="geo-map-wrap">
            <MapContainer className="geo-leaflet-map" center={mapCenter} zoom={6} scrollWheelZoom>
              <TileLayer
                attribution="&copy; OpenStreetMap contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <FitMapToBounds bounds={mapBounds} />
              {countryOutlinePositions.length > 2 && (
                <Polygon
                  positions={countryOutlinePositions}
                  pathOptions={{
                    color: '#0f4c81',
                    weight: 2,
                    fillColor: '#0f4c81',
                    fillOpacity: 0.15,
                  }}
                />
              )}

              {normalizedPoints.map((point) => (
                <CircleMarker
                  key={`${point.country}-${point.name}`}
                  center={[point.lat, point.lng]}
                  radius={Math.min(14, Math.max(5, Math.sqrt(point.accounts) / 3.6))}
                  pathOptions={{
                    color: '#1f2937',
                    weight: 1,
                    fillColor: point.color,
                    fillOpacity: 0.9,
                  }}
                >
                  <Tooltip direction="top" offset={[0, -8]} opacity={0.95}>
                    <div>
                      <strong>{point.name}</strong>
                      <br />
                      PAR: {point.par.toFixed(1)}% | Accounts: {point.accounts}
                    </div>
                  </Tooltip>
                </CircleMarker>
              ))}
            </MapContainer>
          </div>

          {mapError && <p className="status-text">Map data unavailable: {mapError}</p>}
          {!mapData?.points?.length && (
            <p className="status-text">Live map data is unavailable; showing fallback map points.</p>
          )}
          <p className="status-text">Interactive map: zoom and pan enabled, hover points for branch details.</p>
        </section>

        <section className="status-card analytics-detail-card">
          <h2>Regional heatmap table</h2>
          <div className="live-table-wrap">
            <table className="live-table">
              <thead>
                <tr>
                  <th>Region</th>
                  <th>Risk</th>
                  <th>PAR %</th>
                  <th>NPL %</th>
                  <th>Accounts</th>
                  <th>Intensity</th>
                </tr>
              </thead>
              <tbody>
                {heatmap?.regions?.map((region) => (
                  <tr key={region.name}>
                    <td>{region.name}</td>
                    <td>{region.risk_level}</td>
                    <td>{region.par.toFixed(1)}%</td>
                    <td>{region.npl_ratio.toFixed(1)}%</td>
                    <td>{region.accounts}</td>
                    <td>
                      <div className="bar-track">
                        <span
                          className="bar-fill"
                          style={{ width: `${Math.max((region.par / maxPar) * 100, 8)}%` }}
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
          <h2>Risk zones</h2>
          <div className="mini-chart-grid">
            {zones?.zones?.map((zone) => (
              <div key={zone.zone} className="mini-chart-item">
                <span>{zone.zone}</span>
                <strong>{zone.accounts}</strong>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}

export default RegionalViewPage
