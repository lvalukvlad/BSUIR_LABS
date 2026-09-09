import torch
import torch.nn as nn

# Одна эпоха обучения
def train_epoch(model, train_loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0

    for images, masks in train_loader:
        images, masks = images.to(device), masks.to(device)

        optimizer.zero_grad()
        logits = model(images)  # [B, num_classes, H, W]
        loss = criterion(logits, masks)  # CrossEntropyLoss работает попиксельно
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    return running_loss / len(train_loader)