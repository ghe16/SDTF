export function StatusChip({ status }) {
  const styles = {
    active: 'bg-secondary/10 text-secondary',
    leader: 'bg-tertiary/10 text-tertiary',
    inactive: 'bg-surface-high text-text-secondary',
    warning: 'bg-tertiary/10 text-tertiary',
    loading: 'bg-tertiary/10 text-tertiary animate-pulse',
  }
  
  const labels = {
    active: 'Active',
    leader: 'Leader',
    inactive: 'Inactive',
    warning: 'Warning',
    loading: 'Loading',
  }
  
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${styles[status] || styles.inactive}`}>
      {labels[status] || status}
    </span>
  )
}