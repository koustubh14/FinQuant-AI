export const num = (value: number | null | undefined, digits = 2) => value == null || !Number.isFinite(value) ? '\u2014' : value.toLocaleString('en-US', {maximumFractionDigits: digits, minimumFractionDigits: digits})
export const pct = (value: number | null | undefined) => value == null || !Number.isFinite(value) ? '\u2014' : `${num(value * 100)}%`
export const modelName = (name: string) => ({naive: 'Naive - last close', moving_average: 'Moving average - 20', ridge_lags: 'Ridge - lagged returns'}[name] || name)
export const dateLabel = (date: string) => date.slice(5)
export const safeUrl = (url: string | null) => url?.startsWith('https://') ? url : undefined
