from __future__ import annotations

import glob
import os
from typing import List, Dict, Any

from PIL import Image, ImageOps, ImageTk, ImageSequence


class ImageLoader:
    IMAGE_EXTENSIONS = ("*.gif", "*.png", "*.jpg", "*.jpeg")

    def __init__(self):
        self.cached_media: List[Dict[str, Any]] = []

    def load_and_cache(self, path: str, scale_percent: float, base_flip: bool) -> bool:
        self.cached_media.clear()
        if not path or not os.path.exists(path):
            return False

        files_to_load = []
        if os.path.isdir(path):
            for ext in self.IMAGE_EXTENSIONS:
                files_to_load.extend(glob.glob(os.path.join(path, ext)))
            files_to_load = files_to_load[:30]
        else:
            files_to_load = [path]

        if not files_to_load:
            return False

        scale_factor = float(scale_percent) / 100.0
        resample_method = getattr(Image, "Resampling", Image).LANCZOS

        for f_path in files_to_load:
            try:
                img = Image.open(f_path)
                frames_normal, frames_flipped = [], []
                default_delay = img.info.get("duration", 50) or 50

                for frame in ImageSequence.Iterator(img):
                    f = frame.convert("RGBA")
                    if base_flip:
                        f = ImageOps.mirror(f)

                    if scale_factor != 1.0:
                        new_w = max(1, int(f.size[0] * scale_factor))
                        new_h = max(1, int(f.size[1] * scale_factor))
                        f = f.resize((new_w, new_h), resample_method)

                    f_flip = ImageOps.mirror(f)
                    frames_normal.append(ImageTk.PhotoImage(f))
                    frames_flipped.append(ImageTk.PhotoImage(f_flip))

                if frames_normal:
                    self.cached_media.append(
                        {"normal": frames_normal, "flipped": frames_flipped, "delay": default_delay}
                    )
            except Exception as exc:
                print(f"Failed to cache {f_path}: {exc}")

        return bool(self.cached_media)
