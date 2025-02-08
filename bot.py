import logging
import os
import re
import requests
import yt_dlp
from moviepy.editor import VideoFileClip
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Replace with your Telegram bot token
TOKEN = "YOUR_BOT_TOKEN"

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.error(f"Error downloading video: {e}")
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
        logger.error(f"Error extracting audio: {e}")
        return None

def create_social_media_buttons():
    """Create inline keyboard buttons for social media accounts."""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("Instagram", url="https://www.instagram.com/elkinabbasovv"),
        InlineKeyboardButton("Twitter", url="https://twitter.com/elkinabbasovv"),
        InlineKeyboardButton("Telegram", url="https://t.me/elkinabbasov")
    )
    return keyboard

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text("Mənə TikTok video linkini göndərin, mən onu sizin üçün HD formatında endirim.")

def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle incoming messages with a TikTok video URL."""
    video_url = update.message.text.strip()
    username = extract_username(video_url)  # Extract username from the URL

    if "tiktok.com" not in video_url:
        update.message.reply_text("Lütfən, etibarlı TikTok video URL göndərin.")
        return

    update.message.reply_text("Video endirilir, zəhmət olmasa gözləyin...")

    download_path = download_tiktok_video(video_url)
    if download_path:
        # Extract audio from the downloaded video using the username
        audio_path = extract_audio_from_video(download_path, username)

        # Create social media buttons
        social_media_buttons = create_social_media_buttons()

        # Send both video and audio back to the user
        with open(download_path, 'rb') as video_file:
            update.message.reply_video(video=video_file, reply_markup=social_media_buttons)

        if audio_path:
            with open(audio_path, 'rb') as audio_file:
                update.message.reply_audio(audio_file)

        # Clean up: remove the video and audio files after sending
        os.remove(download_path)
        if audio_path:  # Check if audio_path is not None before removing
            os.remove(audio_path)
    else:
        update.message.reply_text("Videonu endirmək alınmadı. Daha sonra yenidən cəhd edin.")

def main():
    """Start the bot."""
    updater = Updater(TOKEN, use_context=True)

    # Register handlers
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop
    updater.idle()

if __name__ == '__main__':
    main()
