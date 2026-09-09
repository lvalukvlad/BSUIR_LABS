import { useEffect, useState } from 'react';
import { api } from '../api/client';

function renderHelpContent(content: string) {
  const lines = content.split('\n').map((x) => x.trim()).filter(Boolean);
  const items = lines.filter((l) => /^(\d+\)|•|-)/.test(l));
  const plain = lines.filter((l) => !/^(\d+\)|•|-)/.test(l));

  return (
    <div className="help-lines">
      {plain.map((line, idx) => (
        <p key={`p-${idx}`} className="help-line">
          {line}
        </p>
      ))}
      {items.length ? (
        <ul className="help-list">
          {items.map((line, idx) => (
            <li key={`li-${idx}`}>{line.replace(/^(\d+\)|•|-)\s*/, '')}</li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

export default function HelpPanel() {
  const [help, setHelp] = useState<Awaited<ReturnType<typeof api.getHelp>> | null>(null);
  const [terms, setTerms] = useState<Awaited<ReturnType<typeof api.getTerms>> | null>(null);
  const [loading, setLoading] = useState(true);
  const [section, setSection] = useState<'help' | 'terms'>('help');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [h, t] = await Promise.all([api.getHelp(), api.getTerms()]);
        if (!cancelled) {
          setHelp(h);
          setTerms(t);
        }
      } catch (e) {
        console.error(e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) return <div className="loading">Загрузка справки…</div>;

  return (
    <div className="panel help-panel-wide">
      <h2>Справка</h2>
      <div className="help-tabs">
        <button
          type="button"
          className={section === 'help' ? 'active' : ''}
          onClick={() => setSection('help')}
        >
          Как пользоваться
        </button>
        <button
          type="button"
          className={section === 'terms' ? 'active' : ''}
          onClick={() => setSection('terms')}
        >
          Термины
        </button>
      </div>

      {section === 'help' && help && (
        <div className="help-content">
          <h3>{help.title}</h3>
          <p className="help-desc">{help.description}</p>
          {help.sections.map((s) => (
            <div key={s.id} className="help-section">
              <h4>{s.title}</h4>
              {renderHelpContent(s.content)}
            </div>
          ))}
        </div>
      )}

      {section === 'terms' && terms && (
        <div className="terms-content">
          <h3>{terms.title}</h3>
          <dl className="terms-list">
            {terms.terms.map((item) => (
              <div key={item.term} className="term-item">
                <dt>{item.term}</dt>
                <dd>{item.definition}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </div>
  );
}
