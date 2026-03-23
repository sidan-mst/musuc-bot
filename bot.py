import os
import yt_dlp
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ContextTypes

# GLOBAL PROGRESS TRACKER
PROGRESS_MSG_ID = None

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

# 🎵 DOWNLOAD AUDIO (PROGRESS + BULLETPROOF)
async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global PROGRESS_MSG_ID
    url = update.message.text

    if "youtu" not in url:
        await update.message.reply_text("❌ Send valid YouTube link")
        return

    # 📊 INITIAL PROGRESS MESSAGE
    progress_msg = await update.message.reply_text("⏳ Downloading... 0%")
    PROGRESS_MSG_ID = progress_msg.message_id

    def find_audio_file():
    files = [f for f in os.listdir('.') if any(ext in f.lower() for ext in ['.m4a', '.mp4', '.webm', '.mkv', '.mp3', '.aac'])]
    return files[0] if files else None

ydl_opts = {
    'format': 'best',
    'outtmpl': '%(title)s.%(ext)s',  # ← VIDEO TITLE AS FILENAME
    'quiet': True,
    # ... rest stays same
}

    def progress_hook(d):
        global PROGRESS_MSG_ID
        if d['status'] == 'downloading' and PROGRESS_MSG_ID:
            try:
                percent = d.get('_percent_str', '0%')
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                
                context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=PROGRESS_MSG_ID,
                    text=f"⏳ Downloading... {percent}
⚡ Speed: {speed} | ⏱️ ETA: {eta}"
                )
            except:
                pass

    ydl_opts = {
        'format': 'best',  # Always works
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'geo_bypass': True,
        'ignoreerrors': True,
        'extractaudio': True,
        'audioformat': 'm4a',
        'player_client': ['ios', 'android', 'web'],
        'no_warnings': True,
        'progress_hooks': [progress_hook],  # 🔥 LIVE PROGRESS
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # 🗑️ DELETE PROGRESS MESSAGE
        try:
            await context.bot.delete_message(update.effective_chat.id, PROGRESS_MSG_ID)
        except:
            pass

        audio_file = find_audio_file()
        if not audio_file:
            await update.message.reply_text("❌ Video unavailable in your region.")
            cleanup()
            return

        safe_name = re.sub(r'[<>:"/\\|?*]', '', audio_file)[:100]
        
        with open(audio_file, "rb") as f:
            await update.message.reply_audio(
                f, 
                title=safe_name, 
                performer="MusicGo 🎵",
                caption="🎵 Downloaded from YouTube ✅"
            )

        os.remove(audio_file)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:150]}
Try a different video.")
        cleanup()

def cleanup():
    for f in os.listdir('.'):
        if any(ext in f.lower() for ext in ['.m4a', '.mp4', '.webm', '.mkv', '.mp3', '.aac']):
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

    print("🎵 MusicGo Bot started with LIVE PROGRESS...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
