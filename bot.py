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

# 🎵 DOWNLOAD AUDIO (FIXED VERSION)
async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "youtu" not in url:
        await update.message.reply_text("❌ Send valid YouTube link")
        return

    await update.message.reply_text("⏳ Downloading...")

    def find_mp3_file():
        for file in os.listdir('.'):
            if file.endswith('.mp3'):
                return file
        return None

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best[height<=480]/best',  # ✅ FIXED FORMAT
        'outtmpl': '%(title)s.%(ext)s',  # Dynamic title-based name
        'quiet': True,
        'noplaylist': True,
        'geo_bypass': True,
        'ignoreerrors': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',  # Best quality
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])  # Downloads + converts to MP3

        mp3_file = find_mp3_file()
        if not mp3_file:
            await update.message.reply_text("❌ No audio found. Video may be restricted.")
            return

        # Clean filename for Telegram
        safe_name = re.sub(r'[<>:"/\\|?*]', '', mp3_file)[:100]
        with open(mp3_file, "rb") as f:
            await update.message.reply_audio(f, title=safe_name)

        os.remove(mp3_file)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:200]}
Try a different video.")

# 🚀 MAIN
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(check_subscription, pattern="check"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_audio))

    print("Bot started...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
