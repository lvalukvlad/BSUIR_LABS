import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split, Subset
import torchvision
import torchvision.transforms as transforms
import torchvision.models as models
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import os
import time
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import cv2
os.makedirs('results', exist_ok=True)

RANDOM_SEED = 42
BATCH_SIZE = 64
NUM_CLASSES = 10
MAX_TRAIN_SAMPLES = 10000
NUM_EPOCHS = 15
patience = 3

# ImageNet-статистики для претренированных моделей
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

torch.manual_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed(RANDOM_SEED)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Device: {device}")

# Подготовка данных
def prepare_data_svhn():
    """Подготовка SVHN с правильными трансформациями"""
    print("\nПодготовка данных SVHN")

    train_transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.RandomRotation(10),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    val_test_transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    full_train = torchvision.datasets.SVHN(
        root='./data', split='train', download=True, transform=train_transform
    )
    test_dataset = torchvision.datasets.SVHN(
        root='./data', split='test', download=True, transform=val_test_transform
    )

    print(f"SVHN original train: {len(full_train)}, test: {len(test_dataset)}")

    # Сабсэмплинг для ускорения
    MAX_TRAIN_SAMPLES = 10000
    if len(full_train) > MAX_TRAIN_SAMPLES:
        indices = torch.randperm(len(full_train), generator=torch.Generator().manual_seed(RANDOM_SEED))
        full_train = Subset(full_train, indices[:MAX_TRAIN_SAMPLES].tolist())

    TEST_SAMPLES = 5000
    if len(test_dataset) > TEST_SAMPLES:
        test_indices = torch.randperm(len(test_dataset), generator=torch.Generator().manual_seed(RANDOM_SEED))
        test_dataset = Subset(test_dataset, test_indices[:TEST_SAMPLES].tolist())

    # Разделение train/val (90/10)
    train_size = int(0.9 * len(full_train))
    val_size = len(full_train) - train_size
    train_dataset, val_dataset = random_split(
        full_train, [train_size, val_size],
        generator=torch.Generator().manual_seed(RANDOM_SEED)
    )

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)

    print(f"Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")
    print(f"Image shape: {train_dataset[0][0].shape}")
    return train_loader, val_loader, test_loader, train_dataset, test_dataset

# Функции обучения и оценки
def train_epoch(model, train_loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)

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
    model.eval()
    correct = 0
    total = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    return 100. * correct / total, all_preds, all_labels


def count_trainable_params(model):
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    return trainable, total


def plot_training(train_losses, val_accs, filename, title):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].plot(range(1, len(train_losses) + 1), train_losses, 'b-', linewidth=2)
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title(f'Train Loss - {title}')
    axes[0].grid(True, alpha=0.3)

    random_guess = 100.0 / NUM_CLASSES
    axes[1].plot(range(1, len(val_accs) + 1), val_accs, 'g-', linewidth=2, label='Val Acc')
    axes[1].axhline(y=random_guess, color='r', linestyle='--', label=f'Random ({random_guess:.1f}%)')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy (%)')
    axes[1].set_title(f'Validation Accuracy - {title}')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

# Задание 1: три модели для сравнения
def create_model_a_from_scratch():
    """Модель A: Обучение с нуля"""
    print("\nМодель А: Обучение с нуля")

    class CNNFromScratch(nn.Module):
        def __init__(self, num_classes=10):
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv2d(3, 16, 3, padding=1), nn.BatchNorm2d(16), nn.ReLU(), nn.MaxPool2d(2, 2),
                nn.Conv2d(16, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2, 2),
                nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2, 2),
            )
            self.classifier = nn.Sequential(
                nn.Dropout(0.3), nn.Linear(256 * 4 * 4, 512), nn.ReLU(),
                nn.Dropout(0.3), nn.Linear(512, num_classes)
            )

        def forward(self, x):
            x = self.features(x)
            x = x.view(x.size(0), -1)
            x = self.classifier(x)
            return x

    model = CNNFromScratch(num_classes=NUM_CLASSES).to(device)
    return model

def create_model_b_frozen_pretrained():
    """Модель B: ResNet18 с замороженными слоями"""
    print("\nМодель B: ResNet18")
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

    # Заморозить все параметры
    for param in model.parameters():
        param.requires_grad = False

    # Заменить классификационную голову
    num_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(num_features, 256),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(256, NUM_CLASSES)
    )
    model = model.to(device)
    return model


def create_model_c_finetuning():
    """Модель C: ResNet18 с файнтюнингом"""
    print("\nМодель С: ResNet18 (Fine-Tuning)")
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

    # Заменить классификационную голову
    num_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(num_features, 256),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(256, NUM_CLASSES)
    )
    model = model.to(device)
    return model


def train_model(model, train_loader, val_loader, test_loader, device, model_name, num_epochs=15):
    """Обучение модели с отслеживанием метрик"""
    criterion = nn.CrossEntropyLoss()

    # Для Model C: раздельный learning rate для backbone и head
    if model_name == "C (Fine-tuning)":
        backbone_params = [p for name, p in model.named_parameters() if 'fc' not in name]
        head_params = model.fc.parameters()
        optimizer = optim.Adam([
            {'params': backbone_params, 'lr': 1e-4},
            {'params': head_params, 'lr': 1e-3}
        ])
    else:
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=0.001)

    scheduler  = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.5)
    train_losses = []
    val_accuracies = []
    best_val_acc = 0
    best_model_state = None
    epoch_times = []
    print(f"\n{'Epoch':<8} | {'Train Loss':<12} | {'Val Acc':<12} | {'Time':<10}")
    print("-" * 70)

    for epoch in range(1, num_epochs + 1):
        start_time = time.time()
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_acc, _, _ = evaluate(model, val_loader, device)
        scheduler.step()
        epoch_time = time.time() - start_time
        epoch_times.append(epoch_time)
        train_losses.append(train_loss)
        val_accuracies.append(val_acc)

        print(f"{epoch:<8} | {train_loss:<12.4f} | {val_acc:<12.2f}% | {epoch_time:<10.2f}s")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_state = deepcopy(model.state_dict())

    if best_model_state:
        model.load_state_dict(best_model_state)

    test_acc, test_preds, test_labels = evaluate(model, test_loader, device)
    trainable_params, total_params = count_trainable_params(model)
    avg_epoch_time = np.mean(epoch_times)

    print(f"\n✅ {model_name} завершена:")
    print(f"   Best Val Accuracy: {best_val_acc:.2f}%")
    print(f"   Test Accuracy:     {test_acc:.2f}%")
    print(f"   Trainable Params:  {trainable_params:,} / {total_params:,}")
    print(f"   Avg Epoch Time:    {avg_epoch_time:.2f}s")

    plot_training(train_losses, val_accuracies, f'results/training_{model_name.replace(" ", "_")}.png', model_name)

    return {
        'model': model,
        'val_acc': best_val_acc,
        'test_acc': test_acc,
        'trainable_params': trainable_params,
        'total_params': total_params,
        'avg_epoch_time': avg_epoch_time,
        'epochs': num_epochs,
        'test_preds': test_preds,
        'test_labels': test_labels
    }

# Задание 2: Интерпретируемость
class GradCAM:
    """Grad-CAM для визуализации важности областей изображения"""
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self.hook_layers()

    def hook_layers(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()
        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate_cam(self, input_tensor, target_class):
        self.model.eval()
        output = self.model(input_tensor)
        self.model.zero_grad()
        one_hot = torch.zeros_like(output)
        one_hot[0][target_class] = 1
        output.backward(gradient=one_hot, retain_graph=True)
        pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])
        for i in range(self.activations.shape[1]):
            self.activations[:, i, :, :] *= pooled_gradients[i]
        heatmap = torch.mean(self.activations, dim=1).squeeze()
        heatmap = torch.relu(heatmap)
        heatmap /= torch.max(heatmap) + 1e-8
        return heatmap.cpu().numpy()


def visualize_filters(model, filename='results/filter_visualization.png'):
    """Часть A: Визуализация фильтров первого свёрточного слоя"""
    print("\nЧасть А: Визуализация фильтров первого слоя")

    # Для ResNet первый conv слой - model.conv1
    if hasattr(model, 'conv1'):
        filters = model.conv1.weight.data.cpu()
    else:
        # Для custom CNN
        filters = model.features[0].weight.data.cpu()

    # Первые 16 фильтров
    num_filters = min(16, filters.shape[0])
    fig, axes = plt.subplots(4, 4, figsize=(10, 10))

    for i, ax in enumerate(axes.flat):
        if i < num_filters:
            filter_img = filters[i]
            if filter_img.shape[0] == 3:  # RGB
                filter_img = filter_img.permute(1, 2, 0).numpy()
            else:  # Grayscale
                filter_img = filter_img.squeeze().numpy()
            filter_img = (filter_img - filter_img.min()) / (filter_img.max() - filter_img.min() + 1e-8)
            ax.imshow(filter_img)
        ax.axis('off')

    plt.suptitle('First Layer Filters', fontsize=14)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"✅ Фильтры сохранены в {filename}")


def visualize_activations(model, test_loader, device, filename='results/activation_maps.png'):
    """Часть B: Визуализация карт активаций"""
    print("Часть B: Визуализация карт активаций")
    activations = {}

    def hook_fn(name):
        def hook(module, input, output):
            activations[name] = output.detach().cpu()
        return hook

    # Регистрация хуков для разных слоёв
    if hasattr(model, 'layer1'):
        model.layer1.register_forward_hook(hook_fn('layer1'))
        model.layer3.register_forward_hook(hook_fn('layer3'))
    elif hasattr(model, 'features'):
        model.features[2].register_forward_hook(hook_fn('early'))
        model.features[10].register_forward_hook(hook_fn('deep'))

    model.eval()
    images, labels = next(iter(test_loader))
    images, labels = images.to(device), labels.to(device)

    with torch.no_grad():
        output = model(images[0:1])
    fig, axes = plt.subplots(2, 8, figsize=(16, 4))

    # Визуализация 8 каналов активаций
    for idx, (name, act) in enumerate(activations.items()):
        act_img = act[0, :8].cpu().numpy()  # Первые 8 каналов
        for i in range(8):
            ax = axes[idx, i]
            ax.imshow(act_img[i], cmap='gray')
            ax.axis('off')
            if i == 0:
                ax.set_ylabel(f'{name}')

    plt.suptitle('Activation Maps (Early vs Deep Layers)', fontsize=14)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"✅ Карты активаций сохранены в {filename}")


def visualize_gradcam(model, test_loader, device, filename='results/grad_cam_visualization.png'):
    """Часть C: Grad-CAM для 8 изображений"""
    print("\nЧасть C: Grad-CAM визуализация")

    # Определение целевого слоя для Grad-CAM
    if hasattr(model, 'layer3'):
        target_layer = model.layer3[-1]
    elif hasattr(model, 'features'):
        target_layer = model.features[-3]
    else:
        print("⚠️ Не удалось найти целевой слой для Grad-CAM")
        return

    grad_cam = GradCAM(model, target_layer)

    # Сбор правильных и неправильных предсказаний
    correct_imgs = []
    incorrect_imgs = []

    model.eval()
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            preds = outputs.argmax(dim=1)

            for i in range(len(inputs)):
                if preds[i] == labels[i]:
                    if len(correct_imgs) < 4:
                        correct_imgs.append((inputs[i:i + 1], labels[i].item(), preds[i].item()))
                else:
                    if len(incorrect_imgs) < 4:
                        incorrect_imgs.append((inputs[i:i + 1], labels[i].item(), preds[i].item()))

            if len(correct_imgs) >= 4 and len(incorrect_imgs) >= 4:
                break

    # Визуализация
    fig, axes = plt.subplots(4, 4, figsize=(16, 12))

    all_samples = [(correct_imgs, "Correct"), (incorrect_imgs, "Incorrect")]

    for row_idx, (samples, status) in enumerate(all_samples):
        for col_idx, (input_img, true_label, pred_label) in enumerate(samples[:4]):
            heatmap = grad_cam.generate_cam(input_img, pred_label)

            original_img = input_img.cpu().squeeze().permute(1, 2, 0).numpy()
            original_img = (original_img - original_img.min()) / (original_img.max() - original_img.min() + 1e-8)

            heatmap_resized = cv2.resize(heatmap, (original_img.shape[1], original_img.shape[0]))
            heatmap_color = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
            heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB).astype(float) / 255

            superimposed = heatmap_color * 0.4 + original_img * 0.6

            ax = axes[row_idx * 2, col_idx]
            ax.imshow(original_img)
            ax.set_title(f"True: {true_label}, Pred: {pred_label}")
            ax.axis('off')

            ax = axes[row_idx * 2 + 1, col_idx]
            ax.imshow(superimposed)
            ax.set_title(f"Grad-CAM ({status})")
            ax.axis('off')

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"✅ Grad-CAM сохранён в {filename}")


def plot_confusion_matrix(test_labels, test_preds, filename='results/confusion_matrix.png'):
    """Часть D: Матрица ошибок"""
    print("Часть D: Матрица ошибок")

    class_names = [str(i) for i in range(NUM_CLASSES)]
    cm = confusion_matrix(test_labels, test_preds)

    plt.figure(figsize=(10, 10))
    disp = ConfusionMatrixDisplay(cm, display_labels=class_names)
    disp.plot(xticks_rotation=45, cmap='Blues')
    plt.title("Confusion Matrix - SVHN")
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"✅ Матрица ошибок сохранена в {filename}")

    # Анализ топ-3 ошибок
    np.fill_diagonal(cm, 0)
    error_pairs = []
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            if cm[i, j] > 0:
                error_pairs.append((i, j, cm[i, j]))

    error_pairs.sort(key=lambda x: x[2], reverse=True)

    print("\nПары классов, которые модель путает чаще всего:")
    for i, (true_class, pred_class, count) in enumerate(error_pairs[:3]):
        print(f"   {i + 1}. Класс {true_class} → Класс {pred_class}: {count} ошибок")

    return error_pairs[:3]

def main():
    print("\nTRANSFER LEARNING И ИНТЕРПРЕТИРУЕМОСТЬ")
    print(f"Датасет: SVHN ({NUM_CLASSES} классов)")
    print(f"Нормализация: ImageNet (mean={IMAGENET_MEAN}, std={IMAGENET_STD})")
    print(f"Размер изображений: 64×64")

    # Подготовка данных
    train_loader, val_loader, test_loader, train_dataset, test_dataset = prepare_data_svhn()

    # Задание 1: Сравнение трёх моделей
    results = {}

    # Модель A: Обучение с нуля
    model_a = create_model_a_from_scratch()
    results['A'] = train_model(model_a, train_loader, val_loader, test_loader, device,
                               "A (From Scratch)", num_epochs=15)

    # Модель B: Frozen ResNet18
    model_b = create_model_b_frozen_pretrained()
    results['B'] = train_model(model_b, train_loader, val_loader, test_loader, device,
                               "B (Frozen)", num_epochs=15)

    # Модель C: Fine-tuning
    model_c = create_model_c_finetuning()
    results['C'] = train_model(model_c, train_loader, val_loader, test_loader, device,
                               "C (Fine-tuning)", num_epochs=15)

    # Таблица сравнения
    print("\n" + "=" * 70)
    print("Итоговая таблица сравнения моделей")
    print("=" * 70)

    print(f"""
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│  №  │  Модель              │  Параметры  │  Время/эпоху  │  Эпохи  │  Val Acc   │  Test Acc   │
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│  A  │  From Scratch        │  {results['A']['trainable_params']:>10,}  │  {results['A']['avg_epoch_time']:>8.2f}s   │  {results['A']['epochs']:>5}  │  {results['A']['val_acc']:>7.2f}%  │  {results['A']['test_acc']:>8.2f}%  │
│  B  │  Frozen Pretrained   │  {results['B']['trainable_params']:>10,}  │  {results['B']['avg_epoch_time']:>8.2f}s   │  {results['B']['epochs']:>5}  │  {results['B']['val_acc']:>7.2f}%  │  {results['B']['test_acc']:>8.2f}%  │
│  C  │  Fine-tuning         │  {results['C']['trainable_params']:>10,}  │  {results['C']['avg_epoch_time']:>8.2f}s   │  {results['C']['epochs']:>5}  │  {results['C']['val_acc']:>7.2f}%  │  {results['C']['test_acc']:>8.2f}%  │
└───────────────────────────────────────────────────────────────────────────────────────────────┘
    """)

    # Лучшая модель
    best_model_key = max(results, key=lambda x: results[x]['test_acc'])
    best_model = results[best_model_key]['model']
    print(f"\nЛучшая модель: {best_model_key} (Test Accuracy: {results[best_model_key]['test_acc']:.2f}%)")

    # Задание 2: интерпретируемость для лучшей модели

    print("\nЗадание 2: Интерпретируемость")

    visualize_filters(best_model)
    visualize_activations(best_model, test_loader, device)
    visualize_gradcam(best_model, test_loader, device)
    top_errors = plot_confusion_matrix(results[best_model_key]['test_labels'],
                                       results[best_model_key]['test_preds'])

    print("Результаты сохранены в папке results/:")
    print("  • training_*.png — графики обучения для каждой модели")
    print("  • filter_visualization.png — фильтры первого слоя")
    print("  • activation_maps.png — карты активаций")
    print("  • grad_cam_visualization.png — Grad-CAM для 8 изображений")
    print("  • confusion_matrix.png — матрица ошибок")

if __name__ == "__main__":
    main()