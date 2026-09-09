import numpy as np
import torch

# Mean Intersection over Union (mIoU)
def calculate_iou(pred, target, num_classes):
    ious = []
    for cls in range(num_classes):
        pred_cls = (pred == cls)
        target_cls = (target == cls)
        intersection = (pred_cls & target_cls).sum().item()
        union = (pred_cls | target_cls).sum().item()
        iou = intersection / (union + 1e-8)
        ious.append(iou)
    return np.mean(ious), ious

# Mean Dice Score (Sørensen-Dice coefficient)
def calculate_dice(pred, target, num_classes):
    dices = []
    for cls in range(num_classes):
        pred_cls = (pred == cls)
        target_cls = (target == cls)
        intersection = (pred_cls & target_cls).sum().item()
        dice = 2 * intersection / (pred_cls.sum().item() + target_cls.sum().item() + 1e-8)
        dices.append(dice)
    return np.mean(dices), dices