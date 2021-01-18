import numpy as np
import torch
import torchvision.models as models
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image

from rdv.extractors.structured.kmeans import KMeansOutlierScorer

# Loosely based on "Deep Nearest Neighbor Anomaly Detection": https://arxiv.org/abs/2002.10445


class ImageDataset(Dataset):
    """Face Landmarks dataset."""

    def __init__(self, loaded_data, transform=None):

        self.loaded_data = loaded_data
        self.transform = transform

    def __len__(self):
        return len(self.loaded_data)

    def __getitem__(self, idx):
        sample = self.loaded_data[idx]
        if self.transform:
            sample = self.transform(sample)
        return sample


class DN2OutlierScorer(KMeansOutlierScorer):
    def __init__(self, k=16, clusters=None, dist="euclidean"):
        super().__init__(k=k, clusters=clusters, dist=dist)
        self.mobilenet = models.mobilenet_v2(pretrained=True).eval()
        self.tfs = transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])]
        )

    def extract_feature(self, data):
        if not isinstance(data, Image.Image):
            raise ValueError(f"data must be of type PIL.Image.Image, not {data.shape}")
        batchtf = self.tfs(data)[None, :]
        feats = self.mobilenet(batchtf).detach().numpy()
        return super().extract_feature(data=feats)

    def build(self, data, batch_size=16):
        dataset = ImageDataset(loaded_data=data, transform=self.tfs)
        # data is a list of images here
        dataloader = DataLoader(dataset, shuffle=False, batch_size=batch_size, drop_last=True)
        embeddings = torch.zeros(size=(len(data), 1000))
        for batchidx, batchtf in enumerate(dataloader):
            # batchtf = self.tfs(batch)
            features = self.mobilenet(batchtf).detach()  # .numpy()
            startidx = batchidx * 16
            stopidx = startidx + len(features)
            embeddings[startidx:stopidx, :] = features

        embeddings = embeddings[embeddings.abs().sum(axis=1) != 0]
        embeddings = embeddings.numpy()
        super().build(data=embeddings)
