from PIL import Image
from typing import Iterator, Union, Optional
import numpy as np


class VideoProcessor:
    @staticmethod
    def read_gif(path: str) -> Iterator[Image.Image]:
        img = Image.open(path)
        try:
            while True:
                yield img.copy()
                img.seek(img.tell() + 1)
        except EOFError:
            pass

    @staticmethod
    def read_video_frames(
        path: str, max_frames: Optional[int] = None
    ) -> Iterator[Image.Image]:
        try:
            import cv2
        except ImportError:
            raise ImportError("opencv-python is required for video processing")

        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {path}")

        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            yield Image.fromarray(frame_rgb)
            frame_count += 1
            if max_frames and frame_count >= max_frames:
                break

        cap.release()
