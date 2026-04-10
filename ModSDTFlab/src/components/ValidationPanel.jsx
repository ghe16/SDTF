import { Card } from './Card'

export function ValidationPanel({ validation, isRunning }) {
  const validationData = !isRunning ? validation : null
  
  return (
    <Card>
      <h3 className="text-sm font-medium text-text-secondary mb-4">Validation</h3>
      
      {isRunning && (
        <div className="text-text-secondary text-sm">Run execution to see validation</div>
      )}
      
      {!isRunning && !validationData && (
        <div className="text-text-secondary text-sm">No results yet</div>
      )}
      
      {validationData && (
        <div className="space-y-4">
          <div className={`flex items-center gap-2 ${validationData.success ? 'text-secondary' : 'text-error'}`}>
            <span className={`w-3 h-3 rounded-full ${validationData.success ? 'bg-secondary' : 'bg-error'}`}></span>
            <span className="font-medium">{validationData.success ? 'Passed' : 'Failed'}</span>
          </div>
          
          {validationData.explanation && (
            <div className="text-sm text-text-secondary">
              {validationData.explanation}
            </div>
          )}
          
          {validationData.invariants && validationData.invariants.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs text-text-secondary font-medium">Invariants</p>
              {validationData.invariants.map((inv, i) => (
                <div key={i} className={`flex items-center gap-2 text-xs ${inv.holds ? 'text-secondary' : 'text-error'}`}>
                  <span>{inv.holds ? '✓' : '✗'}</span>
                  <span className="text-text-primary">{inv.name}</span>
                  <span className="text-text-secondary">- {inv.description}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </Card>
  )
}