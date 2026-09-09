class LogicEngineService:
    TRANSLATION_KNOWLEDGE_BASE = {
        "люблю": [
            {"style": "casual", "translation": "love"},
            {"style": "formal", "translation": "respect"},
            {"style": "poetic", "translation": "adore"}
        ],
        "ты": [
            {"style": "casual", "translation": "you"},
            {"style": "formal", "translation": "you (formal)"},
        ],
        "мир": [
            {"domain": "peace", "translation": "peace"},
            {"domain": "world", "translation": "world"},
        ]
    }

    @staticmethod
    def get_translation(word, context):
        rules = LogicEngineService.TRANSLATION_KNOWLEDGE_BASE.get(word.lower(), [])
        for rule in rules:
            match = True
            for key, value in context.items():
                if rule.get(key) != value:
                    match = False
                    break
            if match:
                return rule['translation']
        return word

    @staticmethod
    def parse_and_translate(text, context):
        words = text.split()
        translated_words = []
        for word in words:
            clean_word = word.strip('.,!?')
            punct = ''.join(c for c in word if c in '.,!?')
            translated_word = LogicEngineService.get_translation(clean_word, context)
            translated_words.append(translated_word + punct)
        return ' '.join(translated_words)