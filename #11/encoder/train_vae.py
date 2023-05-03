"""
Import necessary libraries to create a variational autoencoder
The code is mainly developed using the PyTorch library
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from torchvision.utils import save_image
from PIL import Image
from model import VAE
from torchvision.transforms import Compose, ToPILImage, ToTensor, Resize


"""
Determine if any GPUs are available
"""
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


"""
Initialize Hyperparameters
"""
BATCH_SIZE = 128
LEARNING_RATE = 1e-3
NUM_EPOCHS = 100
DIR_PATH_INPUT = "../data/train/input"
DIR_PATH_OUTPUT = "../data/train/output"



WEIGHTS_PATH = "../weights/encoder_weights.pth"


"""
Create dataloaders to feed data into the neural network
Default MNIST dataset is used and standard train/test split is performed
"""

# Создание наборов данных и загрузчиков
train_transforms = Compose([
    Resize((512, 512)),
    ToTensor()
])


train_dataset = MyDataset(DIR_PATH_INPUT, DIR_PATH_OUTPUT, transform=train_transforms)
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

"""
Initialize the network and the Adam optimizer
"""
net = VAE().to(device)
optimizer = torch.optim.Adam(net.parameters(), lr=LEARNING_RATE)


"""
Training the network for a given number of epochs
The loss after every epoch is printed
"""
for epoch in range(NUM_EPOCHS):
    for idx, data in enumerate(train_loader, 0):
        imgs, _ = data
        imgs = imgs.to(device)

        # Feeding a batch of images into the network to obtain the output image, mu, and logVar
        out, mu, logVar = net(imgs)

        # The loss is the BCE loss combined with the KL divergence to ensure the distribution is learnt
        kl_divergence = -0.5 * torch.sum(1 + logVar - mu.pow(2) - logVar.exp())
        loss = F.binary_cross_entropy(out, imgs, size_average=False) + kl_divergence

        # Backpropagation based on the loss
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print('Epoch {}: Loss {}'.format(epoch, loss))
torch.save(net.state_dict(), WEIGHTS_PATH)

