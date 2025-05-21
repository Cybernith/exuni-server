import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from pathlib import Path


class ImageFeatureExtractor:

    def __init__(self, use_gpu_if_available=True):
        self.device = torch.device("cuda" if use_gpu_if_available and torch.cuda.is_available() else "cpu")

        try:
            self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            self.model.eval()
            self.feature_extractor = torch.nn.Sequential(*list(self.model.children())[:-1])
            self.feature_extractor.to(self.device)
        except Exception as e:
            raise RuntimeError(f"خطا در بارگذاری مدل: {e}")

        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def extract_features(self, image_input, batch_mode=False):
        try:
            if batch_mode:
                return self._extract_batch_features(image_input)
            else:
                return self._extract_single_feature(image_input)
        except Exception as e:
            raise RuntimeError(f"خطا در استخراج ویژگی‌ها: {e}")

    def _extract_single_feature(self, image_input):
        if isinstance(image_input, (str, Path)):
            img = Image.open(image_input).convert('RGB')
        elif isinstance(image_input, Image.Image):
            img = image_input.convert('RGB')
        elif hasattr(image_input, 'read'):
            img = Image.open(image_input).convert('RGB')
        else:
            raise ValueError("ورودی باید مسیر تصویر، شیء PIL.Image یا Django File باشد.")

        input_tensor = self.preprocess(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            features = self.feature_extractor(input_tensor)
        features = features.squeeze().cpu().numpy()
        return features

    def _extract_batch_features(self, image_inputs):
        if not isinstance(image_inputs, (list, tuple)):
            raise ValueError("برای حالت batch، ورودی باید لیست باشد.")

        input_tensors = []
        for image_input in image_inputs:
            if isinstance(image_input, (str, Path)):
                img = Image.open(image_input).convert('RGB')
            elif isinstance(image_input, Image.Image):
                img = image_input.convert('RGB')
            elif hasattr(image_input, 'read'):
                img = Image.open(image_input).convert('RGB')
            else:
                raise ValueError(f"ورودی نامعتبر در لیست: {image_input}")
            input_tensors.append(self.preprocess(img))

        input_batch = torch.stack(input_tensors).to(self.device)

        with torch.no_grad():
            features = self.feature_extractor(input_batch)
        features = features.squeeze().cpu().numpy()
        return features


# مثال استفاده
#if __name__ == "__main__":
#    extractor = ImageFeatureExtractor()
#
#    # استخراج ویژگی از یک تصویر
#    try:
#        features = extractor.extract_features("path/to/image.jpg")
#        print(f"ویژگی‌های تصویر: {features.shape}")
#    except Exception as e:
#        print(f"خطا: {e}")
#
#    # استخراج ویژگی از لیست تصاویر
#    try:
#        image_paths = ["path/to/image1.jpg", "path/to/image2.jpg"]
#        batch_features = extractor.extract_features(image_paths, batch_mode=True)
#        print(f"ویژگی‌های دسته: {batch_features.shape}")
#    except Exception as e:
#        print(f"خطا: {e}")