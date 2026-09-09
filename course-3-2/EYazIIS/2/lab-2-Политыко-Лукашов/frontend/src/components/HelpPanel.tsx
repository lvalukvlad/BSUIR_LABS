import { useState, useEffect } from 'react';
import { api } from '../api/client';

function HelpPanel() {
  const [helpData, setHelpData] = useState<any>(null);
  const [terms, setTerms] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState<'help' | 'terms'>('help');

  useEffect(() => {
    loadHelp();
  }, []);

  const loadHelp = async () => {
    try {
      setLoading(true);
      const [helpData, termsData] = await Promise.all([
        api.getHelp(),
        api.getTerms(),
      ]);
      setHelpData(helpData);
      setTerms(termsData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Загрузка справки...</div>;

  return (
    <div className="panel">
      <h2>Справка</h2>

      <div className="help-tabs">
        <button
          className={activeSection === 'help' ? 'active' : ''}
          onClick={() => setActiveSection('help')}
        >
          Как пользоваться
        </button>
        <button
          className={activeSection === 'terms' ? 'active' : ''}
          onClick={() => setActiveSection('terms')}
        >
          Термины
        </button>
      </div>

      {activeSection === 'help' && helpData && (
        <div className="help-content">
          <h3>{helpData.title}</h3>
          <p className="help-desc">{helpData.description}</p>
          
          {helpData.sections?.map((section: any) => (
            <div key={section.id} className="help-section">
              <h4>{section.title}</h4>
              <pre>{section.content}</pre>
            </div>
          ))}
        </div>
      )}

      {activeSection === 'terms' && terms && (
        <div className="terms-content">
          <h3>{terms.title}</h3>
          <dl className="terms-list">
            {terms.terms?.map((item: any, idx: number) => (
              <div key={idx} className="term-item">
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

export default HelpPanel;
