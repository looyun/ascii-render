from PIL import Image
from typing import Iterator, Optional


class VideoProcessor:
    @staticmethod
    def read_gif(path: str) -> Iterator[Image.Image]:
        """
        Read GIF frames and yield them as images.

        Note: Some GIFs (especially those created by certain tools) only have the
        'transparency' field in the first frame's info, even though all frames use
        the same transparent color. Pillow only applies transparency handling to
        frames that have this field in their info dict.

        For example, if frame 0 has transparency=255 (palette index 255 is transparent),
        but subsequent frames don't have 'transparency' in their info, Pillow will:
        - Frame 0: Correctly treat palette index 255 as transparent
        - Frame 1+: NOT treat any pixels as transparent, causing the background to
                   appear different (solid white instead of transparent)

        This fix extracts the transparency index from any frame that has it, then
        applies the same logic to all subsequent frames during RGBA conversion.
        """
        img = Image.open(path)
        frames = []
        try:
            while True:
                frames.append(img.copy())
                img.seek(img.tell() + 1)
        except EOFError:
            pass

        if not frames:
            return

        trans_index = None
        for f in frames:
            if f.mode == "P" and "transparency" in f.info:
                trans_index = f.info["transparency"]
                break

        for i, f in enumerate(frames):
            if f.mode == "P":
                f = f.convert("RGBA")

                if trans_index is not None and i > 0:
                    alpha = f.split()[3]
                    alpha = alpha.point(lambda p: 0 if p == 255 else p)
                    channels = list(f.split())
                    channels[3] = alpha
                    f = Image.merge("RGBA", channels)

            yield f

    @staticmethod
    def get_gif_info(path: str) -> Optional[float]:
        img = Image.open(path)
        if img.format == "GIF" and "duration" in img.info:
            duration = img.info["duration"]
            if isinstance(duration, list):
                duration = sum(duration) / len(duration) if duration else 100
            return 1000.0 / duration if duration > 0 else 10.0
        return None

    @staticmethod
    def read_video_frames(
        path: str, max_frames: Optional[int] = None
    ) -> Iterator[Image.Image]:
        try:
            import cv2
        except ImportError:
            raise ImportError(
                "opencv-python-headless is required for video processing. "
                "Install it with: pip install ascii_render[video]"
            )

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
