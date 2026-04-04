#!/usr/bin/env python3
"""
Telegram YouTube Download Bot for Nexa
Listens for YouTube links and sends downloaded files to the user.
"""

import os
import logging
import yt_dlp
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token - using the same bot as Nexa
BOT_TOKEN = "8785224568:AAGYmL4Vdrs00QykAZQE8-kxy4wLB7jVpeg"

# Allowed user IDs (Nemesis)
ALLOWED_USERS = [7924461837]

# Download directory
DOWNLOAD_DIR = "/root/Downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# yt-dlp options
YDLP_OPTS = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("Unauthorized.")
        return
    await update.message.reply_text("Send me a YouTube link and I'll download it for you! 🎵")

async def download_video(url: str, user_id: int) -> dict:
    """Download YouTube video/audio and return file info."""
    ydl_opts = YDLP_OPTS.copy()
    ydl_opts['outtmpl'] = os.path.join(DOWNLOAD_DIR, f'user_{user_id}', '%(title)s.%(ext)s')
    
    # Create user-specific directory
    user_dir = os.path.join(DOWNLOAD_DIR, f'user_{user_id}')
    os.makedirs(user_dir, exist_ok=True)
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            title = info.get('title', 'Unknown')
            return {
                'success': True,
                'filepath': filepath,
                'title': title
            }
    except Exception as e:
        logger.error(f"Download error: {e}")
        return {'success': False, 'error': str(e)}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages with YouTube links."""
    user_id = update.effective_user.id
    
    if user_id not in ALLOWED_USERS:
        logger.warning(f"Unauthorized access attempt from {user_id}")
        return
    
    text = update.message.text
    
    # Check for YouTube link
    if 'youtube.com' in text or 'youtu.be' in text or 'yt.dl' in text:
        # Send initial message
        msg = await update.message.reply_text("⏬ Downloading...")
        
        # Download
        result = await download_video(text, user_id)
        
        if result['success']:
            # Send file
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=msg.message_id
                )
                await update.message.reply_text(f"📤 Uploading: {result['title']}...")
                
                with open(result['filepath'], 'rb') as f:
                    await update.message.reply_document(
                        document=f,
                        caption=result['title']
                    )
                
                # Cleanup
                try:
                    os.remove(result['filepath'])
                except:
                    pass
                    
            except Exception as e:
                await update.message.reply_text(f"Upload failed: {e}")
        else:
            await msg.edit_text(f"❌ Download failed: {result['error']}")
    else:
        # Not a YouTube link
        await update.message.reply_text("Send me a YouTube link! 🎵")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")

def main() -> None:
    """Start the bot."""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    logger.info("Starting YouTube download bot...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
