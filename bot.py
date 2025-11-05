from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os

# ----------------- CONFIG -----------------
BOT_TOKEN = "8503121779:AAEhU3hRbwBeA0O0bUl_XQrQRSDeF0wFk0U"  # <-- Replace with your Bot Token
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ----------------- FUNCTIONS -----------------
def download_audio(url):
    """
    Downloads the best audio from YouTube using yt-dlp.
    Returns the path to the downloaded file.
    """
    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        return filename
    except yt_dlp.utils.DownloadError:
        return None

# ----------------- TELEGRAM HANDLERS -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Send me a YouTube link and I’ll download the audio for you!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "youtube.com" in url or "youtu.be" in url:
        await update.message.reply_text("🔄 Downloading audio, please wait...")
        audio_file = download_audio(url)
        if audio_file:
            try:
                await update.message.reply_audio(audio=open(audio_file, 'rb'))
                os.remove(audio_file)  # delete after sending
            except Exception as e:
                await update.message.reply_text(f"⚠️ Could not send file: {e}")
        else:
            await update.message.reply_text(
                "❌ Could not download this video. "
                "It might be age-restricted, private, or blocked."
            )
    else:
        await update.message.reply_text("❌ Please send a valid YouTube link.")

# ----------------- MAIN -----------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()
