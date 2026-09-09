import torch
import numpy as np
from utils.metrics import calculate_iou, calculate_dice

#  Оценка модели: mIoU, mDice
def evaluate(model, val_loader, device, num_classes):

    model.eval()
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for images, masks in val_loader:
            images, masks = images.to(device), masks.to(device)
            logits = model(images)
            preds = logits.argmax(dim=1)  # [B, H, W]

            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(masks.cpu().numpy())

    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)

    mIoU, ious_per_class = calculate_iou(all_preds, all_targets, num_classes)
    mDice, dices_per_class = calculate_dice(all_preds, all_targets, num_classes)

    return mIoU, mDice, ious_per_class, dices_per_class