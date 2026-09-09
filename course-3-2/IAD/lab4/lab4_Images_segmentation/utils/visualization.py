import numpy as np
import matplotlib.pyplot as plt
import torch
from configs.config import RESULTS_DIR, IMAGENET_MEAN, IMAGENET_STD

# Цвета для классов
CLASS_COLORS = {
    0: [0, 0, 0],  # Фон - чёрный
    1: [255, 0, 0],  # Fish - красный
    2: [0, 255, 0],  # Flower - зелёный
    3: [0, 0, 255],  # Gravel - синий
    4: [255, 255, 0],  # Sugar - жёлтый
}

# Конвертация маски в цветное изображение для визуализации
def mask_to_color(mask):
    color_mask = np.zeros((*mask.shape, 3), dtype=np.uint8)
    for class_id, color in CLASS_COLORS.items():
        color_mask[mask == class_id] = color
    return color_mask

# Денормализация изображения (ImageNet stats)
def denormalize_image(image):
    if hasattr(image, 'cpu'):
        # Это torch тензор [C, H, W]
        image = image.cpu().permute(1, 2, 0).numpy()
    else:
        # Это numpy массив [H, W, C]
        image = image
    image = image * np.array(IMAGENET_STD) + np.array(IMAGENET_MEAN)
    return np.clip(image, 0, 1)


# Визуализация примеров из датасета перед обучением.
def visualize_dataset_samples(dataset, num_samples=5, filename='dataset_samples.png'):
    fig, axes = plt.subplots(num_samples, 2, figsize=(10, 5 * num_samples))

    # Если только 1 образец, axes не будет массивом
    if num_samples == 1:
        axes = axes.reshape(1, -1)

    for i in range(num_samples):
        image, mask = dataset[i]

        # Денормализация изображения (работает с numpy и torch)
        image_np = denormalize_image(image)

        # Маска (может быть numpy или torch)
        if hasattr(mask, 'numpy'):
            mask_np = mask.numpy()
        else:
            mask_np = mask

        # Столбец 1: Исходное изображение
        axes[i, 0].imshow(image_np)
        axes[i, 0].set_title(f'Image {i + 1}')
        axes[i, 0].axis('off')

        # Столбец 2: Маска (цветная)
        axes[i, 1].imshow(mask_to_color(mask_np))
        axes[i, 1].set_title(f'Mask {i + 1} (classes: {np.unique(mask_np).tolist()})')
        axes[i, 1].axis('off')

    plt.tight_layout()
    plt.savefig(RESULTS_DIR / filename, dpi=150)
    plt.close()
    print(f"✅ Визуализация датасета сохранена в {RESULTS_DIR / filename}")

# Графики обучения: train loss + val mIoU по эпохам
def plot_training_history(train_losses, val_mious, suffix=''):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # График 1: Train Loss
    axes[0].plot(train_losses, 'b-', linewidth=2)
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Train Loss')
    axes[0].grid(True, alpha=0.3)

    # График 2: Validation mIoU
    axes[1].plot(val_mious, 'g-', linewidth=2)
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Mean IoU')
    axes[1].set_title('Validation mIoU')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    filename = f'training_history_{suffix}.png' if suffix else 'training_history.png'
    plt.savefig(RESULTS_DIR / filename, dpi=150)
    plt.close()
    print(f"✅ Графики сохранены в {RESULTS_DIR / filename}")

#  Визуализация предсказаний модели
def plot_predictions(model, dataset, device, num_classes, num_samples=6, suffix=''):
    model.eval()
    fig, axes = plt.subplots(num_samples, 3, figsize=(15, 5 * num_samples))

    # Если только 1 образец, axes не будет массивом
    if num_samples == 1:
        axes = axes.reshape(1, -1)

    for i in range(num_samples):
        image, mask = dataset[i]

        # Предсказание
        with torch.no_grad():
            logits = model(image.unsqueeze(0).to(device))
            pred_mask = logits.argmax(dim=1).squeeze(0).cpu().numpy()

        image_np = denormalize_image(image)
        mask_np = mask.numpy()

        # Столбец 1: Исходное изображение
        axes[i, 0].imshow(image_np)
        axes[i, 0].set_title('Image')
        axes[i, 0].axis('off')

        # Столбец 2: Истинная маска
        axes[i, 1].imshow(mask_to_color(mask_np))
        axes[i, 1].set_title('True Mask')
        axes[i, 1].axis('off')

        # Столбец 3: Предсказанная маска
        axes[i, 2].imshow(mask_to_color(pred_mask))
        axes[i, 2].set_title('Pred Mask')
        axes[i, 2].axis('off')

    plt.tight_layout()
    filename = f'predictions_{suffix}.png' if suffix else 'predictions.png'
    plt.savefig(RESULTS_DIR / filename, dpi=150)
    plt.close()
    print(f"✅ Предсказания сохранены в {RESULTS_DIR / filename}")

# Поиск изображения с наименьшим IoU для анализа ошибок
def find_worst_predictions(model, dataset, device, num_classes, num_samples=6):
    model.eval()
    results = []

    with torch.no_grad():
        for i in range(len(dataset)):
            image, mask = dataset[i]

            # Предсказание
            logits = model(image.unsqueeze(0).to(device))
            pred_mask = logits.argmax(dim=1).squeeze(0).cpu().numpy()
            true_mask = mask.numpy()

            # Вычисление IoU для этого изображения (по всем классам)
            iou_sum = 0
            num_present_classes = 0
            for cls in range(num_classes):
                pred_cls = (pred_mask == cls)
                true_cls = (true_mask == cls)
                intersection = (pred_cls & true_cls).sum()
                union = (pred_cls | true_cls).sum()
                if union > 0:
                    iou_sum += intersection / union
                    num_present_classes += 1

            avg_iou = iou_sum / max(num_present_classes, 1)

            # Карта ошибок: бинарное изображение
            error_map = (pred_mask != true_mask).astype(float)

            results.append({
                'idx': i,
                'image': image,
                'true_mask': true_mask,
                'pred_mask': pred_mask,
                'iou': avg_iou,
                'error_map': error_map
            })

    # Сортировка по IoU (наименьший первый)
    results.sort(key=lambda x: x['iou'])

    # Возвращаем num_samples худших предсказаний
    return results[:num_samples]

# Визуализация изображений с наименьшим IoU
def plot_error_maps_worst(worst_results, num_classes, filename='error_maps_worst.png'):
    num_samples = len(worst_results)
    fig, axes = plt.subplots(num_samples, 4, figsize=(20, 5 * num_samples))

    # Если только 1 образец, axes не будет массивом
    if num_samples == 1:
        axes = axes.reshape(1, -1)

    for i, result in enumerate(worst_results):
        # Денормализация изображения
        image_np = denormalize_image(result['image'])

        true_mask = result['true_mask']
        pred_mask = result['pred_mask']
        error_map = result['error_map']
        iou = result['iou']

        # Столбец 1: Исходное изображение
        axes[i, 0].imshow(image_np)
        axes[i, 0].set_title(f'Image (IoU={iou:.3f})')
        axes[i, 0].axis('off')

        # Столбец 2: Истинная маска
        axes[i, 1].imshow(mask_to_color(true_mask))
        axes[i, 1].set_title('True Mask')
        axes[i, 1].axis('off')

        # Столбец 3: Предсказанная маска
        axes[i, 2].imshow(mask_to_color(pred_mask))
        axes[i, 2].set_title('Pred Mask')
        axes[i, 2].axis('off')

        # Столбец 4: Карта ошибок
        axes[i, 3].imshow(error_map, cmap='Reds')
        axes[i, 3].set_title('Error Map')
        axes[i, 3].axis('off')

    plt.tight_layout()
    plt.savefig(RESULTS_DIR / filename, dpi=150)
    plt.close()
    print(f"✅ Карты ошибок (худшие {num_samples}) сохранены в {RESULTS_DIR / filename}")