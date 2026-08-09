import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.datasets as datasets
import torchvision.transforms as transforms


class Autoencoder(nn.Module):
    def __init__(self):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(1, 10, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, stride=2),
            nn.Conv2d(10, 20, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.Dropout(p=0.25),
            nn.MaxPool2d(2, stride=2),
            nn.Flatten(),
            nn.LazyLinear(300)
        )
        self.decoder = nn.Sequential(
            nn.Linear(300, 20 * 13 * 13),
            nn.ReLU(),
            nn.Unflatten(1, (20, 13, 13)),               # -> 20 x 13 x 13

            nn.Upsample(size=27, mode='nearest'),        # 13 -> 27
            nn.Conv2d(20, 10, 3, stride=1, padding=1),
            nn.ReLU(),

            nn.Upsample(size=53, mode='nearest'),        # 27 -> 53
            nn.Conv2d(10, 10, 3, stride=1, padding=1),
            nn.ReLU(),

            nn.Upsample(size=107, mode='nearest'),       # 53 -> 107
            nn.Conv2d(10, 10, 3, stride=1, padding=1),
            nn.ReLU(),

            nn.Upsample(size=214, mode='nearest'),       # 107 -> 214
            nn.Conv2d(10, 1, 3, stride=1, padding=1),
            nn.Hardtanh(min_val=0, max_val=10000)
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x
    def encode(self, x):
        return self.encoder(x)

class SparseHistogramAutoencoder(nn.Module):
    def __init__(self, latent_dim=128):
        super(SparseHistogramAutoencoder, self).__init__()

        # 1. Encoder: Extract spatial patterns from the 2D grid
        # Assumes input shape is (Batch, 1, 32, 32)
        self.encoder_conv = nn.Sequential(
            nn.Conv2d(1, 10, kernel_size=3, stride=2, padding=1),
            nn.LeakyReLU(0.2),
            nn.MaxPool2d(2, stride=2),
            nn.Conv2d(10, 20, kernel_size=3, stride=2, padding=1),
            nn.LeakyReLU(0.2),
            nn.MaxPool2d(2, stride=2),
            nn.LeakyReLU(0.2),
            nn.Flatten()
        )
        self.encoder_linear = nn.LazyLinear(latent_dim)

        # 2. Shared Decoder Backbone
        self.decoder_linear = nn.Linear(latent_dim, 20 * 13 * 13)
        self.decoder_conv = nn.Sequential(

            nn.ConvTranspose2d(20, 10, kernel_size=5, stride=4, padding=1, output_padding=2), # -> (32, 8, 8)
            nn.LeakyReLU(0.2),
        )

        # 3. Dual-Headed Output Layers (both map from 16 channels to 1 channel)
        # Head 1: Predicts a probability mask of which bins are active (0 to 1)
        self.mask_head = nn.ConvTranspose2d(10, 1, kernel_size=6, stride=4, padding=1, output_padding=2)

        # Head 2: Predicts raw count values (forces >= 0 using ReLU)
        self.intensity_head = nn.Sequential(
            nn.ConvTranspose2d(10, 1, kernel_size=6, stride=4, padding=1, output_padding=2),
            nn.ReLU()
        )

    def forward(self, x):
        # Pass through encoder
        features = self.encoder_conv(x)
        latent = self.encoder_linear(features)

        # Pass through shared decoder
        x_recon = self.decoder_linear(latent)
        x_recon = x_recon.view(-1, 20, 13, 13)
        shared_features = self.decoder_conv(x_recon)

        # Compute Head 1: Mask logits (leave raw for BCEWithLogitsLoss during training)
        mask_logits = self.mask_head(shared_features)

        # Compute Head 2: Intensities
        intensities = self.intensity_head(shared_features)

        # For evaluation/inference, calculate final prediction
        with torch.no_grad():
            mask_probs = torch.sigmoid(mask_logits)
            # Binary gate: Zero out intensities where the mask probability is less than 50%
            final_recon = intensities * (mask_probs > 0.5).float()

        return mask_logits, intensities, final_recon

    def encode(self, x):
        x = self.encoder_conv(x)
        z = self.encoder_linear(x)
        return z