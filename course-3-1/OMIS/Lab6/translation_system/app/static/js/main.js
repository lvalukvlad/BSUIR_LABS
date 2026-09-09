document.addEventListener('DOMContentLoaded', () => {
  const dialects = {
    'en': [
      {value: '', label: 'Стандартный'},
      {value: 'en-US', label: 'Американский'},
      {value: 'en-GB', label: 'Британский'},
      {value: 'en-AU', label: 'Австралийский'},
      {value: 'en-CA', label: 'Канадский'}
    ],
    'fr': [
      {value: '', label: 'Стандартный'},
      {value: 'fr-FR', label: 'Французский (Франция)'},
      {value: 'fr-CA', label: 'Французский (Канада)'},
      {value: 'fr-BE', label: 'Французский (Бельгия)'},
      {value: 'fr-CH', label: 'Французский (Швейцария)'}
    ],
    'de': [
      {value: '', label: 'Стандартный'},
      {value: 'de-DE', label: 'Немецкий (Германия)'},
      {value: 'de-AT', label: 'Немецкий (Австрия)'},
      {value: 'de-CH', label: 'Немецкий (Швейцария)'}
    ],
    'es': [
      {value: '', label: 'Стандартный'},
      {value: 'es-ES', label: 'Испанский (Испания)'},
      {value: 'es-MX', label: 'Испанский (Мексика)'},
      {value: 'es-AR', label: 'Испанский (Аргентина)'},
      {value: 'es-CO', label: 'Испанский (Колумбия)'}
    ],
    'it': [
      {value: '', label: 'Стандартный'},
      {value: 'it-IT', label: 'Итальянский (Италия)'},
      {value: 'it-CH', label: 'Итальянский (Швейцария)'}
    ],
    'ru': [
      {value: '', label: 'Стандартный'},
      {value: 'ru-RU', label: 'Русский (Россия)'},
      {value: 'ru-UA', label: 'Русский (Украина)'}
    ],
    'zh': [
      {value: '', label: 'Стандартный'},
      {value: 'zh-CN', label: 'Китайский (упрощенный)'},
      {value: 'zh-TW', label: 'Китайский (традиционный)'}
    ],
    'ja': [
      {value: '', label: 'Стандартный'},
      {value: 'ja-JP', label: 'Японский (Япония)'}
    ]
  };

  function updateDialects(targetLang) {
    const dialectSelect = document.getElementById('dialect');
    if (!dialectSelect) return;
    
    const langDialects = dialects[targetLang] || [{value: '', label: 'Стандартный'}];
    dialectSelect.innerHTML = langDialects.map(d => 
      `<option value="${d.value}">${d.label}</option>`
    ).join('');
  }

  function saveFormState() {
    const sourceLang = document.getElementById('source_lang')?.value;
    const targetLang = document.getElementById('target_lang')?.value;
    const translationType = document.querySelector('select[name="translation_type"]')?.value;
    const domain = document.querySelector('select[name="domain"]')?.value;
    const style = document.querySelector('select[name="style"]')?.value;
    const audience = document.querySelector('select[name="audience"]')?.value;
    const dialect = document.getElementById('dialect')?.value;
    
    if (sourceLang) localStorage.setItem('source_lang', sourceLang);
    if (targetLang) localStorage.setItem('target_lang', targetLang);
    if (translationType) localStorage.setItem('translation_type', translationType);
    if (domain) localStorage.setItem('domain', domain);
    if (style) localStorage.setItem('style', style);
    if (audience) localStorage.setItem('audience', audience);
    if (dialect) localStorage.setItem('dialect', dialect);
  }
  
  function restoreFormState() {
    const sourceLang = localStorage.getItem('source_lang');
    const targetLang = localStorage.getItem('target_lang');
    const translationType = localStorage.getItem('translation_type');
    const domain = localStorage.getItem('domain');
    const style = localStorage.getItem('style');
    const audience = localStorage.getItem('audience');
    const dialect = localStorage.getItem('dialect');
    
    if (sourceLang && document.getElementById('source_lang')) {
      document.getElementById('source_lang').value = sourceLang;
    }
    if (targetLang && document.getElementById('target_lang')) {
      document.getElementById('target_lang').value = targetLang;
      updateDialects(targetLang);
      if (dialect) {
        setTimeout(() => {
          const dialectSelect = document.getElementById('dialect');
          if (dialectSelect) dialectSelect.value = dialect;
        }, 100);
      }
    }
    if (translationType && document.querySelector('select[name="translation_type"]')) {
      document.querySelector('select[name="translation_type"]').value = translationType;
    }
    if (domain && document.querySelector('select[name="domain"]')) {
      document.querySelector('select[name="domain"]').value = domain;
    }
    if (style && document.querySelector('select[name="style"]')) {
      document.querySelector('select[name="style"]').value = style;
    }
    if (audience && document.querySelector('select[name="audience"]')) {
      document.querySelector('select[name="audience"]').value = audience;
    }
  }

  const targetLangSelect = document.getElementById('target_lang');
  if (targetLangSelect) {
    restoreFormState();
    
    if (!localStorage.getItem('target_lang')) {
      updateDialects(targetLangSelect.value);
    }
    
    targetLangSelect.addEventListener('change', (e) => {
      updateDialects(e.target.value);
      saveFormState();
    });
  }
  
  document.querySelectorAll('select').forEach(select => {
    select.addEventListener('change', saveFormState);
  });

  const form = document.getElementById('translate-form');
  if (form) {
    form.onsubmit = async (e) => {
      e.preventDefault();

      const content = document.getElementById('content').value;
      const source_lang = document.getElementById('source_lang').value;
      const target_lang = document.getElementById('target_lang').value;
      const style = document.getElementById('style').value;
      const dialect = document.getElementById('dialect').value;

      const response = await fetch('/api/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          context: { style },
          dialect
        })
      });

      const data = await response.json();
      if (data.message) {
        document.getElementById('result').innerHTML = `<h3>Результат перевода:</h3><p><strong>${data.message}</strong></p>`;
      } else {
        document.getElementById('result').innerHTML = `<h3>Результат перевода:</h3><p><strong>${data.draft}</strong></p>`;
      }
      document.getElementById('result').style.display = 'block';
    };
  }

  const buttons = document.querySelectorAll('button');
  buttons.forEach(button => {
    button.addEventListener('click', () => {
      button.innerHTML = 'Обработка...';
      setTimeout(() => {
        button.innerHTML = 'Перевести';
      }, 1500);
    });
  });
});