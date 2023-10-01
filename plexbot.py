import logging
import asyncio
from configparser import ConfigParser
from pathlib import Path
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackContext, filters


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

configpath = Path("~/.config/plexbot/config").expanduser()
config = ConfigParser()
config.read(configpath)


async def download_video(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    videos = Path(config["Bot"]["videos-folder"])

    logging.info(f"Downloading video {url} ...")
    
    success = await download_with_yt_dlp(url, videos)
    
    if (success):
        logging.info(f"Downloaded video {url}")
    else:
        logging.error(f"Download failed: {url}")


async def download_with_yt_dlp(url, dest) -> bool:
    format_str = ''

    proc = await asyncio.create_subprocess_shell(
        f'yt-dlp '
        f'-o "{dest}/%(title)s.%(ext)s" '
        # prefer 1080p
        # limit codec to h265|h264|vp8|h263 and aac|mp4a|mp3
        f'-S "+res:1080,codec:h265:aac,br"'
        f'--sponsorblock-remove default '
        f'{url}',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    
    stdout, stderr = await proc.communicate()

    if stdout:
        logging.debug(f'[stdout]\n{stdout.decode()}')
    if stderr:
        logging.debug(f'[stderr]\n{stderr.decode()}')

    return (proc.returncode == 0)


def main() -> None:
    token = config["Bot"]["token"]
    application = ApplicationBuilder().token(token).build()
    application.add_handler(MessageHandler(~filters.COMMAND, download_video))
    application.run_polling()


if __name__ == "__main__":
    main()