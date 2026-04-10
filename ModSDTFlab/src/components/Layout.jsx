import { Outlet, NavLink } from 'react-router-dom'

export default function Layout() {
  const navLink = ({ isActive }) =>
    `px-4 py-2 rounded-btn text-sm font-medium tracking-tight transition-colors
     ${isActive
       ? 'bg-primary/10 text-primary'
       : 'text-text-secondary hover:text-text-primary hover:bg-surface-high'
     }`

  return (
    <div className="flex flex-col h-full min-h-screen bg-surface-base">
      {/* Top Nav */}
      <header className="sticky top-0 z-50 bg-surface-low/70 backdrop-blur-glass border-b border-white/5">
        <nav className="max-w-screen-2xl mx-auto px-6 h-14 flex items-center justify-between">
          {/* Brand */}
          <span className="font-mono text-primary font-medium tracking-tight">
            SDTF<span className="text-text-secondary">Lab</span>
          </span>

          {/* Links */}
          <div className="flex items-center gap-1">
            <NavLink to="/"          className={navLink}>Home</NavLink>
            <NavLink to="/dashboard" className={navLink}>Dashboard</NavLink>
          </div>
        </nav>
      </header>

      {/* Page content */}
      <main className="flex-1 max-w-screen-2xl mx-auto w-full px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}
