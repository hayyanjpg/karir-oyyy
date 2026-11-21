import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import type { StatusCount } from '../types'

export default function StatusChart({ data }: { data: StatusCount[] }) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: -18, bottom: 42 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis
            dataKey="status"
            interval={0}
            angle={-28}
            textAnchor="end"
            height={70}
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            axisLine={{ stroke: '#1e293b' }}
            tickLine={false}
          />
          <YAxis
            allowDecimals={false}
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: 'rgba(56, 189, 248, 0.08)' }}
            contentStyle={{
              background: '#0f172a',
              border: '1px solid #1e293b',
              borderRadius: 10,
              color: '#e2e8f0',
              fontSize: 12,
            }}
          />
          <Bar dataKey="count" name="Lamaran" fill="#38bdf8" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
