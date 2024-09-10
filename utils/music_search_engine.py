import asyncio

from youtubesearchpython import VideosSearch

async def search_music(artist: str, title: str):
    videos_search = VideosSearch(f"{artist} - {title}", limit=10)
    video_results = await asyncio.to_thread(videos_search.result)

    for video_result in video_results.get("result", []):
        video_link = video_result["link"]
        duration_str = video_result.get("duration", "0")

        duration = parse_duration(duration_str)

        if duration <= 600:
            return video_link


def parse_duration(duration_str: str) -> int:
    """
    Parses a duration string in the format of HH:MM:SS, MM:SS, or SS and converts it into total seconds.

    Parameters:
    ----------
    duration_str : str
        The duration string to parse.

    Returns:
    -------
    int
        The total duration in seconds.
    """
    duration_parts = duration_str.split(":")
    if len(duration_parts) == 3:
        return int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60 + int(duration_parts[2])
    elif len(duration_parts) == 2:
        return int(duration_parts[0]) * 60 + int(duration_parts[1])
    return int(duration_parts[0])