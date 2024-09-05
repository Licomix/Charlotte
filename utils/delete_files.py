import aiofiles.os
import logging


async def delete_files(files=None):
    """
    Asynchronously deletes multiple files.

    :param files: List of filenames to delete. Defaults to None.
    :return: List of successfully deleted files.
    """
    if files is None:
        files = []

    deleted_files = []

    for filename in files:
        try:
            if await aiofiles.os.path.exists(filename):
                await aiofiles.os.remove(filename)
                deleted_files.append(filename)
                logging.info(f"Deleted file: {filename}")
            else:
                logging.warning(f"File not found: {filename}")
        except Exception as e:
            logging.error(f"Error deleting file {filename}: {e}")

    return deleted_files
