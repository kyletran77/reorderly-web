import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard.jsx'
import Onboarding from './pages/Onboarding.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/app/" element={<Dashboard />} />
        <Route path="/app/onboarding/" element={<Onboarding />} />
        <Route path="/app" element={<Navigate to="/app/" replace />} />
        <Route path="*" element={<Navigate to="/app/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
