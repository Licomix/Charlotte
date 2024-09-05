import asyncio
import logging
import os

import yt_dlp
from aiogram.enums import InputMediaType
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder


async def download_tiktok(url, output_path="other/downloadsTemp", format="mp4"):
    if format == "mp4":
        try:
            options = {
                "format": "mp4",
                "outtmpl": f"{output_path}/%(title)s.%(ext)s",
            }
            with yt_dlp.YoutubeDL(options) as ydl:
                info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
                filename = ydl.prepare_filename(info_dict)
                await asyncio.to_thread(ydl.download, [url])

                media_group = MediaGroupBuilder()
                media_group.add_video(media=FSInputFile(filename), type=InputMediaType.VIDEO)

                if os.path.exists(filename):
                    return media_group, " ", filename
        except Exception as e:
            logging.error(f"Error downloading Tiktok video: {str(e)}")
            return None
