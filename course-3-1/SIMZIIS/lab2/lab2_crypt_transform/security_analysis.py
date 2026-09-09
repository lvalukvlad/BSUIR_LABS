class ScytaleSecurityAnalysis:
    def __init__(self):
        self.analysis_results = {}

    def analyze_key_space(self, max_text_length=1000):
        analysis = {
            'problem': 'Малое пространство ключей',
            'description': 'Ключом является только диаметр палки, который должен быть ≤ длине текста',
            'key_space_size': max_text_length,
            'complexity': 'O(n)',
            'vulnerability': 'Высокая',
            'recommendation': 'Недостаточно для современной криптографии',
            'example': f'Для текста из {max_text_length} символов: {max_text_length} возможных ключей'
        }
        return analysis

    def analyze_time_complexity_attack(self):
        analysis = {
            'problem': 'Полиномиальное время взлома',
            'description': 'Атака полным перебором требует O(n²) операций',
            'time_complexity': 'O(n²)',
            'vulnerability': 'Критическая',
            'example': 'Текст из 1000 символов взламывается за ~1 млн попыток',
            'comparison': 'Современные шифры требуют 2¹²⁸ операций для взлома'
        }
        return analysis

    def analyze_frequency_analysis_resistance(self):
        analysis = {
            'problem': 'Сохранение частотных характеристик',
            'description': 'Шифр только переставляет символы, не меняя их частотное распределение',
            'vulnerability': 'Высокая',
            'attack_method': 'Частотный анализ сохраняет эффективность',
            'protection': 'Отсутствует'
        }
        return analysis

    def analyze_known_plaintext_attack(self):
        analysis = {
            'problem': 'Уязвимость к атаке по известному тексту',
            'description': 'При известной паре (открытый текст, шифртекст) ключ находится мгновенно',
            'vulnerability': 'Абсолютная',
            'protection': 'Отсутствует',
            'example': 'Зная всего 1 пару текст-шифр, можно найти ключ'
        }
        return analysis

    def analyze_modern_standards_comparison(self):
        analysis = {
            'problem': 'Несоответствие современным требованиям',
            'description': 'Шифр Скитала не удовлетворяет критериям Керкхоффа',
            'vulnerability': 'Критическая',
            'comparison': {
                'AES-256': '2²⁵⁶ ключей → невозможно взломать',
                'RSA-2048': '2¹⁰²⁴ операций → миллионы лет',
                'Scytale': 'n ключей → секунды/минуты'
            },
            'conclusion': 'Устаревший шифр'
        }
        return analysis

    def calculate_security_score(self):
        assessments = [
            self.analyze_key_space(),
            self.analyze_time_complexity_attack(),
            self.analyze_frequency_analysis_resistance(),
            self.analyze_known_plaintext_attack()
        ]

        score_mapping = {
            'Критическая': 0,
            'Абсолютная': 0,
            'Высокая': 1,
            'Средняя': 2,
            'Низкая': 3
        }

        total_score = 0
        max_score = len(assessments) * 3

        for assessment in assessments:
            total_score += score_mapping.get(assessment['vulnerability'], 0)

        security_percentage = (total_score / max_score) * 100
        return security_percentage

    def full_security_assessment(self):
        assessments = [
            self.analyze_key_space(),
            self.analyze_time_complexity_attack(),
            self.analyze_frequency_analysis_resistance(),
            self.analyze_known_plaintext_attack(),
            self.analyze_modern_standards_comparison()
        ]

        print("=" * 70)
        print("ОЦЕНКА КРИПТОГРАФИЧЕСКОЙ СТОЙКОСТИ ШИФРА СКИТАЛА")
        print("=" * 70)

        for i, assessment in enumerate(assessments, 1):
            print(f"\n{i}. {assessment['problem']}")
            print(f"{assessment['description']}")
            if 'vulnerability' in assessment:
                print(f"Уязвимость: {assessment['vulnerability']}")
            if 'example' in assessment:
                print(f"Пример: {assessment['example']}")
            if 'recommendation' in assessment:
                print(f"Рекомендация: {assessment['recommendation']}")

        security_score = self.calculate_security_score()

        print(f"\n{'=' * 70}")
        print(f"ОБЩАЯ ОЦЕНКА СТОЙКОСТИ: {security_score:.1f}%")
        print(f"{'=' * 70}")

        if security_score < 25:
            print("🚨 КРИТИЧЕСКИ НЕНАДЕЖНЫЙ ШИФР")
            print("❌ Не использовать для защиты конфиденциальной информации!")
            print("✅ Только для учебных целей и демонстрации")
        elif security_score < 50:
            print("⚠️  СЛАБЫЙ ШИФР")
            print("✅ Только для учебных целей")
        else:
            print("✅ ПРИЕМЛЕМАЯ СТОЙКОСТЬ")

        print(f"\nВЫВОД: Шифр Скитала является историческим криптографическим")
        print("          алгоритмом и не должен использоваться в современных")
        print("          системах защиты информации.")

        return security_score


def demonstrate_security_analysis():
    analyzer = ScytaleSecurityAnalysis()
    print("ДЕМОНСТРАЦИЯ АНАЛИЗА КРИПТОГРАФИЧЕСКОЙ СТОЙКОСТИ")
    print("=" * 50)
    score = analyzer.full_security_assessment()
    return score


if __name__ == "__main__":
    demonstrate_security_analysis()