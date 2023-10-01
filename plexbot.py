import logging
import asyncio
import random
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

def ok_reply() -> str:
    return random.choice([
        "Downloading ⬇️",
        "Fetching it right now ⬇️",
        "On it! ⬇️",
        "Working on it ⬇️",
        "Right away ⬇️",
        "One moment ⌛",
        "Just a moment ⏱️"])

def success_reply() -> str:
    return random.choice([
        "Done ✅",
        "Done 🎉",
        "Finished ✅",
        "Enjoy your video 🎉",
        "Your video is ready 📺"])

async def download_video(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    videos = Path(config["Bot"]["videos-folder"])

    logging.info(f"Downloading video {url} ...")
    await context.bot.send_message(
        update.message.chat_id,
        ok_reply()
    )

    success = await download_with_yt_dlp(url, videos)

    logging.info(f"Download {'complete' if success else 'failed'}: {url}")
    await context.bot.send_message(
        update.message.chat_id,
        success_reply() if success else "Download failed ❌😭"
    )

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
    success = proc.returncode == 0

    if stdout:
        logging.debug(f'[stdout]\n{stdout.decode()}')
    if stderr:
        logging.debug(f'[stderr]\n{stderr.decode()}')
    if not success:
        logging.error(f'[stderr]\n{stderr.decode()}')

    return (success)


def main() -> None:
    token = config["Bot"]["token"]
    application = ApplicationBuilder().token(token).build()
    application.add_handler(MessageHandler(~filters.COMMAND, download_video))
    application.run_polling()


if __name__ == "__main__":
    main()