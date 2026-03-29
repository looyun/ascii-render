from PIL import Image
from pathlib import Path
from typing import Union


def load_image(path: Union[str, Path]) -> Image.Image:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    return Image.open(path)
