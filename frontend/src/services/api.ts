import type { Analysis } from '../types'
async function request(path: string, init?: RequestInit): Promise<Analysis> {
  const response = await fetch(path, {...init, signal: AbortSignal.timeout(180_000)})
  const body = await response.json()
  if (!response.ok) {
    const detail = Array.isArray(body.detail) ? body.detail.map((d: {msg: string}) => d.msg).join('; ') : body.detail
    throw new Error(body.error?.message || detail || `Request failed (${response.status})`)
  }
  return body as Analysis
}
export const analyze = (symbol: string, period: string, forecast_horizon: number, include_ai: boolean, annual_risk_free: number) =>
  request('/api/analyze', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({symbol, period, forecast_horizon, include_ai, annual_risk_free})})
export const loadAnalysis = (id: string) => request(`/api/analysis/${encodeURIComponent(id)}`)
