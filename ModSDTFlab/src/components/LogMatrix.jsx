export function LogMatrix({ logs, highlightIndex = -1 }) {
  const levelColors = {
    INFO: 'text-secondary',
    WARN: 'text-tertiary',
    ERROR: 'text-error',
    DEBUG: 'text-text-secondary',
  }
  
  return (
    <div className="bg-surface-inset rounded-lg p-4 font-mono text-xs overflow-auto max-h-64">
      <table className="w-full">
        <tbody>
          {logs.map((log, i) => (
            <tr 
              key={log.id || i} 
              className={`
                ${i % 3 === 0 ? 'bg-white/2' : ''}
                ${i === highlightIndex ? 'bg-primary/20 ring-1 ring-primary' : ''}
              `}
            >
              <td className="text-text-secondary py-0.5 pr-4 whitespace-nowrap">{log.time}</td>
              <td className={`py-0.5 pr-4 ${levelColors[log.level]}`}>{log.level}</td>
              <td className="text-text-primary py-0.5">{log.message}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}