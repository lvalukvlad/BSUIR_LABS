import torch
import torch.nn as nn

# U-Net с encoder-decoder и skip-connections.
class UNet(nn.Module):

    def __init__(self, in_channels=3, num_classes=5, base_filters=32):
        super().__init__()

        # ENCODER (3 уровня)
        self.enc1 = self._block(in_channels, base_filters)  # [B, 32, 128, 128]
        self.pool1 = nn.MaxPool2d(2, 2)  # [B, 32, 64, 64]

        self.enc2 = self._block(base_filters, base_filters * 2)  # [B, 64, 64, 64]
        self.pool2 = nn.MaxPool2d(2, 2)  # [B, 64, 32, 32]

        self.enc3 = self._block(base_filters * 2, base_filters * 4)  # [B, 128, 32, 32]
        self.pool3 = nn.MaxPool2d(2, 2)  # [B, 128, 16, 16]

        # BOTTLENECK
        self.bottleneck = self._block(base_filters * 4, base_filters * 8)  # [B, 256, 16, 16]

        # DECODER + SKIP-CONNECTIONS
        self.up3 = nn.ConvTranspose2d(base_filters * 8, base_filters * 4, kernel_size=2, stride=2)
        self.dec3 = self._block(base_filters * 8, base_filters * 4)  # skip: 128+128=256

        self.up2 = nn.ConvTranspose2d(base_filters * 4, base_filters * 2, kernel_size=2, stride=2)
        self.dec2 = self._block(base_filters * 4, base_filters * 2)  # skip: 64+64=128

        self.up1 = nn.ConvTranspose2d(base_filters * 2, base_filters, kernel_size=2, stride=2)
        self.dec1 = self._block(base_filters * 2, base_filters)  # skip: 32+32=64

        # OUTPUT (1×1 conv для логитов)
        self.out_conv = nn.Conv2d(base_filters, num_classes, kernel_size=1)

# Двойная свёртка: Conv → BN → ReLU → Conv → BN → ReLU
    def _block(self, in_ch, out_ch):

        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        # Encoder
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool1(e1))
        e3 = self.enc3(self.pool2(e2))

        # Bottleneck
        b = self.bottleneck(self.pool3(e3))

        # Decoder + Skip-connections
        d3 = self.up3(b)
        d3 = torch.cat([d3, e3], dim=1)  # skip-connection
        d3 = self.dec3(d3)

        d2 = self.up2(d3)
        d2 = torch.cat([d2, e2], dim=1)  # skip-connection
        d2 = self.dec2(d2)

        d1 = self.up1(d2)
        d1 = torch.cat([d1, e1], dim=1)  # skip-connection
        d1 = self.dec1(d1)

        # Output: [B, num_classes, H, W]
        return self.out_conv(d1)

# Тестирование архитектуры U-Net
def test_unet():

    print("Тестирование U-NET")
    print("=" * 70)

    model = UNet(in_channels=3, num_classes=5, base_filters=32)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    print(f"Total params: {total_params:,}")
    print(f"Trainable params: {trainable_params:,}")

    # Проверка размерностей
    x = torch.randn(1, 3, 128, 128)
    y = model(x)

    print(f"Input:  {list(x.shape)}")
    print(f"Output: {list(y.shape)}")

    assert y.shape == (1, 5, 128, 128), f"Output shape mismatch: {y.shape}"
    print("\n✅ Размерности корректны!")
    print("=" * 70)

    return model


if __name__ == "__main__":
    test_unet()