import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split, Subset
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import os

# Конфигурация
RANDOM_SEED = 42
BATCH_SIZE = 64
NUM_CLASSES = 26  # EMNIST Letters: A-Z
MAX_TRAIN_SAMPLES = 80000  # Для соответствия требованию <= 100000 изображений

# Фиксация random seed
torch.manual_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed(RANDOM_SEED)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


### Подготовка данных
def prepare_data():
    print("Подготовка данных")

    # Трансформации
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    # Загрузка датасета
    original_train = torchvision.datasets.EMNIST(
        root='./data', split='letters', train=True,
        download=True, transform=transform
    )
    test_dataset = torchvision.datasets.EMNIST(
        root='./data', split='letters', train=False,
        download=True, transform=transform
    )

    # Сабсэмплинг
    if len(original_train) > MAX_TRAIN_SAMPLES:
        indices = torch.randperm(len(original_train),
                                 generator=torch.Generator().manual_seed(RANDOM_SEED))
        original_train = Subset(original_train, indices[:MAX_TRAIN_SAMPLES].tolist())

    # Разделение train/val (90/10)
    train_size = int(0.9 * len(original_train))
    val_size = len(original_train) - train_size
    train_dataset, val_dataset = random_split(
        original_train, [train_size, val_size],
        generator=torch.Generator().manual_seed(RANDOM_SEED)
    )

    # DataLoader
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)
    print(f"Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")
    print(f"Image shape: {train_dataset[0][0].shape}")
    return train_loader, val_loader, test_loader

### Вспомогательные функции
def train_epoch(model, train_loader, criterion, optimizer, device):
    """Одна эпоха обучения"""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        labels = labels - 1

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
    return running_loss / len(train_loader), 100. * correct / total


def evaluate(model, loader, device):
    """Оценка на валидационной/тестовой выборке"""
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for inputs, labels in loader:
            inputs, labels = inputs.to(device), labels.to(device)
            labels = labels - 1

            outputs = model(inputs)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

    return 100. * correct / total


def plot_results(train_losses, val_accuracies, random_guess_acc, filename, title):
    """Визуализация результатов обучения"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].plot(range(1, len(train_losses) + 1), train_losses, 'b-', linewidth=2, label='Train Loss')
    axes[0].set_xlabel('Эпоха')
    axes[0].set_ylabel('Loss')
    axes[0].set_title(f'Train Loss ({title})')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    axes[1].plot(range(1, len(val_accuracies) + 1), val_accuracies, 'g-', linewidth=2, label='Val Accuracy')
    axes[1].axhline(y=random_guess_acc, color='r', linestyle='--', label=f'Random ({random_guess_acc:.1f}%)')
    axes[1].set_xlabel('Эпоха')
    axes[1].set_ylabel('Accuracy (%)')
    axes[1].set_title(f'Val Accuracy ({title})')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.show()


class BaselineCNN(nn.Module):
    """Базовая CNN для Задания 1"""
    def __init__(self, num_classes=26):
        super(BaselineCNN, self).__init__()

        # Свёрточные слои
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(2, 2)

        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(2, 2)

        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(2, 2)

        self.dropout2d = nn.Dropout2d(p=0.25)

        # Полносвязные слои
        self.fc1 = nn.Linear(128 * 3 * 3, 256)
        self.dropout = nn.Dropout(p=0.3)
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):
        x = self.pool1(torch.relu(self.bn1(self.conv1(x))))
        x = self.pool2(torch.relu(self.bn2(self.conv2(x))))
        x = self.pool3(torch.relu(self.bn3(self.conv3(x))))
        x = self.dropout2d(x)
        x = x.view(-1, 128 * 3 * 3)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


def run_task1(train_loader, val_loader, test_loader, device):
    print("Задание 1: базовая CNN")
    model = BaselineCNN(num_classes=NUM_CLASSES).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Обучение
    NUM_EPOCHS = 25
    patience = 5
    train_losses = []
    val_accuracies = []
    best_val_acc = 0
    best_model_state = None
    no_improve_count = 0

    print(f"{'Эпоха':<8} | {'Train Loss':<12} | {'Train Acc':<12} | {'Val Acc':<12}")
    print("-" * 70)

    for epoch in range(1, NUM_EPOCHS + 1):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_acc = evaluate(model, val_loader, device)

        train_losses.append(train_loss)
        val_accuracies.append(val_acc)

        print(f"{epoch:<8} | {train_loss:<12.4f} | {train_acc:<12.2f} | {val_acc:<12.2f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_state = deepcopy(model.state_dict())
            no_improve_count = 0
        else:
            no_improve_count += 1
            if no_improve_count >= patience:
                print(f"\nEarly stopping на эпохе {epoch}")
                break

    if best_model_state:
        model.load_state_dict(best_model_state)

    # Финальная оценка на тесте
    test_acc = evaluate(model, test_loader, device)
    random_guess_acc = 100.0 / NUM_CLASSES

    # Визуализация
    plot_results(train_losses, val_accuracies, random_guess_acc,
                 'task1_baseline_results.png', 'Baseline')

    print("\n" + "=" * 70)
    print("Результаты задания 1")
    print("=" * 70)
    print(f"Best Val Accuracy: {best_val_acc:.2f}%")
    print(f"Test Accuracy:     {test_acc:.2f}%")
    print(f"Random Guess:      {random_guess_acc:.2f}%")
    print(f"Improvement:       {test_acc / random_guess_acc:.2f}×")
    print("=" * 70 + "\n")

    return test_acc, best_val_acc


# Улучшенная CNN с аугментацией
class ImprovedCNN(nn.Module):
    """Улучшенная CNN для Задания 2"""

    def __init__(self, num_classes=26):
        super(ImprovedCNN, self).__init__()

        # 4 свёрточных слоя
        self.conv1 = nn.Conv2d(1, 32, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(2, 2)

        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(2, 2)

        self.conv3 = nn.Conv2d(64, 128, 3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(2, 2)

        self.conv4 = nn.Conv2d(128, 256, 3, padding=1)
        self.bn4 = nn.BatchNorm2d(256)
        self.pool4 = nn.MaxPool2d(2, 2)

        self.dropout2d = nn.Dropout2d(p=0.3)

        # Полносвязные слои
        self.fc1 = nn.Linear(256 * 1 * 1, 512)
        self.bn_fc = nn.BatchNorm1d(512)
        self.dropout = nn.Dropout(p=0.4)
        self.fc2 = nn.Linear(512, num_classes)

    def forward(self, x):
        x = self.pool1(torch.relu(self.bn1(self.conv1(x))))
        x = self.pool2(torch.relu(self.bn2(self.conv2(x))))
        x = self.pool3(torch.relu(self.bn3(self.conv3(x))))
        x = self.pool4(torch.relu(self.bn4(self.conv4(x))))
        x = self.dropout2d(x)
        x = x.view(-1, 256 * 1 * 1)
        x = torch.relu(self.bn_fc(self.fc1(x)))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


def get_augmented_loaders():
    """Создание DataLoader с аугментацией для Задания 2"""
    print("Задание 2: аугментация данных")

    # RandomErasing после ToTensor()
    train_transform = transforms.Compose([
        transforms.RandomRotation(degrees=10),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
        transforms.ToTensor(),  # конвертируем в тензор
        transforms.RandomErasing(p=0.1, scale=(0.02, 0.1)),
        transforms.Normalize((0.5,), (0.5,))
    ])

    # Без аугментаций для val/test
    val_test_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    # Загрузка
    original_train = torchvision.datasets.EMNIST(
        root='./data', split='letters', train=True,
        download=True, transform=train_transform
    )
    test_dataset = torchvision.datasets.EMNIST(
        root='./data', split='letters', train=False,
        download=True, transform=val_test_transform
    )

    # Сабсэмплинг
    if len(original_train) > MAX_TRAIN_SAMPLES:
        indices = torch.randperm(len(original_train),
                                 generator=torch.Generator().manual_seed(RANDOM_SEED))
        original_train = Subset(original_train, indices[:MAX_TRAIN_SAMPLES].tolist())

    # Разделение
    train_size = int(0.9 * len(original_train))
    val_size = len(original_train) - train_size

    val_dataset_raw = torchvision.datasets.EMNIST(
        root='./data', split='letters', train=True,
        download=False, transform=val_test_transform
    )

    train_dataset = Subset(original_train, list(range(train_size)))
    val_dataset = Subset(val_dataset_raw, list(range(train_size, train_size + val_size)))

    # DataLoader
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # Визуализация аугментаций
    visualize_augmentations(train_transform, val_test_transform)
    return train_loader, val_loader, test_loader


def visualize_augmentations(train_transform, val_test_transform):
    """Визуализация аугментированных изображений"""
    base_dataset = torchvision.datasets.EMNIST(
        root='./data', split='letters', train=True,
        download=False, transform=val_test_transform
    )
    aug_dataset = torchvision.datasets.EMNIST(
        root='./data', split='letters', train=True,
        download=False, transform=train_transform
    )

    fig, axes = plt.subplots(2, 5, figsize=(15, 6))

    for i in range(5):
        img, label = base_dataset[i]
        # Универсальное получение значения метки
        label_val = label.item() if hasattr(label, 'item') else int(label)
        label_char = chr(ord('A') + label_val - 1)
        axes[0, i].imshow(img.squeeze(), cmap='gray')
        axes[0, i].set_title(f"Original: {label_char}")
        axes[0, i].axis('off')

        img, label = aug_dataset[i]
        # Универсальное получение значения метки
        label_val = label.item() if hasattr(label, 'item') else int(label)
        label_char = chr(ord('A') + label_val - 1)
        axes[1, i].imshow(img.squeeze(), cmap='gray')
        axes[1, i].set_title(f"Augmented: {label_char}")
        axes[1, i].axis('off')

    plt.tight_layout()
    plt.savefig('task2_augmentation_visualization.png', dpi=150)
    plt.show()
    print("Визуализация аугментаций сохранена\n")

def run_task2(train_loader, val_loader, test_loader, device):
    print("Задание 2: Улучшенная модель")

    model = ImprovedCNN(num_classes=NUM_CLASSES).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=3)

    # Обучение
    NUM_EPOCHS = 30
    patience = 5
    train_losses = []
    val_accuracies = []
    best_val_acc = 0
    best_model_state = None
    no_improve_count = 0

    print(f"{'Эпоха':<8} | {'Train Loss':<12} | {'Train Acc':<12} | {'Val Acc':<12} | {'LR':<10}")
    print("-" * 70)

    for epoch in range(1, NUM_EPOCHS + 1):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_acc = evaluate(model, val_loader, device)
        scheduler.step(val_acc)
        current_lr = optimizer.param_groups[0]['lr']

        train_losses.append(train_loss)
        val_accuracies.append(val_acc)

        print(f"{epoch:<8} | {train_loss:<12.4f} | {train_acc:<12.2f} | {val_acc:<12.2f} | {current_lr:<10.6f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_state = deepcopy(model.state_dict())
            no_improve_count = 0
        else:
            no_improve_count += 1
            if no_improve_count >= patience:
                print(f"\nEarly stopping на эпохе {epoch}")
                break

    if best_model_state:
        model.load_state_dict(best_model_state)

    # Финальная оценка
    test_acc = evaluate(model, test_loader, device)
    random_guess_acc = 100.0 / NUM_CLASSES

    # Проверка ограничения 80%
    if best_val_acc >= 80:
        print("\nval accuracy ≥ 80%")
    else:
        print("\nval accuracy < 80%")

    # Визуализация
    plot_results(train_losses, val_accuracies, random_guess_acc,
                 'task2_improved_results.png', 'Improved')

    print("Результаты задания 2")
    print(f"Best Val Accuracy: {best_val_acc:.2f}%")
    print(f"Test Accuracy:     {test_acc:.2f}%")
    print(f"Random Guess:      {random_guess_acc:.2f}%")
    print(f"Improvement:       {test_acc / random_guess_acc:.2f}×")
    print("=" * 70 + "\n")

    return test_acc, best_val_acc


def main():
    """Основная точка входа"""
    print("Датасет: EMNIST Letters (26 классов)")

    # Подготовка данных
    train_loader, val_loader, test_loader = prepare_data()

    # Задание 1: Базовая модель
    task1_test_acc, task1_val_acc = run_task1(train_loader, val_loader, test_loader, device)

    # Задание 2: Улучшенная модель с аугментацией
    train_loader_aug, val_loader_aug, test_loader_aug = get_augmented_loaders()
    task2_test_acc, task2_val_acc = run_task2(train_loader_aug, val_loader_aug, test_loader_aug, device)

    # Итоговая таблица
    print("Итоговая таблица экспериментов")
    print(f"""
┌────────────────────────────────────────────────────────────────────────────┐
│  №  │  Модель      │  Val Acc  │  Test Acc  │  Улучшение  │  Статус        │
├────────────────────────────────────────────────────────────────────────────┤
│  0  │  Baseline    │  {task1_val_acc:>6.2f}%  │  {task1_test_acc:>6.2f}%   │  —          │  Задание 1     │
│  1  │  Improved    │  {task2_val_acc:>6.2f}%  │  {task2_test_acc:>6.2f}%   │  +{task2_test_acc - task1_test_acc:>5.2f}%    │  Задание 2     │
└────────────────────────────────────────────────────────────────────────────┘
    """)

    # Проверка требования: Test Acc Задания 2 > Задания 1
    if task2_test_acc > task1_test_acc:
        print("Test Accuracy Задания 2 > Задания 1")
    else:
        print("Test Accuracy Задания 2 не превысила Задание 1")

    print("Work is done:)")


if __name__ == "__main__":
    main()