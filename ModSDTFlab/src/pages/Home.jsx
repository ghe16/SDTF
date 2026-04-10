import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '../components/Card'
import { StatusChip } from '../components/StatusChip'
import { api } from '../api/client'

export default function Home() {
  const [algorithms, setAlgorithms] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    api.getAlgorithms()
      .then(setAlgorithms)
      .catch(err => console.error('Failed to load:', err))
      .finally(() => setLoading(false))
  }, [])
  
  if (loading) {
    return <div className="p-8 text-text-secondary">Loading...</div>
  }
  
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight mb-2">Algorithms</h1>
        <p className="text-text-secondary">Select an algorithm to explore</p>
      </div>
      
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {algorithms.map(algo => (
          <Link key={algo.id} to={`/algorithm?algo=${algo.id}`}>
            <Card className="hover:bg-surface-high transition-colors cursor-pointer h-full">
              <div className="flex items-start justify-between mb-3">
                <h3 className="font-semibold text-text-primary">{algo.name}</h3>
                <StatusChip status={algo.status || 'active'} />
              </div>
              <p className="text-sm text-text-secondary">{algo.description}</p>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}