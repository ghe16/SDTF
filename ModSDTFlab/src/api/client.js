const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

async function fetchJSON(url, options = {}) {
  const res = await fetch(`${API_URL}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error(`${res.status}`)
  return res.json()
}

export const api = {
  async getAlgorithms() {
    return fetchJSON('/algorithms')
  },
  
  async getAlgorithm(id) {
    return fetchJSON(`/algorithms/${id}`)
  },
  
  async startExecution(algorithm, nodeCount = 5, config = {}, scenario = null) {
    return fetchJSON('/executions/start', {
      method: 'POST',
      body: JSON.stringify({ algorithm, node_count: nodeCount, config, scenario }),
    })
  },
  
  async runExecution(id) {
    return fetchJSON(`/executions/${id}/run`, { method: 'POST' })
  },
  
  async getExecutionState(id) {
    return fetchJSON(`/executions/${id}/state`)
  },
  
  async getExecutionLogs(id) {
    return fetchJSON(`/executions/${id}/logs`)
  },
  
  async getExecutionResult(id) {
    return fetchJSON(`/executions/${id}/result`)
  },
  
  async getExecutionValidation(id) {
    return fetchJSON(`/executions/${id}/validation`)
  },
  
  async listExecutions() {
    return fetchJSON('/executions')
  },
}