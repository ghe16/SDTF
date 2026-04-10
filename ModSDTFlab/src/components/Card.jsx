export function Card({ children, className = '', glass = false }) {
  return (
    <div className={`p-6 ${glass ? 'bg-white/7 backdrop-blur-glass rounded-lg' : 'bg-surface-standard rounded-lg'} ${className}`}>
      {children}
    </div>
  )
}