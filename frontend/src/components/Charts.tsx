import { Area, Bar, CartesianGrid, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { dateLabel, num, pct } from '../utils'
type ChartRow = Record<string, string | number | null>
interface Series {key: string; name: string; color: string; type?: 'line' | 'area' | 'bar'; dashed?: boolean}
export function Chart({data, series, percent = false, xKey = 'date', height = 280, label}: {
  data: ChartRow[]; series: Series[]; percent?: boolean; xKey?: string; height?: number; label: string;
}) {
  return <figure className="chart" aria-label={label}>
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={data} margin={{left: 0, right: 18, top: 12, bottom: 0}} accessibilityLayer>
        <CartesianGrid stroke="#e6ebef" vertical={false} />
        <XAxis dataKey={xKey} tickLine={false} axisLine={false} minTickGap={48} tick={{fontSize: 11, fill: '#66758a'}}
          tickFormatter={value => xKey === 'date' ? dateLabel(String(value)) : pct(Number(value))} />
        <YAxis tickLine={false} axisLine={false} width={64} tick={{fontSize: 11, fill: '#66758a'}}
          tickFormatter={value => percent ? pct(Number(value)) : num(Number(value), 0)} domain={['auto', 'auto']} />
        <Tooltip contentStyle={{border: '1px solid #d7e0e8', borderRadius: 4, fontSize: 12}}
          formatter={(value, name) => [percent ? pct(Number(value)) : num(Number(value)), name]} />
        {series.map(s => s.type === 'bar'
          ? <Bar key={s.key} dataKey={s.key} name={s.name} fill={s.color} isAnimationActive={false} />
          : s.type === 'area'
          ? <Area key={s.key} dataKey={s.key} name={s.name} stroke={s.color} fill={s.color} fillOpacity={.09} strokeWidth={1.6} isAnimationActive={false} />
          : <Line key={s.key} type="linear" dataKey={s.key} name={s.name} stroke={s.color} strokeWidth={1.8} dot={false}
              strokeDasharray={s.dashed ? '5 4' : undefined} isAnimationActive={false} />)}
      </ComposedChart>
    </ResponsiveContainer>
    <figcaption>{series.map(s => <span key={s.key}><i style={{background: s.color}} />{s.name}</span>)}</figcaption>
  </figure>
}
