import asyncio
import logging
import os
import re
import requests
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from moviepy.editor import VideoFileClip

# Replace with your Telegram bot token
TOKEN = "1715456897:AAF4RTmQOKp9H-_y-T5UDwgOLuVZO379aDI"

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_full_url(short_url):
    """Resolve the shortened TikTok URL to its full URL."""
    response = requests.head(short_url, allow_redirects=True)
    return response.url

def extract_username(video_url):
    """Extract the username from the TikTok video URL."""
    full_url = get_full_url(video_url)
    match = re.search(r'tiktok\.com/@([^/]+)', full_url)
    if match:
        return match.group(1)
    return "unknown_user"  # Default username if not found

def download_tiktok_video(video_url):
    """Download TikTok video using yt-dlp and return the file path."""
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',  # Save to downloads folder
        'quiet': True,  # Suppress output
    }

    # Create downloads directory if it doesn't exist
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            return ydl.prepare_filename(info_dict)  # Return the path of the downloaded file
    except Exception as e:
        logging.error(f"Error downloading video: {e}")
        return None

def extract_audio_from_video(video_path, username):
    """Extract audio from the downloaded video and return the audio file path."""
    audio_file_path = f'downloads/{username}.mp3'  # Use username in the filename
    try:
        # Load the video file using moviepy
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_file_path)  # Export as MP3
        return audio_file_path
    except Exception as e:
        logging.error(f"Error extracting audio: {e}")
        return None

async def main():
    """Main async function to run the bot polling."""
    @dp.message_handler(commands=['start'])
    async def start_command(message: types.Message):
        await message.reply("Mənə TikTok video linkini göndər, mən də onu sizin üçün HD formatında endirim!")

    @dp.message_handler()
    async def handle_message(message: types.Message):
        video_url = message.text.strip()
        username = extract_username(video_url)  # Extract username from the URL

        if "tiktok.com" not in video_url:
            await message.reply("Lütfən, etibarlı TikTok video URL göndərin.")
            return

        await message.reply("Video endirilir, zəhmət olmasa gözləyin...")

        download_path = download_tiktok_video(video_url)
        if download_path:
            # Extract audio from the downloaded video using the username
            audio_path = extract_audio_from_video(download_path, username)

            # Send both video and audio back to the user
            with open(download_path, 'rb') as video_file:
                await message.reply_video(video=video_file, caption="Here is your HD video! 🎥")

            if audio_path:
                with open(audio_path, 'rb') as audio_file:
                    await message.reply_audio(audio_file, caption="Here is the extracted audio! 🎵")

            # Clean up: remove the video and audio files after sending
            os.remove(download_path)
            if audio_path:  # Check if audio_path is not None before removing
                os.remove(audio_path)
        else:
            await message.reply("Failed to download the video. Please try again later.")

    # Start polling the bot
    executor.start_polling(dp, skip_updates=True)

# Ensure the event loop is set in the main thread
if __name__ == "__main__":
    asyncio.run(main())
