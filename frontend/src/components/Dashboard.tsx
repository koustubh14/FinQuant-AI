import type { ReactNode } from 'react'
import type { Analysis } from '../types'
import { modelName, num, pct, safeUrl } from '../utils'
import { Chart } from './Charts'
export function Panel({id, title, eyebrow, aside, children}: {id?: string; title: string; eyebrow: string; aside?: ReactNode; children: ReactNode}) {
  return <section className="panel" id={id}><div className="panel-head"><div><p className="eyebrow">{eyebrow}</p><h2>{title}</h2></div>{aside}</div>{children}</section>
}
function Metric({label, value, note}: {label: string; value: string; note: string}) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong><small>{note}</small></div>
}
export function Dashboard({data: d}: {data: Analysis}) {
  const c = d.company, f = d.forecast, r = d.recommendation
  const last = d.history[d.history.length - 1]
  const forecastRows = [
    ...d.history.slice(-90).map(p => ({date: p.date, historical: p.adjusted_close, forecast: p.date === last.date ? p.adjusted_close : null})),
    ...f.predictions.map(p => ({date: p.date, historical: null, forecast: p.value})),
  ]
  const download = () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify(d, null, 2)], {type: 'application/json'}))
    const a = document.createElement('a'); a.href = url; a.download = `finquant-${c.symbol}-${d.analysis_id}.json`; a.click(); URL.revokeObjectURL(url)
  }
  return <div className="dashboard">
    <section className="company-head" id="overview">
      <div><p className="eyebrow">{c.exchange || 'Exchange unavailable'} / {c.currency || 'Currency unavailable'} / {c.sector || 'Sector unavailable'}</p>
        <h1>{c.name} <span>{c.symbol}</span></h1>
        <p>Equity research · {d.quality.start} — {d.quality.end} · {d.quality.rows} observed sessions</p></div>
      <div className="quote"><small>Latest available close · {c.currency || 'currency unknown'}</small><strong>{num(c.latest_close)}</strong>
        <span className={c.daily_change >= 0 ? 'positive' : 'negative'}>{c.daily_change >= 0 ? '+' : ''}{pct(c.daily_change)} daily raw close change</span></div>
    </section>
    <div className="run-bar"><span><i className="status-dot" />Generated {new Date(d.generated_at).toLocaleString()} · {d.provenance.source}</span>
      <button className="text-button" onClick={download}>Download run JSON ↓</button></div>
    {d.warnings.length > 0 ? <details className="notice"><summary>{d.warnings.length} data notes · review quality and availability</summary><ul>{d.warnings.map((w, i) => <li key={i}>{w}</li>)}</ul></details> : null}
    <div className="metrics-grid">
      <Metric label="Annualized return" value={pct(d.returns.annualized_return)} note="Geometric · adjusted close" />
      <Metric label="Annualized volatility" value={pct(d.returns.annualized_volatility)} note="Sample SD × square root of 252" />
      <Metric label="Sharpe ratio" value={num(d.risk.sharpe)} note={`Risk-free rate ${pct(d.parameters.annual_risk_free)}`} />
      <Metric label="Sortino ratio" value={num(d.risk.sortino)} note="All-observation downside" />
      <Metric label="Market beta" value={num(d.benchmark?.beta)} note={d.benchmark?.symbol || 'Benchmark unavailable'} />
      <Metric label="Maximum drawdown" value={pct(d.risk.maximum_drawdown)} note="Peak-to-trough · period" />
      <Metric label="Historical VaR · 95%" value={pct(d.risk.historical_var_95)} note="One session · loss fraction" />
      <Metric label="Expected shortfall" value={pct(d.risk.expected_shortfall_95)} note="Mean loss in empirical tail" />
    </div>
    <div className="primary-grid">
      <Panel title="Price & trend" eyebrow="01 / Market overview" aside={<span className="tag">Daily adjusted close</span>}>
        <Chart label="Adjusted price history and 20-session moving average" data={d.history.map(p => ({...p}))}
          series={[{key:'adjusted_close',name:'Adjusted close',color:'#157e80',type:'area'},{key:'moving_average',name:'20-session mean',color:'#c28c36'}]} />
        <div className="inline-stats"><span>Period return <b>{pct(d.returns.total_return)}</b></span><span>Last volume <b>{num(last.volume,0)}</b></span>
          <span>20-session return <b>{pct(last.rolling_return)}</b></span></div>
      </Panel>
      <Panel id="recommendation" title="Quantitative engine output" eyebrow="02 / Deterministic decision">
        <div className="decision"><strong className={r.action === 'BUY' ? 'positive' : r.action === 'SELL' ? 'negative' : ''}>{r.action}</strong>
          <div><b>{pct(r.signal_agreement)}</b><span>signal agreement</span></div></div>
        <p className="muted small">Agreement is not a probability of investment success.</p>
        <div className="signals">{r.signals.map(s => <div key={s.name} title={s.evidence}><span>{s.name}</span>
          <b className={s.score === 1 ? 'positive' : s.score === -1 ? 'negative' : ''}>{s.score == null ? 'Unavailable' : s.score > 0 ? '+1 Positive' : s.score < 0 ? '−1 Negative' : '0 Neutral'}</b></div>)}</div>
        <p className="small muted">Composite score {num(r.score)} · Python rules · unbacktested heuristic</p>
        <details><summary>Inspect decision evidence</summary><p>{r.explanation}</p>{r.signals.map(s => <p key={s.name}><b>{s.name}:</b> {s.evidence}</p>)}</details>
      </Panel>
    </div>
    <div className="two-grid">
      <Panel title="Benchmark-relative performance" eyebrow="03 / Market relationship">
        {d.benchmark ? <><Chart label="Asset and benchmark cumulative returns on aligned dates" percent data={d.benchmark.series}
          series={[{key:'asset',name:c.symbol,color:'#157e80'},{key:'benchmark',name:d.benchmark.symbol,color:'#8391a5'}]} />
          <div className="inline-stats"><span>Relative return <b>{pct(d.benchmark.relative_return)}</b></span><span>Correlation <b>{num(d.benchmark.correlation)}</b></span></div>
          <p className="small muted">{d.benchmark.methodology}</p></> : <p>Benchmark data unavailable. Absolute risk and return results remain available.</p>}
      </Panel>
      <Panel title="Trading volume" eyebrow="04 / Participation">
        <Chart label="Observed daily trading volume" data={d.history.slice(-120).map(p => ({date:p.date,volume:p.volume}))}
          series={[{key:'volume',name:'Volume · last 120 sessions',color:'#93a7b9',type:'bar'}]} />
        <p className="small muted">Provider-reported volume. Zero-volume sessions are disclosed in data quality notes.</p>
      </Panel>
    </div>
    <div className="two-grid" id="risk">
      <Panel title="Drawdown & downside risk" eyebrow="05 / Risk analytics" aside={<span className="tag">{d.risk.level} realized volatility</span>}>
        <Chart label="Historical drawdown from running peak" percent data={d.history.map(p => ({date:p.date,drawdown:p.drawdown}))}
          series={[{key:'drawdown',name:'Underwater return',color:'#b95151',type:'area'}]} />
        <div className="inline-stats"><span>Downside deviation <b>{pct(d.risk.downside_deviation)}</b></span><span>Normal VaR <b>{pct(d.risk.normal_var_95)}</b></span></div>
        <p className="small muted">Normal VaR assumes Gaussian returns; the historical tail can differ substantially.</p>
        <ul className="small">{r.risk_factors.map(x => <li key={x}>{x}</li>)}</ul>
      </Panel>
      <Panel title="Volatility through time" eyebrow="06 / Rolling statistics">
        <Chart label="20-session annualized rolling volatility" percent data={d.history.map(p => ({date:p.date,volatility:p.rolling_volatility}))}
          series={[{key:'volatility',name:'20-session volatility · annualized',color:'#527697',type:'area'}]} />
        <p className="small muted">Realized volatility measures dispersion, not a complete view of risk. A 20-session window responds to recent shocks.</p>
      </Panel>
    </div>
    <div className="two-grid" id="statistics">
      <Panel title="Return distribution" eyebrow="07 / Applied statistics">
        <Chart label="Histogram of daily adjusted simple returns" xKey="return" data={d.statistics.histogram}
          series={[{key:'count',name:'Observed session count',color:'#4d9293',type:'bar'}]} />
        <div className="inline-stats"><span>Skewness <b>{num(d.statistics.skewness)}</b></span><span>Excess kurtosis <b>{num(d.statistics.excess_kurtosis)}</b></span></div>
      </Panel>
      <Panel title="Distribution diagnostics" eyebrow="08 / Assumptions under scrutiny">
        <dl className="data-list"><div><dt>Daily mean / median</dt><dd>{pct(d.statistics.mean)} / {pct(d.statistics.median)}</dd></div>
          <div><dt>Daily standard deviation</dt><dd>{pct(d.statistics.standard_deviation)}</dd></div>
          <div><dt>Daily variance</dt><dd>{num(d.statistics.variance,6)}</dd></div>
          <div><dt>Lag-one autocorrelation</dt><dd>{num(d.statistics.autocorrelation_lag1,3)}</dd></div>
          <div><dt>{d.statistics.normality.name} statistic</dt><dd>{num(d.statistics.normality.statistic,4)}</dd></div>
          <div><dt>Normality p-value</dt><dd>{d.statistics.normality.p_value == null ? 'Not run' : d.statistics.normality.p_value.toExponential(3)}</dd></div></dl>
        <p className="callout">{d.statistics.normality.interpretation}</p>
        <p className="small muted">Used to challenge normal-tail assumptions. These diagnostics do not establish predictability or a tradable edge.</p>
      </Panel>
    </div>
    <Panel id="forecast" title="Forecast & out-of-sample evaluation" eyebrow="09 / Time-series research" aside={<span className="tag">{f.horizon} sessions · {modelName(f.selected_model)}</span>}>
      <Chart label="Recent adjusted price history and selected model output" data={forecastRows}
        series={[{key:'historical',name:'Observed adjusted close',color:'#157e80'},{key:'forecast',name:'Estimated model output',color:'#c28c36',dashed:true}]} />
      <div className="forecast-context"><div><span>Selection period</span><b>{f.validation_start} — {f.validation_end}</b></div>
        <div><span>Separate holdout</span><b>{f.holdout_start} — {f.holdout_end}</b></div>
        <div><span>Estimated endpoint</span><b>{num(f.predictions.at(-1)?.value)} {c.currency} adjusted</b></div></div>
      <div className="table-scroll"><table><caption>All candidate models · errors in adjusted-price units · lower is better</caption>
        <thead><tr><th>Model</th><th>Validation RMSE</th><th>Holdout MAE</th><th>Holdout RMSE</th><th>Holdout MAPE</th><th>Direction</th></tr></thead>
        <tbody>{Object.entries(f.models).map(([name,m]) => <tr className={name === f.selected_model ? 'selected' : ''} key={name}>
          <td>{modelName(name)} {name === f.selected_model ? <span className="mini-tag">Selected</span> : null}</td>
          <td>{num(m.validation.rmse,3)}</td><td>{num(m.holdout.mae,3)}</td><td>{num(m.holdout.rmse,3)}</td><td>{pct(m.holdout.mape)}</td><td>{pct(m.holdout.directional_accuracy)}</td></tr>)}</tbody></table></div>
      <p className="callout">{f.selected_model === 'naive' ? 'The naive baseline won validation. No more complex model was selected.' :
        f.selected_beats_naive_holdout ? 'The selected model had lower holdout RMSE than the naive baseline in this run. This is not evidence of a persistent trading edge.' :
        'The selected model did not beat the naive baseline on holdout RMSE. The result is reported without changing selection after the fact.'}</p>
      <p className="small muted">{f.methodology}</p>
      <details><summary>Forecast uncertainty & limitations</summary><ul>{f.limitations.map(x => <li key={x}>{x}</li>)}</ul></details>
    </Panel>
    <div className="two-grid">
      <Panel title="Financial snapshot" eyebrow="10 / Company context">
        <dl className="data-list"><div><dt>Market capitalization</dt><dd>{num(c.market_cap,0)} {c.currency}</dd></div>
          <div><dt>Trailing / forward P/E</dt><dd>{num(c.trailing_pe)} / {num(c.forward_pe)}</dd></div>
          <div><dt>Price / book</dt><dd>{num(c.price_to_book)}</dd></div>
          <div><dt>Revenue growth</dt><dd>{pct(c.revenue_growth)}</dd></div>
          <div><dt>Return on equity</dt><dd>{pct(c.return_on_equity)}</dd></div></dl>
        <p className="small muted">Provider snapshots; unavailable values are shown as —. Ratios are context, not fair-value estimates or recommendation votes.</p>
      </Panel>
      <Panel id="news" title="News & context" eyebrow="11 / External sources">
        {d.news.length ? <div className="news">{d.news.map((n,i) => <article key={i}><small>{n.source || 'Publisher unavailable'} · {n.date?.slice(0,10) || 'Date unavailable'}</small>
          <h3>{safeUrl(n.url) ? <a href={safeUrl(n.url)} target="_blank" rel="noreferrer">{n.headline} ↗</a> : n.headline}</h3>
          {n.summary ? <p>{n.summary.slice(0,350)}{n.summary.length > 350 ? '…' : ''}</p> : null}</article>)}</div> : <p>No news returned by the provider. News availability does not affect quantitative calculations.</p>}
      </Panel>
    </div>
    <Panel id="analyst" title="AI-generated interpretation" eyebrow="12 / Optional analyst" aside={<span className="tag">{d.interpretation.status}</span>}>
      <p className="small muted">Unverified narrative · Python results above remain authoritative · {d.interpretation.model || 'No model call'}</p>
      <p className="narrative">{d.interpretation.text}</p>
    </Panel>
    <Panel id="methodology" title="How this analysis was produced" eyebrow="13 / Provenance & reproducibility">
      <div className="two-grid compact"><dl className="data-list"><div><dt>Source</dt><dd>{d.provenance.source}</dd></div>
        <div><dt>Fetched at</dt><dd>{d.provenance.fetched_at}</dd></div><div><dt>Cache</dt><dd>{d.provenance.cached ? 'Reused provider snapshot' : 'Fresh fetch'}</dd></div>
        <div><dt>Model training</dt><dd>{f.training_start} — {f.training_end}</dd></div>
        <div><dt>Analysis ID</dt><dd className="mono">{d.analysis_id}</dd></div></dl>
        <div><h3>Data handling</h3><p>{d.quality.handling}</p><p>{r.confidence_definition}</p><p className="small muted">Missing weekdays can be exchange holidays. Future dates are weekday estimates. No currency conversion or exchange-calendar correction.</p></div></div>
      <details><summary>Formulas, assumptions & decision rules</summary>
        <p>Simple return: P[t]/P[t-1] - 1. Log return: ln(P[t]/P[t-1]). Annual return: (P[n]/P[0])^(252/n) - 1. Volatility: sample standard deviation times square root of 252.</p>
        <p>Sharpe: mean daily excess return / sample daily volatility times square root of 252. Sortino: annual arithmetic excess return divided by annualized downside deviation over all observations.</p>
        <p>Drawdown: price / running maximum - 1. Historical VaR: 95th percentile of daily losses. Expected shortfall: mean losses at or above that threshold, including ties.</p>
        <p>{r.explanation}</p><ul>{[...d.risk.assumptions,...d.provenance.assumptions].map(x => <li key={x}>{x}</li>)}</ul>
      </details>
      <details><summary>Input fingerprint & software versions</summary><p className="mono wrap">{d.provenance.input_sha256}</p>
        <pre>{JSON.stringify(d.provenance.versions,null,2)}</pre></details>
    </Panel>
    <footer>FinQuant AI · Research software, not personalized financial advice. Model outputs are uncertain; no trading execution.</footer>
  </div>
}
