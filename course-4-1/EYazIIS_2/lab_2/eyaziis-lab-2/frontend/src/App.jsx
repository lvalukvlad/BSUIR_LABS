import { NavLink, Route, Routes } from 'react-router-dom'
import RecognitionPage from './pages/RecognitionPage.jsx'
import DocumentsPage from './pages/DocumentsPage.jsx'
import DocumentPage from './pages/DocumentPage.jsx'
import MetricsPage from './pages/MetricsPage.jsx'
import HelpPage from './pages/HelpPage.jsx'

const links = [
  { to: '/', label: 'Распознавание', end: true },
  { to: '/documents', label: 'Документы' },
  { to: '/metrics', label: 'Оценка качества' },
  { to: '/help', label: 'Справка' },
]

export default function App() {
  return (
    <div className="layout">
      <header className="masthead">
        <div>
          <h1>Распознавание языка текста</h1>
          <p>Определение русского и немецкого языков по PDF-документам</p>
        </div>
      </header>
      <nav className="nav">
        {links.map((link) => (
          <NavLink key={link.to} to={link.to} end={link.end} className={({ isActive }) => (isActive ? 'active' : '')}>
            {link.label}
          </NavLink>
        ))}
      </nav>
      <Routes>
        <Route path="/" element={<RecognitionPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/documents/:id" element={<DocumentPage />} />
        <Route path="/metrics" element={<MetricsPage />} />
        <Route path="/help" element={<HelpPage />} />
      </Routes>
    </div>
  )
}
