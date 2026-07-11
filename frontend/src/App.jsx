import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { TrendingUp, TrendingDown, Minus, AlertTriangle, CheckCircle, Activity } from 'lucide-react'
import { getCompare, getChanges, getPositioning, getChangesSummary } from './api'



const fmt = (n) => n ? `Rs ${Number(n).toLocaleString()}` : '—'

const severityColor = {
  critical: 'bg-red-100 text-red-700 border-red-200',
  high:     'bg-orange-100 text-orange-700 border-orange-200',
  medium:   'bg-yellow-100 text-yellow-700 border-yellow-200',
  low:      'bg-green-100 text-green-700 border-green-200',
}

const positionIcon = (pos) => {
  if (pos === 'worldlink_cheaper')  return <TrendingDown className="text-green-500" size={16} />
  if (pos === 'competitor_cheaper') return <TrendingUp className="text-red-500" size={16} />
  if (pos === 'no_worldlink_plan')  return <Minus className="text-gray-400" size={16} />
  return null
}



function StatCard({ label, value, sub, color = 'blue' }) {
  const colors = {
    blue:   'border-blue-200 bg-blue-50',
    green:  'border-green-200 bg-green-50',
    red:    'border-red-200 bg-red-50',
    orange: 'border-orange-200 bg-orange-50',
  }
  return (
    <div className={`rounded-xl border p-5 ${colors[color]}`}>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}


function PositioningChart({ data }) {
  const chartData = data.map(r => ({
    name: `${r.download_mbps} Mbps\n${r.isp_name.replace(' Communications','').replace(' Fibernet','')}`,
    competitor: r.competitor_cheapest,
    worldlink:  r.worldlink_price || 0,
    position:   r.position,
  }))

  return (
    <div className="bg-white rounded-xl border p-5">
      <h2 className="font-semibold text-gray-800 mb-4">Price Comparison by Speed Tier(per_monthly)</h2>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 60 }}>
          <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-30} textAnchor="end" interval={0} />
          <YAxis tickFormatter={v => `Rs ${(v/1000).toFixed(0)}k`} tick={{ fontSize: 11 }} />
          <Tooltip formatter={(v) => [`Rs ${Number(v).toLocaleString()}`, '']} />
          <Bar dataKey="worldlink" name="WorldLink" fill="#3b82f6" radius={[4,4,0,0]} />
          <Bar dataKey="competitor" name="Competitor" radius={[4,4,0,0]}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={
                entry.position === 'worldlink_cheaper'  ? '#22c55e' :
                entry.position === 'competitor_cheaper' ? '#ef4444' : '#9ca3af'
              } />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="flex gap-4 mt-2 text-xs text-gray-500">
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-blue-500 inline-block"/>WorldLink</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-green-500 inline-block"/>Competitor (WL cheaper)</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-red-500 inline-block"/>Competitor (cheaper than WL)</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-gray-400 inline-block"/>No WL plan</span>
      </div>
    </div>
  )
}


function CompareTable({ data }) {
  const [filter, setFilter] = useState('')
  const filtered = data.filter(r =>
    !filter || String(r.download_mbps) === filter
  )
  const speeds = [...new Set(data.map(r => r.download_mbps))].sort((a,b) => a-b)

  return (
    <div className="bg-white rounded-xl border p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-gray-800">WorldLink vs Competitors</h2>
        <select
          className="text-sm border rounded px-2 py-1"
          value={filter}
          onChange={e => setFilter(e.target.value)}
        >
          <option value="">All speeds</option>
          {speeds.map(s => <option key={s} value={s}>{s} Mbps</option>)}
        </select>
      </div>
      <div className="overflow-auto max-h-72">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-gray-50">
            <tr className="text-left text-gray-500 text-xs uppercase">
              <th className="pb-2 pr-4">Plan</th>
              <th className="pb-2 pr-4">ISP</th>
              <th className="pb-2 pr-4">Speed</th>
              <th className="pb-2 pr-4">Their price</th>
              <th className="pb-2 pr-4">WL price</th>
              <th className="pb-2">Diff</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {filtered.map(r => (
              <tr key={r.id} className="hover:bg-gray-50">
                <td className="py-2 pr-4 font-medium text-gray-700 max-w-48 truncate">{r.normalized_name}</td>
                <td className="py-2 pr-4 text-gray-500">{r.competitor_name}</td>
                <td className="py-2 pr-4">{r.download_mbps} Mbps</td>
                <td className="py-2 pr-4">{fmt(r.competitor_price)}</td>
                <td className="py-2 pr-4 text-blue-600 font-medium">{fmt(r.worldlink_price)}</td>
                <td className="py-2">
                  {r.price_diff_pct != null ? (
                    <span className={`text-xs font-semibold ${r.price_diff_pct > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {r.price_diff_pct > 0 ? '+' : ''}{r.price_diff_pct}%
                    </span>
                  ) : <span className="text-gray-300">—</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function ChangeFeed({ data }) {
  return (
    <div className="bg-white rounded-xl border p-5">
      <h2 className="font-semibold text-gray-800 mb-4">Recent Changes</h2>
      <div className="space-y-2 max-h-72 overflow-auto">
        {data.length === 0 && (
          <p className="text-sm text-gray-400 text-center py-8">No changes detected yet</p>
        )}
        {data.map(c => (
          <div key={c.id} className={`flex gap-3 p-3 rounded-lg border text-sm ${severityColor[c.severity] || 'bg-gray-50'}`}>
            <AlertTriangle size={14} className="mt-0.5 shrink-0" />
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-semibold">{c.isp_name}</span>
                <span className="text-xs opacity-60">{c.change_type.replace('_',' ')}</span>
              </div>
              <p className="text-xs opacity-80 truncate mt-0.5">{c.summary}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}



function PositioningTable({ data }) {
  return (
    <div className="bg-white rounded-xl border p-5">
      <h2 className="font-semibold text-gray-800 mb-4">Market Positioning</h2>
      <div className="overflow-auto max-h-72">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-gray-50">
            <tr className="text-left text-gray-500 text-xs uppercase">
              <th className="pb-2 pr-4">Speed</th>
              <th className="pb-2 pr-4">Competitor</th>
              <th className="pb-2 pr-4">Their cheapest</th>
              <th className="pb-2 pr-4">WL price</th>
              <th className="pb-2 pr-4">Position</th>
              <th className="pb-2">Diff</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {data.map((r, i) => (
              <tr key={i} className="hover:bg-gray-50">
                <td className="py-2 pr-4 font-medium">{r.download_mbps} Mbps</td>
                <td className="py-2 pr-4 text-gray-500 text-xs">{r.isp_name}</td>
                <td className="py-2 pr-4">{fmt(r.competitor_cheapest)}</td>
                <td className="py-2 pr-4 text-blue-600">{fmt(r.worldlink_price)}</td>
                <td className="py-2 pr-4">
                  <div className="flex items-center gap-1">
                    {positionIcon(r.position)}
                    <span className="text-xs">{r.position.replace(/_/g,' ')}</span>
                  </div>
                </td>
                <td className="py-2">
                  {r.diff_pct != null
                    ? <span className={`text-xs font-semibold ${r.diff_pct > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {r.diff_pct > 0 ? '+' : ''}{r.diff_pct}%
                      </span>
                    : <span className="text-gray-300">—</span>
                  }
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function App() {
  const [compare, setCompare]       = useState([])
  const [changes, setChanges]       = useState([])
  const [positioning, setPositioning] = useState([])
  const [summary, setSummary]       = useState(null)
  const [loading, setLoading]       = useState(true)

  useEffect(() => {
    Promise.all([
      getCompare(),
      getChanges({ days: 30, limit: 30 }),
      getPositioning(),
      getChangesSummary(),
    ]).then(([comp, chg, pos, summ]) => {
      setCompare(comp.data.data)
      setChanges(chg.data.data)
      setPositioning(pos.data.data)
      setSummary({ ...pos.data.summary, changes: summ.data.data })
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-gray-400 flex items-center gap-2">
        <Activity size={20} className="animate-spin" />
        Loading CIP dashboard...
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">WorldLink CIP</h1>
            <p className="text-sm text-gray-500">Competitive Intelligence Platform</p>
          </div>
          <div className="flex items-center gap-2 text-sm text-green-600">
            <CheckCircle size={16} />
            Live data
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* Stats */}
        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              label="Speed tiers tracked"
              value={positioning.length}
              sub="across all ISPs"
              color="blue"
            />
            <StatCard
              label="WL wins"
              value={summary.worldlink_cheaper_count}
              sub={`${summary.worldlink_advantage_pct}% of matched tiers`}
              color="green"
            />
            <StatCard
              label="Coverage gaps"
              value={summary.no_worldlink_coverage_count}
              sub="tiers with no WL plan"
              color="orange"
            />
            <StatCard
              label="Changes (30d)"
              value={changes.length}
              sub="plan additions & updates"
              color="blue"
            />
          </div>
        )}

        {/* Chart */}
        <PositioningChart data={positioning} />

        {/* Two column */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PositioningTable data={positioning} />
          <ChangeFeed data={changes} />
        </div>

        {/* Compare table */}
        <CompareTable data={compare} />
      </div>
    </div>
  )
}