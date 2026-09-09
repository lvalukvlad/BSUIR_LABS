# run_translator.py
import json
import os
import pandas as pd

print("🚀 Создание базы лекарств...")

# Создаем папку data если нет
os.makedirs("data", exist_ok=True)

# 1. Проверяем есть ли исходный датасет
csv_path = "data/medicine_dataset.csv"
if not os.path.exists(csv_path):
    print("⚠️  Исходный CSV не найден, создаю тестовый...")

    # Создаем тестовые данные
    test_data = {
        "id": [1, 2, 3, 4, 5],
        "name": [
            "augmentin 625 duo tablet",
            "azithral 500 tablet",
            "ascoril ls syrup",
            "paracetamol 500mg tablet",
            "ibuprofen 400mg tablet"
        ],
        "use0": [
            "Treatment of Bacterial infections",
            "Treatment of Bacterial infections",
            "Treatment of Cough with mucus",
            "Treatment of Pain",
            "Treatment of Pain and inflammation"
        ],
        "Therapeutic Class": [
            "ANTI INFECTIVES",
            "ANTI INFECTIVES",
            "RESPIRATORY",
            "ANALGESICS",
            "ANALGESICS"
        ]
    }

    df = pd.DataFrame(test_data)
    df.to_csv(csv_path, index=False)
    print(f"✅ Создан тестовый CSV: {csv_path}")

# 2. Загружаем данные
try:
    df = pd.read_csv(csv_path)
    print(f"📊 Загружено {len(df)} лекарств из {csv_path}")
except Exception as e:
    print(f"❌ Ошибка загрузки CSV: {e}")
    # Создаем минимальный набор
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["augmentin", "paracetamol", "ibuprofen"],
        "use0": ["Antibiotic", "Pain relief", "Pain and inflammation"],
        "Therapeutic Class": ["Antibiotics", "Analgesics", "NSAIDs"]
    })

# 3. Простой перевод
translated_medicines = []

for i, row in df.iterrows():
    if i >= 500:  # Ограничиваем 500
        break

    name_en = str(row.get("name", f"Medicine_{row.get('id', i + 1)}"))

    # Простой rule-based перевод
    name_ru = name_en
    translations = {
        "tablet": "таблетки",
        "syrup": "сироп",
        "capsule": "капсулы",
        "augmentin": "Аугментин",
        "azithral": "Азитрал",
        "ascoril": "Аскорил",
        "paracetamol": "Парацетамол",
        "ibuprofen": "Ибупрофен",
        "mg": "мг",
        "duo": "дуо"
    }

    for eng, ru in translations.items():
        if eng in name_ru.lower():
            name_ru = name_ru.lower().replace(eng, ru)

    # Первая буква заглавная
    name_ru = name_ru.capitalize()

    medicine = {
        "id": int(row.get("id", i + 1)),
        "name_en": name_en,
        "name_ru": name_ru,
        "uses_ru": ["Лечение заболеваний"],  # упрощенно
        "therapeutic_class_ru": str(row.get("Therapeutic Class", "Лекарственный препарат")),
        "form": "таблетки" if "tablet" in name_en.lower() else "сироп" if "syrup" in name_en.lower() else "форма выпуска"
    }

    translated_medicines.append(medicine)

# 4. Сохраняем
output_path = "data/medicines_ru_top500.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(translated_medicines, f, ensure_ascii=False, indent=2)

print(f"✅ Сохранено {len(translated_medicines)} лекарств в {output_path}")
print("\n💊 Примеры переведенных лекарств:")
for med in translated_medicines[:3]:
    print(f"   {med['name_en']} → {med['name_ru']}")

print(f"\n🎯 Готово! Файл: {output_path}")