import { NavLink, Route, Routes } from 'react-router-dom'
import UploadPage from './pages/UploadPage.jsx'
import DocumentsPage from './pages/DocumentsPage.jsx'
import DocumentPage from './pages/DocumentPage.jsx'
import MetricsPage from './pages/MetricsPage.jsx'
import HelpPage from './pages/HelpPage.jsx'

const links = [
  { to: '/', label: 'Реферат', end: true },
  { to: '/documents', label: 'Документы' },
  { to: '/metrics', label: 'Оценка' },
  { to: '/help', label: 'Справка' },
]

export default function App() {
  return (
    <div className="layout">
      <header className="masthead no-print">
        <div>
          <h1>Реферирование</h1>
          <p>вар. 22, русский / немецкий</p>
        </div>
      </header>
      <nav className="nav no-print">
        {links.map((l) => (
          <NavLink key={l.to} to={l.to} end={l.end} className={({ isActive }) => (isActive ? 'active' : '')}>
            {l.label}
          </NavLink>
        ))}
      </nav>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/documents/:id" element={<DocumentPage />} />
        <Route path="/metrics" element={<MetricsPage />} />
        <Route path="/help" element={<HelpPage />} />
      </Routes>
    </div>
  )
}
