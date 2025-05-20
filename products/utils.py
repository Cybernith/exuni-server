import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

model = models.resnet50(pretrained=True)
model.eval()
feature_extractor = torch.nn.Sequential(*list(model.children())[:-1])

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def extract_features(image_path):
    img = Image.open(image_path).convert('RGB')
    input_tensor = preprocess(img).unsqueeze(0)
    with torch.no_grad():
        features = feature_extractor(input_tensor)
    features = features.squeeze().numpy()
    return features
