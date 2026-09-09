class DialectService:
    DIALECTS_BY_LANGUAGE = {
        'en': [
            {'value': '', 'label': 'Стандартный'},
            {'value': 'en-US', 'label': 'Американский'},
            {'value': 'en-GB', 'label': 'Британский'},
            {'value': 'en-AU', 'label': 'Австралийский'},
            {'value': 'en-CA', 'label': 'Канадский'}
        ],
        'fr': [
            {'value': '', 'label': 'Стандартный'},
            {'value': 'fr-FR', 'label': 'Французский (Франция)'},
            {'value': 'fr-CA', 'label': 'Французский (Канада)'},
            {'value': 'fr-BE', 'label': 'Французский (Бельгия)'},
            {'value': 'fr-CH', 'label': 'Французский (Швейцария)'}
        ],
        'de': [
            {'value': '', 'label': 'Стандартный'},
            {'value': 'de-DE', 'label': 'Немецкий (Германия)'},
            {'value': 'de-AT', 'label': 'Немецкий (Австрия)'},
            {'value': 'de-CH', 'label': 'Немецкий (Швейцария)'}
        ],
        'es': [
            {'value': '', 'label': 'Стандартный'},
            {'value': 'es-ES', 'label': 'Испанский (Испания)'},
            {'value': 'es-MX', 'label': 'Испанский (Мексика)'},
            {'value': 'es-AR', 'label': 'Испанский (Аргентина)'},
            {'value': 'es-CO', 'label': 'Испанский (Колумбия)'}
        ],
        'it': [
            {'value': '', 'label': 'Стандартный'},
            {'value': 'it-IT', 'label': 'Итальянский (Италия)'},
            {'value': 'it-CH', 'label': 'Итальянский (Швейцария)'}
        ],
        'ru': [
            {'value': '', 'label': 'Стандартный'},
            {'value': 'ru-RU', 'label': 'Русский (Россия)'},
            {'value': 'ru-UA', 'label': 'Русский (Украина)'}
        ],
        'zh': [
            {'value': '', 'label': 'Стандартный'},
            {'value': 'zh-CN', 'label': 'Китайский (упрощенный)'},
            {'value': 'zh-TW', 'label': 'Китайский (традиционный)'}
        ],
        'ja': [
            {'value': '', 'label': 'Стандартный'},
            {'value': 'ja-JP', 'label': 'Японский (Япония)'}
        ]
    }
    
    @staticmethod
    def get_dialects_for_language(lang_code):
        return DialectService.DIALECTS_BY_LANGUAGE.get(lang_code, [
            {'value': '', 'label': 'Стандартный'}
        ])

