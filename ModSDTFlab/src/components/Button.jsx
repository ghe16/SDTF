export function Button({ children, variant = 'primary', className = '', ...props }) {
  const base = 'px-4 py-2 rounded-btn font-medium text-sm transition-all duration-200 cursor-pointer'
  const variants = {
    primary: 'bg-primary text-surface-base hover:bg-primary/90',
    ghost: 'border border-primary/20 text-primary hover:bg-primary/10',
    danger: 'bg-error text-surface-base hover:bg-error/90',
  }
  
  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  )
}