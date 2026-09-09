from pathlib import Path
import torch
import os

# Автоматическое определение пути
if os.path.exists('/kaggle/input'):
    # Kaggle
    DATA_DIR = Path('/kaggle/input/understanding-cloud-organization')
    PROJECT_ROOT = Path('/kaggle/working')
else:
    # PyCharm
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / 'understanding_cloud_organization'

IMAGES_DIR = DATA_DIR / 'train_images'
MASKS_DIR = DATA_DIR / 'train_masks'
RESULTS_DIR = PROJECT_ROOT / 'results'

# Параметры
RANDOM_SEED = 42
BATCH_SIZE = 16
IMG_SIZE = 128  # ≤ 256
NUM_CLASSES = 5  # 0=фон, 1=Fish, 2=Flower, 3=Gravel, 4=Sugar
EPOCHS = 30
LEARNING_RATE = 1e-3
LEARNING_RATE_ENCODER = 1e-4  # Для pretrained encoder

# ImageNet статистики (для совместимости с pretrained)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Устройство
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Создание папок
RESULTS_DIR.mkdir(exist_ok=True)
MASKS_DIR.mkdir(exist_ok=True)

# Для отчёта
print(f"📂 Data: {DATA_DIR}")
print(f"📁 Results: {RESULTS_DIR}")
print(f"🖥️  Device: {DEVICE}")