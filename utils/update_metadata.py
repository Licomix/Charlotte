import logging
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1

def update_metadata(audio_file: str, title: str, artist: str, cover_file: str = None) -> None:
    """
    Updates the MP3 file metadata and adds a cover art.

    :param audio_file: The path to the MP3 file.
    :param title: New title of the track.
    :param artist: New artist of the track.
    :param cover_file: Path to cover image (optional).
    :return: None
    """
    # Checking file extension
    if not audio_file.lower().endswith(".mp3"):
        logging.error(f"Файл {audio_file} не является MP3.")
        return

    try:
        # Open the file to read and write metadata
        audio = MP3(audio_file, ID3=ID3)

        # Add or update title and artist
        audio["TIT2"] = TIT2(encoding=3, text=title)
        audio["TPE1"] = TPE1(encoding=3, text=artist)

        # If there's a cover, add it
        if cover_file:
            with open(cover_file, 'rb') as img:
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc='Cover',
                        data=img.read()
                    )
                )

        audio.save()
        logging.info(f"Metadata and file cover of {audio_file} have been successfully updated.")

    except Exception as e:
        logging.error(f"Error when updating metadata: {str(e)}")
