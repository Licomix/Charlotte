import asyncio
import logging
import os
import urllib.request

import yt_dlp
from fake_headers import Headers
from aiogram.enums import InputMediaType
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


class TwitterDownloader:
    """
    A class for downloading media from Twitter using yt-dlp and Playwrigpt.

    Attributes:
    ----------
    output_path : str
        Directory where the downloaded files will be saved.

    Methods:
    -------
    download(url: str, format: str)
        Choose which function use to download.

    _download_video(url: str)
        Download a video from a given Twitter URL.

    _download_music(url: str)
        Download an audio from a given Twitter URL.
    """

    def __init__(self, output_path: str = "other/downloadsTemp"):
        """
        Initialize the Twitter downlaoder with an output path for downloads.

        Parameters:
        ----------
        output_path : str, optional
            The directory where downloaded files will be saved (default is "other/downloadsTemp").
        """
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.yt_dlp_video_options = {
            "outtmpl": f"{output_path}/%(title)s.%(ext)s",
        }

    async def download(self, url: str, format: str):
        """
        Download a media file  based on the format.

        Parameters:
        ----------
        url : str
            The Twitter video URL to download.
        format : str
            The format of the download ('media' for video or 'audio' for audio). Media only.

        Yields:
        -------
        AsyncGenerator
            Returns an async generator yielding media filenames or None if an error occurs.
        """
        try:
            if format == "media":
                async for result in self._download_media(url):
                    yield result
            else:
                logging.error(f"Unsupported format: {format}")
                yield None
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            yield None


    async def _download_media(self, url: str, output_path: str = "other/downloadsTemp", format: str = "media"):
        try:
            temp_medias = []
            with yt_dlp.YoutubeDL(self.yt_dlp_video_options) as ydl:
                info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
                title = info_dict.get("title", "video")
                filename = ydl.prepare_filename(info_dict)

                await asyncio.to_thread(ydl.download, [url])

                media_group = MediaGroupBuilder(caption=title)
                media_group.add_video(media=FSInputFile(filename), type=InputMediaType.VIDEO)

                temp_medias.append(filename)

                if os.path.exists(filename):
                    yield media_group, title, temp_medias

        except yt_dlp.DownloadError:
            try:
                header = Headers().generate()["User-Agent"]

                async with async_playwright() as p:
                    browser = await p.firefox.launch(
                        headless=True,
                        args=[
                            "--no-sandbox",
                            "--disable-dev-shm-usage",
                            "--ignore-certificate-errors",
                            "--disable-gpu",
                            "--log-level=3",
                            "--disable-notifications",
                            "--disable-popup-blocking",
                            f"--user-agent={header}"
                        ]
                    )
                    page = await browser.new_page()
                    await page.goto(url)

                    await asyncio.sleep(4)

                    content = await page.content()
                    soup = BeautifulSoup(content, "html.parser")

                    images = soup.find_all("img")
                    tweet_text_div = soup.find("div", {"data-testid": "tweetText"})
                    if tweet_text_div:
                        tweet_spans = tweet_text_div.find_all("span")
                        tweet_texts = [span.get_text() for span in tweet_spans]
                        full_text = " ".join(tweet_texts)
                    else:
                        full_text = ""

                    images = [img["src"] for img in images if "/media/" in str(img["src"])]
                    title = f"{url.split('/')[3]} - {full_text}"

                    media_group = MediaGroupBuilder(caption=title)

                    temp_medias = []

                    for image in images:
                        image = image.split("&name")[0]
                        filename = os.path.join(output_path, f"{image.split('/')[-1]}.jpg")
                        try:
                            urllib.request.urlretrieve(image, filename)
                            media_group.add_photo(media=FSInputFile(filename), type=InputMediaType.PHOTO)
                            temp_medias.append(filename)
                        except Exception as e:
                            print(f"Failed to download image {image}: {e}")
                            continue

                    await browser.close()

                    yield media_group, title, temp_medias

            except Exception as e:
                print(f"Error downloading Twitter post: {str(e)}")

        except Exception as e:
            logging.error(f"Error downloading Twitter video: {str(e)}")
            yield None
