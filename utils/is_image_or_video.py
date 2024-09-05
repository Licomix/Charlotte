import os
from typing import Literal

def is_image_or_video(filename: str) -> Literal["video", "photo", "gif", "unknown"]:
    """
    Determines the file type by its extension.

    :param filename: The name of the file to check.
    :return: File type: “video”, “photo”, “gif”, or “unknown” if the extension is not recognized.
    """
    video_extensions = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"}
    photo_extensions = {".jpg", ".jpeg", ".png", ".bmp"}
    gif_extensions = {".gif"}

    ext = os.path.splitext(filename)[1].lower()

    if ext in video_extensions:
        return "video"
    elif ext in photo_extensions:
        return "photo"
    elif ext in gif_extensions:
        return "gif"
    else:
        return "unknown"
