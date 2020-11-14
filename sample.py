import os
import pickle
from typing import Callable, List, Tuple, Union

import numpy as np

import skimage.io

import torch

from torchvision import transforms

from src.data.transforms import Rescale
from src.models.decoder import FactoredLSTM
from src.models.encoder import EncoderCNN


def load_sample_images(
    img_dir: str,
    transform: Callable[[np.ndarray], np.ndarray]
) -> Tuple[Union[List[str], List[np.ndarray]]]:
    img_names = os.listdir(img_dir)
    img_list = []
    for img_name in img_names:
        img_name = os.path.join(img_dir, img_name)
        img = skimage.io.imread(img_name)
        img = transform(img).unsqueeze(0)
        img_list.append(img)
    return img_names, img_list


def main() -> None:
    # load vocablary
    with open("data/vocab.pkl", "rb") as f:
        vocab = pickle.load(f)

    # build model
    encoder = EncoderCNN(300)
    decoder = FactoredLSTM(300, 512, 512, len(vocab))

    encoder.load_state_dict(torch.load("pretrained_models/encoder-15.pkl"))
    decoder.load_state_dict(torch.load("pretrained_models/decoder-15.pkl"))

    # prepare images
    transform = transforms.Compose([
        Rescale((224, 224)),
        transforms.ToTensor()
    ])
    img_names, img_list = load_sample_images("sample_images/", transform)
    image = img_list[30]

    # if torch.cuda.is_available():
    #     encoder = encoder.cuda()
    #     decoder = decoder.cuda()

    # farward
    features = encoder(image)
    output = decoder.sample(features, mode="factual")

    caption = [vocab.i2w[x] for x in output]
    print(img_names[30])
    print(caption)


if __name__ == "__main__":
    main()
