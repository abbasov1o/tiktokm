import streamlit as st
import threading
import asyncio
from bot import main  # Import the main function from bot.py

# Function to run the Telegram bot asynchronously
def run_async_bot():
    asyncio.run(main())  # This runs the main async function from bot.py

# Start the bot in a separate thread
bot_thread = threading.Thread(target=run_async_bot)
bot_thread.daemon = True
bot_thread.start()

# Streamlit UI
st.title('TikTok Video Downloader Bot')

st.write(
    "Bu bot TikTok videolarını HD formatında endirir və audiosunu çıxarar. "
    "Sadəcə video linkini göndərin və botdan nəticə alın."
)

# Take input from the user for TikTok video URL
video_url = st.text_input("TikTok Video Linki")

# If user provides a URL, send it to the bot (you can expand this part)
if video_url:
    st.write("Video linki göndərildi, nəticəni gözləyin...")
    # Here you could send the URL to the bot and get the response, but this requires integration between Streamlit and your Telegram bot.
    st.write("Bot əməliyyatları başlatıldı...")

# Inform the user to keep the app running
st.write("Bot işləməyə davam edir... Bu səhifəni bağlamayın.")
