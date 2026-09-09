import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms, models, datasets
from torchvision.utils import save_image
from PIL import Image
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

torch.manual_seed(42)

device = torch.device("cpu")
print(f"{'=' * 70}")
print(f"Generative Image Models")
print(f"Device: {device}")
print(f"{'=' * 70}")


# Neural Style Transfer
print("\n")
print("Neural Style Transfer")
print("=" * 70)

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def load_image(path, size=256):
    image = Image.open(path).convert("RGB")
    transform = transforms.Compose(
        [
            transforms.Resize((size, size)),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]
    )
    return transform(image).unsqueeze(0)


def denormalize(tensor):
    mean = torch.tensor(IMAGENET_MEAN).view(3, 1, 1)
    std = torch.tensor(IMAGENET_STD).view(3, 1, 1)
    img = tensor.clone().squeeze(0).cpu()
    img = img * std + mean
    return img.clamp(0, 1).permute(1, 2, 0).numpy()


print("\nLoading VGG19...")
vgg = models.vgg19(weights=models.VGG19_Weights.DEFAULT).features.to(device)
for param in vgg.parameters():
    param.requires_grad = False
vgg.eval()
print("VGG19 loaded")

style_layers = {"conv1_1": 0, "conv2_1": 5, "conv3_1": 10, "conv4_1": 19, "conv5_1": 28}
content_layers = {"conv4_2": 21}
all_layers = {**style_layers, **content_layers}


def get_features(image, model, layers):
    idx_to_name = {v: k for k, v in layers.items()}
    max_idx = max(idx_to_name.keys())
    features = {}
    x = image
    for i, layer in enumerate(model):
        x = layer(x)
        if i in idx_to_name:
            features[idx_to_name[i]] = x
        if i == max_idx:
            break
    return features


def content_loss(generated_features, content_features):
    return F.mse_loss(generated_features, content_features)


def gram_matrix(features):
    b, c, h, w = features.shape
    F = features.view(b, c, h * w)
    G = torch.bmm(F, F.transpose(1, 2))
    return G / (c * h * w)


def style_loss(generated_features, style_features):
    G_gen = gram_matrix(generated_features)
    G_style = gram_matrix(style_features)
    return F.mse_loss(G_gen, G_style)


def run_style_transfer(
    content_path,
    style_path,
    output_path,
    img_size=256,
    num_steps=300,
    alpha=1,
    beta=1e5,
):
    print(
        f"\nStyle Transfer: {os.path.basename(content_path)} + {os.path.basename(style_path)}"
    )
    print(f"{'=' * 60}")

    content_img = load_image(content_path, size=img_size).to(device)
    style_img = load_image(style_path, size=img_size).to(device)

    generated = content_img.clone().requires_grad_(True)

    with torch.no_grad():
        content_features = get_features(content_img, vgg, all_layers)
        style_features = get_features(style_img, vgg, all_layers)

    optimizer = optim.LBFGS([generated], lr=1.0, max_iter=20)

    mean = torch.tensor(IMAGENET_MEAN, device=device).view(1, 3, 1, 1)
    std = torch.tensor(IMAGENET_STD, device=device).view(1, 3, 1, 1)

    def closure():
        optimizer.zero_grad()
        gen_features = get_features(generated, vgg, all_layers)
        c_loss = content_loss(gen_features["conv4_2"], content_features["conv4_2"])
        s_loss = sum(
            style_loss(gen_features[layer], style_features[layer])
            for layer in style_layers
        )
        total_loss = alpha * c_loss + beta * s_loss
        total_loss.backward()
        closure.last_losses = (total_loss, c_loss, s_loss)
        return total_loss

    print(f"Optimization ({num_steps} steps)...")
    for step in range(num_steps):
        optimizer.step(closure)
        with torch.no_grad():
            generated.data = (generated.data * std + mean).clamp(0, 1)
            generated.data = (generated.data - mean) / std
        if step % 50 == 0 or step == num_steps - 1:
            total_loss, c_loss, s_loss = closure.last_losses
            print(
                f"Step {step:3d}: total={total_loss.item():.4f}, content={c_loss.item():.4f}, style={s_loss.item():.4f}"
            )

    os.makedirs(
        os.path.dirname(output_path) if os.path.dirname(output_path) else ".",
        exist_ok=True,
    )
    result = (generated.data * std + mean).clamp(0, 1)
    save_image(result, output_path)
    print(f"Result saved: {output_path}")

    return generated


def create_test_images():
    os.makedirs("data/nst", exist_ok=True)
    content = np.zeros((256, 256, 3), dtype=np.uint8)
    content[64:192, 64:192] = [255, 200, 100]
    Image.fromarray(content).save("data/nst/content.png")

    style = np.zeros((256, 256, 3), dtype=np.uint8)
    for i in range(0, 256, 32):
        for j in range(0, 256, 32):
            if (i // 32 + j // 32) % 2 == 0:
                style[i : i + 32, j : j + 32] = [200, 50, 50]
            else:
                style[i : i + 32, j : j + 32] = [50, 50, 200]
    Image.fromarray(style).save("data/nst/style.png")
    print("Test images created in data/nst/")


# Проверка наличия изображений
if not os.path.exists("data/nst/content.png") or not os.path.exists(
    "data/nst/style.png"
):
    print("\nСоздание тестовых изображений...")
    create_test_images()

# Запуск Style Transfer
print("\n")
print("Эксперимент 1. Базовый перенос стиля (β=1e5)")
print("=" * 60)
generated_1 = run_style_transfer(
    content_path="data/nst/content.png",
    style_path="data/nst/style.png",
    output_path="results/nst_result_beta1e5.png",
    img_size=256,
    num_steps=300,
    alpha=1,
    beta=1e5,
)

print("\n")
print("Эксперимент 2. Слабый стиль (β=1e3)")
print("=" * 60)
generated_2 = run_style_transfer(
    content_path="data/nst/content.png",
    style_path="data/nst/style.png",
    output_path="results/nst_result_beta1e3.png",
    img_size=256,
    num_steps=300,
    alpha=1,
    beta=1e3,
)

print("\n")
print("Эксперимент 3. Сильный стиль (β=1e7)")
print("=" * 60)
generated_3 = run_style_transfer(
    content_path="data/nst/content.png",
    style_path="data/nst/style.png",
    output_path="results/nst_result_beta1e7.png",
    img_size=256,
    num_steps=300,
    alpha=1,
    beta=1e7,
)

print("\n")
print("Эксперимент 4. Инициализация шумом")
print("=" * 60)

# Инициализация случайным шумом
content_img = load_image("data/nst/content.png", size=256).to(device)
style_img = load_image("data/nst/style.png", size=256).to(device)
generated_noise = torch.randn_like(content_img).requires_grad_(True)

with torch.no_grad():
    content_features = get_features(content_img, vgg, all_layers)
    style_features = get_features(style_img, vgg, all_layers)

optimizer = optim.LBFGS([generated_noise], lr=1.0, max_iter=20)
mean = torch.tensor(IMAGENET_MEAN, device=device).view(1, 3, 1, 1)
std = torch.tensor(IMAGENET_STD, device=device).view(1, 3, 1, 1)


def closure_noise():
    optimizer.zero_grad()
    gen_features = get_features(generated_noise, vgg, all_layers)
    c_loss = content_loss(gen_features["conv4_2"], content_features["conv4_2"])
    s_loss = sum(
        style_loss(gen_features[layer], style_features[layer]) for layer in style_layers
    )
    total_loss = c_loss + 1e5 * s_loss
    total_loss.backward()
    closure_noise.last_losses = (total_loss, c_loss, s_loss)
    return total_loss


print("Оптимизация (инициализация шумом, 300 шагов)...")
for step in range(300):
    optimizer.step(closure_noise)
    with torch.no_grad():
        generated_noise.data = (generated_noise.data * std + mean).clamp(0, 1)
        generated_noise.data = (generated_noise.data - mean) / std
    if step % 100 == 0:
        total_loss, c_loss, s_loss = closure_noise.last_losses
        print(f"Step {step}: total={total_loss.item():.4f}")

result_noise = (generated_noise.data * std + mean).clamp(0, 1)
save_image(result_noise, "results/nst_result_noise_init.png")
print("✅ Результат (шум) сохранён: results/nst_result_noise_init.png")

print("\n")
print("Часть 1 завершена!")
print("=" * 70)

print("\n")
print("DCGAN (Generative Adversarial Network)")
print("=" * 70)

print("\nLoading EMNIST dataset...")
transform = transforms.Compose(
    [
        transforms.Resize(32),
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5]),
    ]
)

dataset = datasets.EMNIST(
    root="data", split="digits", train=True, download=True, transform=transform
)

dataloader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=0)

print(f"Loaded {len(dataset)} images")
print(f"Batch size: {dataloader.batch_size}")


class Generator(nn.Module):
    def __init__(self, latent_dim=100, img_channels=1):
        super().__init__()
        self.net = nn.Sequential(
            nn.ConvTranspose2d(latent_dim, 256, 4, 1, 0, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            nn.ConvTranspose2d(256, 128, 4, 2, 1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            nn.ConvTranspose2d(128, 64, 4, 2, 1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.ConvTranspose2d(64, img_channels, 4, 2, 1, bias=False),
            nn.Tanh(),
        )

    def forward(self, z):
        return self.net(z)


class Discriminator(nn.Module):
    def __init__(self, img_channels=1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(img_channels, 64, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(64, 128, 4, 2, 1, bias=False),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(128, 256, 4, 2, 1, bias=False),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(256, 1, 4, 1, 0, bias=False),
        )

    def forward(self, img):
        return self.net(img).view(-1)


def weights_init(m):
    if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
        nn.init.normal_(m.weight, 0.0, 0.02)
    elif isinstance(m, nn.BatchNorm2d):
        nn.init.normal_(m.weight, 1.0, 0.02)
        nn.init.zeros_(m.bias)


latent_dim = 100
generator = Generator(latent_dim=latent_dim, img_channels=1).to(device)
discriminator = Discriminator(img_channels=1).to(device)
generator.apply(weights_init)
discriminator.apply(weights_init)

print(f"\nDCGAN architecture created")
print(f"Generator params: {sum(p.numel() for p in generator.parameters()):,}")
print(f"Discriminator params: {sum(p.numel() for p in discriminator.parameters()):,}")

criterion = nn.BCEWithLogitsLoss()
opt_G = optim.Adam(generator.parameters(), lr=2e-4, betas=(0.5, 0.999))
opt_D = optim.Adam(discriminator.parameters(), lr=2e-4, betas=(0.5, 0.999))

fixed_noise = torch.randn(16, latent_dim, 1, 1, device=device)

history = {"loss_D": [], "loss_G": [], "D_x": [], "D_G_z": []}

num_epochs = 15
os.makedirs("results/gan", exist_ok=True)

print(f"\n{'=' * 60}")
print(f"DCGAN TRAINING ({num_epochs} epochs)")
print(f"{'=' * 60}")

for epoch in range(num_epochs):
    epoch_loss_D = 0.0
    epoch_loss_G = 0.0
    epoch_D_x = 0.0
    epoch_D_G_z = 0.0
    num_batches = 0

    for real_images, _ in dataloader:
        batch_size = real_images.size(0)
        real_images = real_images.to(device)

        real_labels = torch.ones(batch_size, device=device)
        fake_labels = torch.zeros(batch_size, device=device)

        z = torch.randn(batch_size, latent_dim, 1, 1, device=device)
        fake_images = generator(z)

        d_real = discriminator(real_images)
        d_fake = discriminator(fake_images.detach())

        loss_real = criterion(d_real, real_labels)
        loss_fake = criterion(d_fake, fake_labels)
        loss_D = loss_real + loss_fake

        opt_D.zero_grad()
        loss_D.backward()
        opt_D.step()

        z = torch.randn(batch_size, latent_dim, 1, 1, device=device)
        fake_images = generator(z)

        d_fake_for_G = discriminator(fake_images)
        loss_G = criterion(d_fake_for_G, torch.ones(batch_size, device=device))

        opt_G.zero_grad()
        loss_G.backward()
        opt_G.step()

        epoch_loss_D += loss_D.item()
        epoch_loss_G += loss_G.item()
        epoch_D_x += torch.sigmoid(d_real).mean().item()
        epoch_D_G_z += torch.sigmoid(d_fake_for_G).mean().item()
        num_batches += 1

    history["loss_D"].append(epoch_loss_D / num_batches)
    history["loss_G"].append(epoch_loss_G / num_batches)
    history["D_x"].append(epoch_D_x / num_batches)
    history["D_G_z"].append(epoch_D_G_z / num_batches)

    print(
        f"Epoch [{epoch + 1:2d}/{num_epochs}] | loss_D={history['loss_D'][-1]:.4f} | "
        f"loss_G={history['loss_G'][-1]:.4f} | D(x)={history['D_x'][-1]:.3f} | D(G(z))={history['D_G_z'][-1]:.3f}"
    )

    if (epoch + 1) % 5 == 0 or epoch == 0:
        with torch.no_grad():
            fake = generator(fixed_noise)
            save_image(
                fake,
                f"results/gan/epoch_{epoch + 1:03d}.png",
                nrow=4,
                normalize=True,
                value_range=(-1, 1),
            )

print(f"\n{'=' * 60}")
print("TRAINING COMPLETE")
print(f"{'=' * 60}")

print("\nPlotting training history...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].plot(history["loss_D"], "r-", label="loss_D", linewidth=2)
axes[0].plot(history["loss_G"], "b-", label="loss_G", linewidth=2)
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Loss")
axes[0].set_title("Generator and Discriminator Loss")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(history["D_x"], "g-", label="D(x)", linewidth=2)
axes[1].plot(history["D_G_z"], "m-", label="D(G(z))", linewidth=2)
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("Probability")
axes[1].set_title("Discriminator Confidence")
axes[1].legend()
axes[1].grid(True, alpha=0.3)
axes[1].axhline(y=0.5, color="k", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("results/gan/training_history.png", dpi=150)
plt.close()
print("Training history: results/gan/training_history.png")

print("\nGenerating final grid...")
generator.eval()
with torch.no_grad():
    final_noise = torch.randn(64, latent_dim, 1, 1, device=device)
    final_images = generator(final_noise)
    save_image(
        final_images,
        "results/gan/final_grid.png",
        nrow=8,
        normalize=True,
        value_range=(-1, 1),
    )
print("Final grid: results/gan/final_grid.png (64 images)")

print("\nLatent space interpolation...")
z1 = torch.randn(1, latent_dim, 1, 1, device=device)
z2 = torch.randn(1, latent_dim, 1, 1, device=device)
alphas = torch.linspace(0, 1, steps=10)

with torch.no_grad():
    interp_images = []
    for a in alphas:
        z_interp = (1 - a) * z1 + a * z2
        interp_images.append(generator(z_interp))
    interp_images = torch.cat(interp_images, dim=0)
    save_image(
        interp_images,
        "results/gan/interpolation.png",
        nrow=10,
        normalize=True,
        value_range=(-1, 1),
    )
print("Interpolation: results/gan/interpolation.png")

print("\n" + "=" * 60)
print("SAVING MODELS")
print("=" * 60)

torch.save(
    {
        "generator_state_dict": generator.state_dict(),
        "discriminator_state_dict": discriminator.state_dict(),
        "optimizer_G_state_dict": opt_G.state_dict(),
        "optimizer_D_state_dict": opt_D.state_dict(),
        "history": history,
        "latent_dim": latent_dim,
        "num_epochs": num_epochs,
    },
    "results/gan/dcgan_emnist.pth",
)

print("Model saved: results/gan/dcgan_emnist.pth")

print("\n" + "=" * 70)
print("LAB 5 COMPLETE")
print("=" * 70)

print("""
+-------------------------------------------------------------------------+
|  Task 1: Neural Style Transfer                                          |
+-------------------------------------------------------------------------+
|  results/nst_result_beta1e5.png    -- basic transfer (beta=1e5)        |
|  results/nst_result_beta1e3.png    -- weak style (beta=1e3)           |
|  results/nst_result_beta1e7.png    -- strong style (beta=1e7)         |
|  results/nst_result_noise_init.png -- noise initialization            |
+-------------------------------------------------------------------------+

+-------------------------------------------------------------------------+
|  Task 2: DCGAN on EMNIST                                               |
+-------------------------------------------------------------------------+
|  results/gan/epoch_*.png           -- progress by epochs               |
|  results/gan/final_grid.png        -- 64 generated images            |
|  results/gan/interpolation.png     -- latent space interpolation      |
|  results/gan/training_history.png  -- training plots                  |
|  results/gan/dcgan_emnist.pth      -- model weights                  |
+-------------------------------------------------------------------------+
""")

print("=" * 70)
print("LAB COMPLETE")
print("=" * 70)
