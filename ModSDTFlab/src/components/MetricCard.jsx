export function MetricCard({ label, value, unit, trend }) {
  return (
    <div className="p-4 bg-surface-standard rounded-lg">
      <p className="text-text-secondary text-sm mb-1">{label}</p>
      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-semibold text-text-primary tracking-tight">{value}</span>
        {unit && <span className="text-text-secondary text-sm">{unit}</span>}
      </div>
      {trend && (
        <p className={`text-xs mt-2 ${trend > 0 ? 'text-secondary' : 'text-error'}`}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
        </p>
      )}
    </div>
  )
}