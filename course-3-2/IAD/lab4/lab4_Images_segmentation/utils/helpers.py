import torch
import numpy as np

# Подсчёт параметров модели
def count_parameters(model):
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    return trainable, total

# Фиксация random seed для воспроизводимости
def set_seed(seed=42):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

# Вычисление весов классов для несбалансированных данных
def get_class_weights(dataset, num_classes):
    class_counts = np.zeros(num_classes)

    for _, mask in dataset:
        for cls in range(num_classes):
            class_counts[cls] += (mask == cls).sum().item()

    # Обратные веса (редкие классы получают больший вес)
    class_weights = 1.0 / (class_counts + 1e-6)
    class_weights = class_weights / class_weights.sum() * num_classes

    return torch.tensor(class_weights, dtype=torch.float32)

# Проверка корректности данных
def validate_data_format(dataset, num_classes, img_size=128):
    image, mask = dataset[0]

    # Определяем формат
    if hasattr(image, 'shape'):
        if len(image.shape) == 3 and image.shape[2] == 3:
            # numpy формат [H, W, C]
            h, w, c = image.shape
            print(f"✅ Image shape: {image.shape} (numpy [H, W, C])")
        elif len(image.shape) == 3 and image.shape[0] == 3:
            # torch формат [C, H, W]
            c, h, w = image.shape
            print(f"✅ Image shape: {image.shape} (torch [C, H, W])")
        else:
            print(f"⚠️  Unexpected image shape: {image.shape}")
            h, w = image.shape[:2] if len(image.shape) >= 2 else (0, 0)
    else:
        print(f"❌ Image has no shape attribute!")
        return

    print(f"✅ Mask shape: {mask.shape}")

    # Проверка типа mask
    if hasattr(mask, 'numpy'):
        # Это torch тензор
        mask_np = mask.numpy()
        mask_dtype = mask.dtype
        mask_classes = torch.unique(mask)
    else:
        # Это numpy массив
        mask_np = mask
        mask_dtype = mask.dtype
        mask_classes = np.unique(mask)

    print(f"✅ Mask dtype: {mask_dtype}")
    print(f"✅ Mask classes: {mask_classes}")

    # Assert проверки
    assert c == 3, f"Image channels mismatch: expected 3, got {c}"
    assert h >= img_size and w >= img_size, f"Image too small: {h}x{w} (expected >= {img_size}x{img_size})"
    assert mask_dtype in [np.uint8, np.int64, torch.int64], f"Mask dtype mismatch: {mask_dtype}"
    assert mask_classes.min() >= 0 and mask_classes.max() < num_classes, f"Mask classes out of range: {mask_classes}"

    # Проверка на дробные значения
    if hasattr(mask_np, 'dtype') and np.issubdtype(mask_np.dtype, np.floating):
        assert (mask_np == mask_np.astype(int)).all(), "Mask contains fractional values!"

    print("\n✅ Все проверки пройдены!")
    print("=" * 70)