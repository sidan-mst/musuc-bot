import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import os
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
        "👋 Welcome!\n\nJoin our channel to use this bot.",
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

# 🎵 DOWNLOAD AUDIO
async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "youtu" not in url:
        await update.message.reply_text("❌ Send valid YouTube link")
        return

    await update.message.reply_text("⏳ Downloading...")

    ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'audio.%(ext)s',
    'quiet': True,
    'noplaylist': True,
    'geo_bypass': True,
    'ignoreerrors': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',
    }],
    }

    try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        mp3_file = filename.rsplit(".", 1)[0] + ".mp3"

    with open(mp3_file, "rb") as f:
        update.message.reply_audio(f)

    os.remove(mp3_file)

except Exception as e:
    update.message.reply_text(f"❌ Error: {e}")

# 🚀 MAIN
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

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
