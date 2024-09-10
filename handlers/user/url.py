import logging
import re

from aiogram import exceptions, types
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from downloaders import (
    YouTubeDownloader,
    download_apple_music,
    download_bilibili,
    download_instagram,
    download_pinterest,
    download_soundcloud,
    download_spotify,
    download_tiktok,
    download_twitter,
)
from filters.playlist_filter import PlaylistFilter
from filters.url_filter import UrlFilter
from loader import dp
from utils import (
    delete_files,
    get_all_tracks_from_playlist_soundcloud,
    get_all_tracks_from_playlist_spotify,
    # random_emoji,
)


@dp.message(UrlFilter())
async def url_handler(message: types.Message):
    youtube_match = re.match(
        r"https?://(?:www\.)?(?:youtu\.be\/|youtube\.com/(?:shorts/|watch\?v=))([\w-]+)",
        message.text
    )
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
    await download_handler(callback_query.message, format= callback_query.data)

async def process_download(message: types.Message, download_func, format: str = "media"):
    try:
        if format == "media":
            await message.bot.send_chat_action(message.chat.id, "record_video")
            media_group, title, temp_medias = await download_func(url=message.text, format="media")
            await message.bot.send_chat_action(message.chat.id, "upload_video")
            await message.answer_media_group(media=media_group.build(), caption=title)
            await delete_files(temp_medias)
        elif format == "audio":
            await message.bot.send_chat_action(message.chat.id, "record_voice")
            audio_filename, thumbnail_filename = await download_func(url=message.text, format="audio")
            print(audio_filename, thumbnail_filename)
            await message.bot.send_chat_action(message.chat.id, "upload_voice")
            await message.answer_audio(audio=types.FSInputFile(audio_filename), thumbnail=types.FSInputFile(thumbnail_filename))
            await delete_files([audio_filename, thumbnail_filename])
    except exceptions.TelegramEntityTooLarge:
        await message.answer(_("Critical error #022 - media file is too large"))
    except Exception as e:
        logging.error(f"{e}")
        await message.answer(_("Sorry, there was an error. Try again later 🧡"))

@dp.message(UrlFilter())
async def download_handler(message: types.Message, format: str = "media"):
    url_patterns = {
        r"https?://(?:www\.)?(?:youtu\.be\/|youtube\.com/(?:shorts/|watch\?v=))([\w-]+)": (YouTubeDownloader().download, None),
        r"https?://vm.tiktok.com/": (download_tiktok, "media"),
        r"https?://vt.tiktok.com/": (download_tiktok, "media"),
        r"https?://(?:www\.)?tiktok\.com/.*": (download_tiktok, "media"),
        r"https://soundcloud\.com\/[\w-]+\/(?!sets\/)[\w-]+": (download_soundcloud, "audio"),
        r"https?://open\.spotify\.com/track/([\w-]+)": (download_spotify, "audio"),
        r'https?://music\.apple\.com/.*/album/.+/\d+(\?.*)?$': (download_apple_music, "audio"),
        r'https?://(?:\w{2,3}\.)?pinterest\.com/[\w/\-]+|https://pin\.it/[A-Za-z0-9]+': (download_pinterest, "media"),
        r"https?://(?:www\.)?bilibili\.(?:com|tv)/[\w/?=&]+": (download_bilibili, "media"),
        r"https://(?:twitter|x)\.com/\w+/status/\d+": (download_twitter, "media"),
        r'https://www\.instagram\.com/(?:p|reel|tv|stories)/([A-Za-z0-9_-]+)/': (download_instagram, "media"),
    }

    for pattern, (download_func, media_format) in url_patterns.items():
        if media_format is not None:
            format = media_format
        if re.match(pattern, message.text):
            await process_download(message, download_func, format)
            return

@dp.message(PlaylistFilter())
async def download_playlist_handler(message: types.Message, format: str = "audio"):
    if re.match(r"https?://open\.spotify\.com/playlist/([\w-]+)", message.text):
        tracks = get_all_tracks_from_playlist_spotify(message.text)
        for track in tracks:
            try:
                await message.bot.send_chat_action(message.chat.id, "record_voice")
                audio_filename, thumbnail_filename = await download_spotify(url=track, format="audio")
                await message.bot.send_chat_action(message.chat.id, "upload_voice")
                await message.answer_audio(audio=types.FSInputFile(audio_filename), thumbnail=types.FSInputFile(thumbnail_filename))
                await delete_files([audio_filename, thumbnail_filename])
            except Exception as e:
                logging.error(f"{e}")
                await message.answer(_(f"Sorry, there's been an error with this song:\n{track}"))

    elif re.match("https?://soundcloud\.com/[a-zA-Z0-9_-]+/sets/[a-zA-Z0-9_-]+", message.text):
        tracks = get_all_tracks_from_playlist_soundcloud(message.text)
        for track in tracks:
            try:
                await message.bot.send_chat_action(message.chat.id, "record_voice")
                audio_filename, thumbnail_filename = await download_soundcloud(url=track, format="audio")
                await message.bot.send_chat_action(message.chat.id, "upload_voice")
                await message.answer_audio(audio=types.FSInputFile(audio_filename),
                                           thumbnail=types.FSInputFile(thumbnail_filename))
                await delete_files([audio_filename, thumbnail_filename])
            except Exception as e:
                logging.error(f"{e}")
                await message.answer(_(f"Sorry, there's been an error with this song:\n{track}"))