import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Dashboard } from './components/Dashboard'
import { analyze, loadAnalysis } from './services/api'
import type { Analysis } from './types'
const nav = [['overview','Overview'],['risk','Risk analytics'],['statistics','Statistics'],['forecast','Forecast research'],['recommendation','Decision evidence'],['news','News & context'],['analyst','AI interpretation'],['methodology','Methodology']]
export default function App() {
  const [symbol,setSymbol] = useState('AAPL'), [period,setPeriod] = useState('2y')
  const [horizon,setHorizon] = useState(30), [ai,setAi] = useState(false), [rf,setRf] = useState(0)
  const [result,setResult] = useState<Analysis | null>(null), [loading,setLoading] = useState(false), [error,setError] = useState('')
  useEffect(() => {
    const id = new URLSearchParams(location.search).get('analysis')
    if (!id) return
    let active = true
    setLoading(true)
    loadAnalysis(id).then(data => {if(active) {setResult(data); setSymbol(data.company.symbol); setPeriod(data.parameters.period); setHorizon(data.parameters.forecast_horizon); setRf(data.parameters.annual_risk_free*100)}})
      .catch(e => {if(active) setError(String(e.message))}).finally(() => {if(active) setLoading(false)})
    return () => {active = false}
  }, [])
  async function submit(event: FormEvent) {
    event.preventDefault(); setLoading(true); setError('')
    try {
      const data = await analyze(symbol,period,horizon,ai,rf/100)
      setResult(data)
      history.replaceState(null,'',`?analysis=${data.analysis_id}`)
    } catch(e) {setError(e instanceof Error ? e.message : 'Unable to complete analysis.')}
    finally {setLoading(false)}
  }
  return <div className="app-shell">
    <aside className="sidebar"><a className="brand" href="/"><span className="brand-mark">FQ</span><div>FinQuant <b>AI</b><small>QUANTITATIVE RESEARCH</small></div></a>
      <p className="nav-label">RESEARCH WORKSPACE</p><nav aria-label="Research sections">{nav.map(([id,title],i) => <a key={id} href={`#${id}`}><span>{String(i+1).padStart(2,'0')}</span>{title}</a>)}</nav>
      <div className="sidebar-note"><span className="status-dot" /> Python calculates.<br/>AI explains.<p>Transparent methods.<br/>Measured results.</p></div>
      <a className="api-link" href="/docs" target="_blank" rel="noreferrer">API documentation ↗</a></aside>
    <main><header className="topbar"><div><b>Equity research</b><span> / Analysis workspace</span></div><span className="tag">Research edition · v0.1</span></header>
      <div className="content"><form className="search-panel" onSubmit={submit}>
        <label className="search-field">Company or ticker<input required maxLength={80} value={symbol} onChange={e=>setSymbol(e.target.value)} placeholder="Company or ticker" /></label>
        <label>History<select value={period} onChange={e=>setPeriod(e.target.value)}><option value="1y">1 year</option><option value="2y">2 years</option><option value="5y">5 years</option></select></label>
        <label>Horizon<select value={horizon} onChange={e=>setHorizon(Number(e.target.value))}><option value={5}>5 sessions</option><option value={10}>10 sessions</option><option value={30}>30 sessions</option><option value={60}>60 sessions</option></select></label>
        <label>Risk-free %<input className="rf-input" type="number" min="0" max="30" step=".1" value={rf} onChange={e=>setRf(Number(e.target.value))}/></label>
        <label className="checkbox"><input type="checkbox" checked={ai} onChange={e=>setAi(e.target.checked)} />AI interpretation</label>
        <button className="primary-button" disabled={loading}>{loading ? 'Analyzing…' : 'Run analysis →'}</button>
      </form>
      {error ? <div className="error" role="alert"><b>Analysis could not be completed.</b> {error}{result ? ' The previous run remains displayed below.' : ''}</div> : null}
      {loading ? <div className="loading" role="status">Fetching market history, validating data and evaluating forecasts. This may take up to three minutes.</div> : null}
      {result ? <Dashboard data={result}/> : !loading ? <section className="empty-state"><p className="eyebrow">FINANCE / STATISTICS / MACHINE LEARNING</p><h1>Every signal.<br/>Open to scrutiny.</h1>
        <p>Analyze an equity through its returns, tail risk and forecast evidence. Inspect the data, compare the baselines and trace the decision.</p>
        <div className="empty-columns"><div><span>01</span><h3>Measure the risk</h3><p>Return distributions, drawdowns and expected shortfall.</p></div><div><span>02</span><h3>Test the forecast</h3><p>Chronological validation and an honest naive baseline.</p></div><div><span>03</span><h3>Inspect the reasoning</h3><p>Python-owned decisions with optional AI interpretation.</p></div></div>
        <p className="small muted">Start with AAPL, RELIANCE.NS or a company name. Core analysis needs no LLM key.</p></section> : null}
      </div></main>
  </div>
}
