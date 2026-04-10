// Page: 404 Not Found
import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
      <span className="font-mono text-5xl text-surface-high">404</span>
      <h1 className="text-text-primary text-lg font-medium">Page not found</h1>
      <Link
        to="/"
        className="px-4 py-2 rounded-btn bg-primary text-surface-base text-sm font-semibold hover:opacity-90 transition-opacity"
      >
        Back to Home
      </Link>
    </div>
  )
}
