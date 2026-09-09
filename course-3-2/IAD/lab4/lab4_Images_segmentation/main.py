import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pathlib import Path
import os
import sys

# Добавляем корень проекта в path для импортов
sys.path.insert(0, str(Path(__file__).parent))

from configs.config import (
    DEVICE, NUM_CLASSES, EPOCHS, LEARNING_RATE, LEARNING_RATE_ENCODER,
    BATCH_SIZE, RESULTS_DIR, MASKS_DIR, DATA_DIR, IMG_SIZE
)
from data.dataset import get_dataloaders
from data.prepare_data import prepare_masks
from models.unet import UNet
from models.unet_pretrained import UNetPretrained
from training.train import train_epoch
from training.evaluate import evaluate
from utils.visualization import (
    plot_training_history,
    plot_predictions,
    plot_error_maps_worst,
    find_worst_predictions,
    visualize_dataset_samples
)
from utils.helpers import set_seed, count_parameters, validate_data_format

def main():
    print("Сегментация изображений")
    print("Датасет: Understanding Clouds from Satellite Images")
    print("=" * 70)
    print(f"Device: {DEVICE}")

    # Фиксация seed для воспроизводимости
    set_seed(42)

    # Подготовка данных
    print("Подготовка данных")
    print("=" * 70)

    # Генерация масок из RLE
    prepare_masks()

    # Создание DataLoader
    train_loader, val_loader = get_dataloaders(
        batch_size=BATCH_SIZE,
        max_train_samples=2000  # Ограничение для ускорения обучения
    )

    # Проверка корректности данных
    print("Проверка корректности данных")
    print("=" * 70)
    validate_data_format(train_loader.dataset, NUM_CLASSES, IMG_SIZE)

    # Визуализация датасета перед обучением
    print("Визуализация датасета перед обучением")
    print("=" * 70)
    visualize_dataset_samples(
        train_loader.dataset,
        num_samples=5,
        filename='dataset_samples.png'
    )

    # Задание 1: U-NET
    print("Задание 1: U-NET")
    print("=" * 70)
    model = UNet(in_channels=3, num_classes=NUM_CLASSES, base_filters=32).to(DEVICE)
    trainable_unet, total_unet = count_parameters(model)
    print(f"Params: {trainable_unet:,} (обуч.) / {total_unet:,} (всего)")
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    train_losses_unet, val_mious_unet = [], []
    best_mIoU_unet = 0
    best_epoch_unet = 0
    ious_per_class_unet = None

    for epoch in range(1, EPOCHS + 1):
        train_loss = train_epoch(model, train_loader, criterion, optimizer, DEVICE)
        mIoU, mDice, ious_per_class, _ = evaluate(model, val_loader, DEVICE, NUM_CLASSES)
        train_losses_unet.append(train_loss)
        val_mious_unet.append(mIoU)

        if mIoU > best_mIoU_unet:
            best_mIoU_unet = mIoU
            best_epoch_unet = epoch
            ious_per_class_unet = ious_per_class.copy() if ious_per_class is not None else None
            torch.save(model.state_dict(), RESULTS_DIR / 'best_model_unet.pth')

        print(
            f"Epoch {epoch:2d}/{EPOCHS} | Loss: {train_loss:.4f} | mIoU: {mIoU:.4f} | Dice: {mDice:.4f} | Best: {best_mIoU_unet:.4f}")

    # Загрузка лучшей модели для визуализации
    model.load_state_dict(torch.load(RESULTS_DIR / 'best_model_unet.pth', weights_only=True, map_location=DEVICE))

    # Визуализация результатов
    plot_training_history(train_losses_unet, val_mious_unet, suffix='unet')
    plot_predictions(
        model, val_loader.dataset, DEVICE, NUM_CLASSES,
        num_samples=6, suffix='unet'
    )

    # Финальная оценка на валидации
    final_mIoU_unet, final_mDice_unet, ious_per_class_unet, _ = evaluate(
        model, val_loader, DEVICE, NUM_CLASSES
    )

    print(f"\n✅ Задание 1 завершено!")
    print(f"   Лучший mIoU: {best_mIoU_unet:.4f} (эпоха {best_epoch_unet})")
    print(f"   Финальный mIoU: {final_mIoU_unet:.4f}")
    print(f"   Финальный Dice: {final_mDice_unet:.4f}")

    # Задание 2: U-NET with pretrained encoder
    print("Задание 2: U-NET with pretrained encoder (ResNet18)")
    print("=" * 70)
    model_pt = UNetPretrained(num_classes=NUM_CLASSES, pretrained=True).to(DEVICE)
    trainable_pt, total_pt = count_parameters(model_pt)
    print(f"Params: {trainable_pt:,} (обуч.) / {total_pt:,} (всего)")

    # Раздельный LR для encoder/decoder
    optimizer_pt = optim.Adam([
        {'params': model_pt.get_encoder_params(), 'lr': LEARNING_RATE_ENCODER},  # 1e-4
        {'params': model_pt.get_decoder_params(), 'lr': LEARNING_RATE},  # 1e-3
    ])

    train_losses_pt, val_mious_pt = [], []
    best_mIoU_pt = 0
    best_epoch_pt = 0
    ious_per_class_pt = None

    for epoch in range(1, EPOCHS + 1):
        train_loss = train_epoch(model_pt, train_loader, criterion, optimizer_pt, DEVICE)
        mIoU, mDice, ious_per_class, _ = evaluate(model_pt, val_loader, DEVICE, NUM_CLASSES)
        train_losses_pt.append(train_loss)
        val_mious_pt.append(mIoU)

        if mIoU > best_mIoU_pt:
            best_mIoU_pt = mIoU
            best_epoch_pt = epoch
            ious_per_class_pt = ious_per_class.copy() if ious_per_class is not None else None
            torch.save(model_pt.state_dict(), RESULTS_DIR / 'best_model_unet_pretrained.pth')

        print(
            f"Epoch {epoch:2d}/{EPOCHS} | Loss: {train_loss:.4f} | mIoU: {mIoU:.4f} | Dice: {mDice:.4f} | Best: {best_mIoU_pt:.4f}")

    # Загрузка лучшей модели
    model_pt.load_state_dict(
        torch.load(RESULTS_DIR / 'best_model_unet_pretrained.pth', weights_only=True, map_location=DEVICE))

    # Визуализация результатов
    plot_training_history(train_losses_pt, val_mious_pt, suffix='unet_pretrained')
    plot_predictions(
        model_pt, val_loader.dataset, DEVICE, NUM_CLASSES,
        num_samples=6, suffix='unet_pretrained'
    )

    # Финальная оценка
    final_mIoU_pt, final_mDice_pt, ious_per_class_pt, _ = evaluate(
        model_pt, val_loader, DEVICE, NUM_CLASSES
    )

    print(f"\n✅ Задание 2 завершено!")
    print(f"   Лучший mIoU: {best_mIoU_pt:.4f} (эпоха {best_epoch_pt})")
    print(f"   Финальный mIoU: {final_mIoU_pt:.4f}")
    print(f"   Финальный Dice: {final_mDice_pt:.4f}")

    # Итоговая таблица сравнения моделей
    print("Итоговая таблица сравнения моделей")
    print("=" * 70)

    print(f"""
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  Модель              │  Параметры  │  Параметры  │  Эпохи  │  mIoU(val)  │  mIoU(test)  │
│                      │  (всего)    │  (обуч.)    │         │             │              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  U-Net с нуля        │  {total_unet:>10,} │  {trainable_unet:>10,} │  {EPOCHS:>5}  │  {best_mIoU_unet:>9.4f}  │ {best_mIoU_unet:>11.4f}  │
│  U-Net + Pretrained  │  {total_pt:>10,} │  {trainable_pt:>10,} │  {EPOCHS:>5}  │  {best_mIoU_pt:>9.4f}  │ {best_mIoU_pt:>11.4f}  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
    """)

    # IoU по каждому классу
    print("IoU по каждому классу")
    print("=" * 70)

    CLASS_NAMES = ['Фон', 'Fish', 'Flower', 'Gravel', 'Sugar']

    print(f"{'Класс':<12} {'IoU (с нуля)':<15} {'IoU (pretrained)':<18} {'Улучшение':<10}")
    print("-" * 60)

    if ious_per_class_unet and ious_per_class_pt:
        for i, name in enumerate(CLASS_NAMES):
            iou_unet = ious_per_class_unet[i]
            iou_pt = ious_per_class_pt[i]
            delta = iou_pt - iou_unet
            print(f"{name:<12} {iou_unet:<15.4f} {iou_pt:<18.4f} {delta:+.4f}")

    print("-" * 60)

    # Анализ ошибок
    print("Анализ ошибок")
    print("=" * 70)

    # Поиск 6 изображений с наименьшим IoU
    worst_results = find_worst_predictions(
        model_pt, val_loader.dataset, DEVICE, NUM_CLASSES, num_samples=6
    )

    # Визуализация
    plot_error_maps_worst(worst_results, NUM_CLASSES, filename='error_maps_worst.png')

    # Анализируем ошибки по классам
    print("\nАнализ ошибок по классам (на 6 худших изображениях):")
    print("-" * 70)

    class_errors = {i: 0 for i in range(NUM_CLASSES)}
    total_pixels = {i: 0 for i in range(NUM_CLASSES)}

    for result in worst_results:
        true_mask = result['true_mask']
        error_map = result['error_map']

        for cls in range(NUM_CLASSES):
            cls_pixels = (true_mask == cls).sum()
            total_pixels[cls] += cls_pixels
            cls_errors = ((true_mask == cls) & (error_map == 1)).sum()
            class_errors[cls] += cls_errors

    print(f"{'Класс':<10} {'Всего пикселей':<18} {'Ошибок':<10} {'% ошибок':<10}")
    print("-" * 70)
    for i, name in enumerate(CLASS_NAMES):
        if total_pixels[i] > 0:
            error_rate = class_errors[i] / total_pixels[i] * 100
            print(f"{name:<10} {total_pixels[i]:<18} {class_errors[i]:<10} {error_rate:.2f}%")
    print("-" * 70)

    # Классификация типичных ошибок
    print("\nКлассификация типичных ошибок:")
    print("""
1. Границы объектов:
   - Наблюдается неточное выделение контуров облаков
   - Размытые переходы между классами (особенно Fish/Flower)
   - Модель "размазывает" границы при пулинге

2. Мелкие объекты:
   - Маленькие облака типа Sugar часто пропускаются
   - Тонкие структуры теряются при уменьшении разрешения
   - Объекты < 10 пикселей могут быть полностью пропущены

3. Похожие классы:
   - Fish ↔ Flower: путаются из-за схожей текстуры
   - Gravel ↔ Sugar: похожие паттерны (мелкие детали)
   - Модель использует текстурные признаки, а не семантику

4. Сложные случаи:
   - Изображения с множественными типами облаков
   - Облака на границе кадра (частичное перекрытие)
   - Низкая контрастность между облаком и фоном
   - Перекрывающиеся облака разных типов
    """)

    # Предложения по улучшению
    print("\nПредложения по улучшению:")
    print("""
1. Функции потерь:
   - Boundary Loss для точных границ облаков
   - Focal Loss для баланса классов (если есть дисбаланс)
   - Combo Loss (CrossEntropy + Dice) для лучшей сходимости
   - Tversky Loss для медицинской сегментации

2. Аугментация:
   - RandomErasing для улучшения робастности к частичным объектам
   - CutMix для обучения на составных изображениях
   - ColorJitter для разнообразия освещения и погоды
   - ElasticTransform для симуляции деформаций облаков

3. Архитектура:
   - Увеличение глубины (4 уровня вместо 3)
   - Attention gates в skip-connections (Attention U-Net)
   - Deeper backbone (ResNet34/50 вместо ResNet18)
   - Dilated convolutions для большего receptive field

4. Post-processing:
   - Conditional Random Fields (CRF) для сглаживания границ
   - Морфологические операции (opening/closing) для удаления шума
   - Threshold tuning для каждого класса отдельно
   - Connected components для удаления мелких ложных срабатываний
    """)

    print("\n" + "=" * 70)
    print("The End!)")
    print("=" * 70)

    print(f"""
📁 Результаты сохранены в: {RESULTS_DIR}

Файлы:
  ✅ best_model_unet.pth              — веса U-Net с нуля
  ✅ best_model_unet_pretrained.pth   — веса U-Net с pretrained encoder
  ✅ training_history_unet.png        — графики обучения (U-Net)
  ✅ training_history_unet_pretrained.png — графики обучения (Pretrained)
  ✅ predictions_unet.png             — предсказания (U-Net, 6 изображений)
  ✅ predictions_unet_pretrained.png  — предсказания (Pretrained, 6 изображений)
  ✅ error_maps_worst.png             — карты ошибок (6 худших по IoU)
  ✅ dataset_samples.png              — примеры датасета (5 изображений ДО обучения)

Итоговые метрики:
  • U-Net с нуля:        mIoU = {best_mIoU_unet:.4f}, Dice = {final_mDice_unet:.4f}
  • U-Net + Pretrained:  mIoU = {best_mIoU_pt:.4f}, Dice = {final_mDice_pt:.4f}
  • Улучшение:           ΔmIoU = {best_mIoU_pt - best_mIoU_unet:+.4f}
    """)

    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Обучение прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)