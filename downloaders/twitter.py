import asyncio
import logging
import os
import urllib.request
from asyncio import Semaphore

import yt_dlp
from aiogram.enums import InputMediaType
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

semaphore = Semaphore(1)

async def download_twitter(url: str, output_path: str = "other/downloadsTemp", format: str = "media"):
    try:
        temp_medias = []
        options = {
            "outtmpl": f"{output_path}/%(title)s.%(ext)s",
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
            title = info_dict.get("title", "video")
            filename = ydl.prepare_filename(info_dict)

            await asyncio.to_thread(ydl.download, [url])

            media_group = MediaGroupBuilder(caption=title)
            media_group.add_video(media=FSInputFile(filename), type=InputMediaType.VIDEO)

            temp_medias.append(filename)

            if os.path.exists(filename):
                return media_group, title, temp_medias

    except yt_dlp.DownloadError:
        async with semaphore:
            try:
                firefox_options = Options()
                firefox_options.add_argument("--headless")
                firefox_options.add_argument("--no-sandbox")
                firefox_options.add_argument("--disable-dev-shm-usage")

                driver = webdriver.Firefox(options=firefox_options)
                driver.get(url)

                await asyncio.sleep(5)

                soup = BeautifulSoup(driver.page_source, "html.parser")

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

                return media_group, title, temp_medias

            except Exception as e:
                print(f"Error downloading Twitter post: {str(e)}")

            finally:
                if driver:
                    driver.quit()

    except Exception as e:
        logging.error(f"Error downloading Twitter video: {str(e)}")
        print(e)
        return 1
