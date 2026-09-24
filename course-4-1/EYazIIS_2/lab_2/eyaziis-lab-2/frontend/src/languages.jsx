export const LANG_ORDER = ['русский', 'немецкий']

export function languageLabel(language) {
  if (language === 'немецкий') return 'Немецкий'
  if (language === 'русский') return 'Русский'
  return language || 'не обнаружен'
}

export function languagesFromDoc(doc) {
  const neural = doc?.result_json?.neural_network || {}
  const shares = neural.shares || {}
  const languages = neural.languages
    || (doc?.detected_language && doc.detected_language !== 'unknown'
      ? doc.detected_language.split(', ').filter(Boolean)
      : [])
  return { languages, shares }
}

export function formatShare(value) {
  if (value == null) return '—'
  return `${(Number(value) * 100).toFixed(1).replace('.', ',')}%`
}

export function detectedLanguages(languages, shares) {
  if (languages && languages.length) return languages
  return Object.entries(shares || {})
    .filter(([, value]) => Number(value) > 0)
    .sort((left, right) => right[1] - left[1])
    .map(([key]) => key)
}

export function formatLanguageList(languages, shares) {
  const items = detectedLanguages(languages, shares)
  if (!items.length) return 'не обнаружен'
  return items
    .map((lang) => {
      const share = shares?.[lang]
      return share == null ? languageLabel(lang) : `${languageLabel(lang)} ${formatShare(share)}`
    })
    .join(', ')
}

export function LanguageBadges({ languages, shares }) {
  const items = detectedLanguages(languages, shares)
  if (!items.length) return <span className="muted">не обнаружен</span>
  return (
    <span className="language-list">
      {items.map((lang) => (
        <span key={lang} className={`language-badge ${lang === 'немецкий' ? 'lang-german' : 'lang-russian'}`}>
          {languageLabel(lang)}
          {shares?.[lang] != null ? ` ${formatShare(shares[lang])}` : ''}
        </span>
      ))}
    </span>
  )
}
