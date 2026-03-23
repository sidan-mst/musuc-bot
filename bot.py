import os
import yt_dlp
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ContextTypes

# CONFIG
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1003606196677
CHANNEL_LINK = "https://t.me/+mscj29jMDdwyYzg9"

# 🔘 START COMMAND
def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Try Again", callback_data="check")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "👋 Welcome!

Join our channel to use this bot.",
        reply_markup=reply_markup
    )

# 🔘 CHECK SUBSCRIPTION
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ["member", "administrator", "creator"]:
            await query.answer()
            await query.message.reply_text("✅ You joined! Now send YouTube link 🎵")
        else:
            await query.answer("❌ Join channel first", show_alert=True)
    except:
        await query.answer("❌ Error checking", show_alert=True)

# 🎵 DOWNLOAD AUDIO (M4A VERSION - FIXES FORMAT ERROR)
async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "youtu" not in url:
        await update.message.reply_text("❌ Send valid YouTube link")
        return

    await update.message.reply_text("⏳ Downloading...")

    def find_audio_file():
        # Look for M4A, MP4, WEBM (in priority order)
        for file in os.listdir('.'):
            if file.endswith('.m4a'):
                return file
            elif file.endswith('.mp4'):
                return file
            elif file.endswith('.webm'):
                return file
        return None

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best[height<=480]/best',  # ✅ Bulletproof fallback
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'geo_bypass': True,
        'ignoreerrors': True,
        # ✅ NO postprocessor = Direct download (no MP3 conversion)
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        audio_file = find_audio_file()
        if not audio_file:
            await update.message.reply_text("❌ No audio found. Video may be restricted.")
            # Cleanup any leftover files
            for f in os.listdir('.'):
                if f.endswith(('.m4a', '.mp4', '.webm')):
                    os.remove(f)
            return

        # Clean filename for Telegram (remove invalid chars)
        safe_name = re.sub(r'[<>:"/\\|?*]', '', audio_file)[:100]
        
        with open(audio_file, "rb") as f:
            await update.message.reply_audio(
                f, 
                title=safe_name, 
                performer="MusicGo 🎵",
                caption=f"🎵 Downloaded from YouTube"
            )

        # Cleanup
        os.remove(audio_file)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:200]}
Try a different video.")
        # Cleanup on error
        for f in os.listdir('.'):
            if f.endswith(('.m4a', '.mp4', '.webm')):
                try:
                    os.remove(f)
                except:
                    pass

# 🚀 MAIN
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(check_subscription, pattern="check"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_audio))

    print("🎵 MusicGo Bot started...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
