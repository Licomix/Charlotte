import logging
import re
import asyncio

from aiogram import exceptions, types
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config.secrets import ADMIN_ID
from .help import user_tasks

from downloaders import (
    YouTubeDownloader,
    AppleMusicDownloader,
    BilibiliDownloader,
    InstagramDownloader,
    PinterestDownloader,
    SoundCloudDownloader,
    SpotifyDownloader,
    TikTokDownloader,
    TwitterDownloader,
)
from filters.url_filter import UrlFilter
from loader import dp
from utils import (
    delete_files,
)

@dp.message(UrlFilter())
async def url_handler(message: types.Message):
    youtube_match = re.match(r'https?://(?:www\.)?(?:m\.)?(?:youtu\.be/|youtube\.com/(?:shorts/|watch\?v=))([\w-]+)', message.text)
    if youtube_match:
        markup = InlineKeyboardBuilder()
        markup.add(types.InlineKeyboardButton(text=_("Video"), callback_data="media"))
        markup.add(types.InlineKeyboardButton(text=_("Audio"), callback_data="audio"))
        await message.answer(message.text, reply_markup=markup.as_markup())
    else:
        await download_handler(message, format="media")

@dp.callback_query()
async def handle_format_choice(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await download_handler(callback_query.message, format=callback_query.data)


async def process_download(message: types.Message, download_func, format: str = "media", **kwargs):
    try:
        if format == "media":
            await message.bot.send_chat_action(message.chat.id, "record_video")
            async for media_group, temp_medias in download_func(url=message.text, format="media", **kwargs):
                if media_group is None or temp_medias is None:
                    raise SomethingWrong()

                await message.bot.send_chat_action(message.chat.id, "upload_video")
                await message.answer_media_group(media=media_group.build())
                await delete_files(temp_medias)

        elif format == "audio":
            await message.bot.send_chat_action(message.chat.id, "record_voice")
            async for audio_filename, cover_filename in download_func(url=message.text, format="audio", **kwargs):
                if audio_filename is None or cover_filename is None:
                    raise SomethingWrong()

                await message.bot.send_chat_action(message.chat.id, "upload_voice")
                await message.answer_audio(
                    audio=types.FSInputFile(audio_filename),
                    thumbnail=types.FSInputFile(cover_filename),
                    disable_notification=True
                )
                await delete_files([audio_filename, cover_filename])

    except exceptions.TelegramEntityTooLarge:
        await message.answer(_("Critical error #022 - media file is too large"))
    except SomethingWrong:
        await message.answer(_("Critical error #013 - something's wrong, I'm gonna go eat some cookies"))
        await message.bot.send_message(ADMIN_ID, f"Sorry, there was an error:\n {message.text}")
    except Exception as e:
        logging.error(f"{e}")
        await message.answer(_("Sorry, there was an error. Try again later 🧡"))
        await message.bot.send_message(ADMIN_ID, f"Sorry, there was an error:\n {message.text}\n\n{e}")


@dp.message(UrlFilter())
async def download_handler(message: types.Message, format: str = "media"):
    url_patterns = {
        r'https?://(?:www\.)?(?:m\.)?(?:youtu\.be/|youtube\.com/(?:shorts/|watch\?v=))([\w-]+)': (YouTubeDownloader().download, None),
        r"https:\/\/music\.youtube\.com\/(?:watch\?v=|playlist\?list=)([a-zA-Z0-9\-_]+)": (YouTubeDownloader().download, "audio"),
        r"https?://vm.tiktok.com/": (TikTokDownloader().download, "media"),
        r"https?://vt.tiktok.com/": (TikTokDownloader().download, "media"),
        r"https?://(?:www\.)?tiktok\.com/.*": (TikTokDownloader().download, "media"),
        r'https?://soundcloud\.com/([\w-]+)/([\w-]+)': (SoundCloudDownloader().download, "audio"),
        r"https?://open\.spotify\.com/(track|playlist)/([\w-]+)": (SpotifyDownloader().download, "audio"),
        r'https?://music\.apple\.com/.*/album/.+/\d+(\?.*)?$': (AppleMusicDownloader().download, "audio"),
        r'https?://(?:\w{2,3}\.)?pinterest\.com/[\w/\-]+|https://pin\.it/[A-Za-z0-9]+': (PinterestDownloader().download, "media"),
        r"https?://(?:www\.)?bilibili\.(?:com|tv)/[\w/?=&]+": (BilibiliDownloader().download, "media"),
        r"https://(?:twitter|x)\.com/\w+/status/\d+": (TwitterDownloader().download, "media"),
        r'https://www\.instagram\.com/(?:p|reel|tv|stories)/([A-Za-z0-9_-]+)/': (InstagramDownloader().download, "media"),
    }

    for pattern, (download_func, media_format) in url_patterns.items():
        if media_format is not None:
            format = media_format
        if re.match(pattern, message.text):
            task = asyncio.create_task(process_download(message, download_func, format))
            user_tasks[message.from_user.id] = task
            return


class SomethingWrong(Exception):
    pass
