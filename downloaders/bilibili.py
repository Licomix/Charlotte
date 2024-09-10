import logging
import os

import yt_dlp

async def download_bilibili(url: str, output_path: str = "other/downloadsTemp", format: str = "media"):
    """
    Downloads a video from Bilibili using yt-dlp and saves it to the specified output path.

    Parameters:
    ----------
    url : str
        The URL of the Bilibili video to download.
    output_path : str, optional
        The directory where the downloaded video will be saved (default is "other/downloadsTemp").
    format : str, optional
        The format of the download, default is "media". Not used in this implementation.

    Returns:
    -------
    tuple or int
        Returns a tuple containing the title of the video and the file path of the downloaded video if successful.
        Returns 1 if an error occurs.
    """
    try:
        options = {
            "format": "bv*[filesize < 50M][ext=mp4] / w",
            "outtmpl": f"{output_path}/%(title)s.%(ext)s",
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get("title", "video")
            filename = ydl.prepare_filename(info_dict)

            ydl.download([url])

            if os.path.exists(filename):
                return title, filename
    except yt_dlp.DownloadError as e:
        logging.error(f"Error downloading YouTube video: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error downloading YouTube video: {str(e)}")
        return None
