"""
Сервис для анализа культурных особенностей текста
"""
class CulturalAnalysisService:
    CULTURAL_PATTERNS = {
        'ru': {
            'greetings': {
                'formal': ['здравствуйте', 'добрый день', 'добрый вечер'],
                'casual': ['привет', 'здорово', 'салют']
            },
            'address': {
                'formal': ['вы', 'вас', 'вам'],
                'casual': ['ты', 'тебя', 'тебе']
            }
        },
        'en': {
            'greetings': {
                'formal': ['hello', 'good morning', 'good evening'],
                'casual': ['hi', 'hey', 'what\'s up']
            },
            'address': {
                'formal': ['you (formal)', 'sir', 'madam'],
                'casual': ['you', 'dude', 'buddy']
            }
        }
    }
    
    @staticmethod
    def analyze_cultural_features(text, source_lang, target_lang, context):
        """
        Анализирует культурные особенности текста
        """
        cultural_notes = []
        
        if source_lang == 'ru':
            if any(word in text.lower() for word in ['вы', 'вас', 'вам']):
                cultural_notes.append({
                    'type': 'address_formality',
                    'source': 'formal',
                    'target': 'should use formal address in ' + target_lang,
                    'importance': 'high'
                })
            elif any(word in text.lower() for word in ['ты', 'тебя', 'тебе']):
                cultural_notes.append({
                    'type': 'address_formality',
                    'source': 'casual',
                    'target': 'can use casual address in ' + target_lang,
                    'importance': 'medium'
                })
        
        text_lower = text.lower()
        if source_lang == 'ru':
            if any(greeting in text_lower for greeting in CulturalAnalysisService.CULTURAL_PATTERNS['ru']['greetings']['formal']):
                cultural_notes.append({
                    'type': 'greeting',
                    'source': 'formal greeting',
                    'target': 'use formal greeting equivalent',
                    'importance': 'high'
                })
        
        if context.get('domain') == 'love' and source_lang == 'ru':
            cultural_notes.append({
                'type': 'expression',
                'source': 'Russian love expressions are more direct',
                'target': 'may need adaptation for ' + target_lang + ' cultural norms',
                'importance': 'medium'
            })
        
        return cultural_notes

