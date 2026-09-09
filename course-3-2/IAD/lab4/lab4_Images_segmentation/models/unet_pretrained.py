import torch
import torch.nn as nn
import torchvision.models as models


class UNetPretrained(nn.Module):
    def __init__(self, num_classes=5, pretrained=True):
        super().__init__()
        resnet = models.resnet18(weights=models.ResNet18_Weights.DEFAULT if pretrained else None)

        # ENCODER
        self.enc1 = nn.Sequential(resnet.conv1, resnet.bn1, resnet.relu)  # H/2, 64
        self.pool1 = resnet.maxpool  # H/4, 64
        self.enc2 = resnet.layer1  # H/4, 64
        self.enc3 = resnet.layer2  # H/8, 128
        self.enc4 = resnet.layer3  # H/16, 256

        # BOTTLENECK
        self.bottleneck = self._block(256, 512)  # вход 256, выход 512

        # DECODER (3 уровня, skip к e3, e2, e1)
        # Уровень 1: 512 → 256, skip с e3 (128 каналов, H/8)
        self.up4 = nn.ConvTranspose2d(512, 256, 2, stride=2)  # H/16 → H/8
        self.dec4 = self._block(256 + 128, 256)  # ✅ skip с e3 (128)

        # Уровень 2: 256 → 128, skip с e2 (64 канала, H/4)
        self.up3 = nn.ConvTranspose2d(256, 128, 2, stride=2)  # H/8 → H/4
        self.dec3 = self._block(128 + 64, 128)  # ✅ skip с e2 (64)

        # Уровень 3: 128 → 64, skip с e1 (64 канала, H/2)
        self.up2 = nn.ConvTranspose2d(128, 64, 2, stride=2)  # H/4 → H/2
        self.dec2 = self._block(64 + 64, 64)  # ✅ skip с e1 (64)

        # Уровень 4: 64 → 64 (без skip)
        self.up1 = nn.ConvTranspose2d(64, 64, 2, stride=2)  # H/2 → H
        self.dec1 = self._block(64, 64)

        # OUTPUT
        self.out_conv = nn.Conv2d(64, num_classes, 1)

    def _block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True),
        )

    def forward(self, x):
        # Encoder
        e1 = self.enc1(x)  # [B, 64, H/2, W/2]
        e2 = self.enc2(self.pool1(e1))  # [B, 64, H/4, W/4]
        e3 = self.enc3(e2)  # [B, 128, H/8, W/8]
        e4 = self.enc4(e3)  # [B, 256, H/16, W/16]

        # Bottleneck
        b = self.bottleneck(e4)  # [B, 512, H/16, W/16]

        # Decoder + Skip-connections
        d4 = self.up4(b)  # [B, 256, H/8, W/8]
        d4 = torch.cat([d4, e3], dim=1)  # ✅ 256+128=384 (e3 имеет H/8)
        d4 = self.dec4(d4)  # [B, 256, H/8, W/8]

        d3 = self.up3(d4)  # [B, 128, H/4, W/4]
        d3 = torch.cat([d3, e2], dim=1)  # ✅ 128+64=192 (e2 имеет H/4)
        d3 = self.dec3(d3)  # [B, 128, H/4, W/4]

        d2 = self.up2(d3)  # [B, 64, H/2, W/2]
        d2 = torch.cat([d2, e1], dim=1)  # ✅ 64+64=128 (e1 имеет H/2)
        d2 = self.dec2(d2)  # [B, 64, H/2, W/2]

        d1 = self.up1(d2)  # [B, 64, H, W]
        d1 = self.dec1(d1)  # [B, 64, H, W]

        return self.out_conv(d1)

    def get_encoder_params(self):
        return [p for n, p in self.named_parameters()
                if any(x in n for x in ['enc1', 'enc2', 'enc3', 'enc4', 'pool1', 'bottleneck'])]

    def get_decoder_params(self):
        return [p for n, p in self.named_parameters()
                if not any(x in n for x in ['enc1', 'enc2', 'enc3', 'enc4', 'pool1', 'bottleneck'])]