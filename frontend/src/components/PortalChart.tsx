import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

import type { PortalCount } from '../types'

const COLORS = ['#38bdf8', '#a78bfa', '#34d399', '#fbbf24', '#fb7185', '#94a3b8']

export default function PortalChart({ data }: { data: PortalCount[] }) {
  const chartData = data.filter((item) => item.count > 0)

  if (chartData.length === 0) {
    return (
      <div className="flex h-72 items-center justify-center text-sm text-slate-500">
        Belum ada data portal lowongan.
      </div>
    )
  }

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            dataKey="count"
            nameKey="portal"
            innerRadius={52}
            outerRadius={84}
            paddingAngle={3}
            stroke="#0f172a"
            strokeWidth={2}
          >
            {chartData.map((entry, index) => (
              <Cell key={entry.portal} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: '#0f172a',
              border: '1px solid #1e293b',
              borderRadius: 10,
              color: '#e2e8f0',
              fontSize: 12,
            }}
          />
          <Legend
            verticalAlign="bottom"
            iconType="circle"
            wrapperStyle={{ color: '#94a3b8', fontSize: 11, paddingTop: 8 }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
