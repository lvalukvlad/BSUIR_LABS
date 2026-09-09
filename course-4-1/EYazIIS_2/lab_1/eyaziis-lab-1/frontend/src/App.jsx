import { NavLink, Route, Routes } from 'react-router-dom'
import SearchPage from './pages/SearchPage.jsx'
import DocumentsPage from './pages/DocumentsPage.jsx'
import DocumentPage from './pages/DocumentPage.jsx'
import UploadPage from './pages/UploadPage.jsx'
import MetricsPage from './pages/MetricsPage.jsx'
import HelpPage from './pages/HelpPage.jsx'

const links = [
  { to: '/', label: 'Поиск', end: true },
  { to: '/documents', label: 'Документы' },
  { to: '/upload', label: 'Загрузка' },
  { to: '/metrics', label: 'Оценка качества' },
  { to: '/help', label: 'Справка' },
]

export default function App() {
  return (
    <div className="layout">
      <header className="masthead">
        <div>
          <h1>Информационно-поисковая система</h1>
          <p>Вероятностная модель поиска Okapi BM25 по русскоязычной коллекции документов</p>
        </div>
      </header>

      <nav className="nav">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) => (isActive ? 'active' : '')}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>

      <Routes>
        <Route path="/" element={<SearchPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/documents/:id" element={<DocumentPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/metrics" element={<MetricsPage />} />
        <Route path="/help" element={<HelpPage />} />
      </Routes>
    </div>
  )
}
