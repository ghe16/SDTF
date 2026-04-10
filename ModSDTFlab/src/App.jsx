import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Algorithm from './pages/Algorithm'
import NotFound from './pages/NotFound'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/"          element={<Home />} />
        <Route path="/algorithm" element={<Algorithm />} />
        <Route path="*"          element={<NotFound />} />
      </Route>
    </Routes>
  )
}