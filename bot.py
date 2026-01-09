import telebot
import os
import time
from downloader import download_video

import logging

# Configure logging
logging.basicConfig(
    filename='bot_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- CONFIGURATION ---
# Get this from @BotFather
BOT_TOKEN = "6500080341:AAGbjqDMAjUgBRWZ_KYW0jFGAdyoSMAYiyY" 

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    logging.info(f"Received start command from {message.from_user.username}")
    bot.reply_to(message, "Hello! Send me a link from TikTok, Instagram, Facebook, or YouTube, and I'll try to download it for you.")

@bot.message_handler(func=lambda message: True) # Catch all text messages
def handle_message(message):
    url = message.text.strip()
    logging.info(f"Received message: {url} from {message.from_user.username}")
    
    # Basic validation (naive)
    if not url.startswith("http"):
        logging.warning("Invalid URL received")
        bot.reply_to(message, "That doesn't look like a valid link. Please send a URL starting with http/https.")
        return

    bot.reply_to(message, "Downloading... Please wait. ⏳")
    logging.info(f"Processing URL: {url}")
    
    # Download
    try:
        file_paths = download_video(url)
        logging.info(f"Download returned: {file_paths}")
    except Exception as e:
        logging.error(f"Download failed: {e}")
        file_paths = []
    
    if file_paths:
        bot.reply_to(message, f"Found {len(file_paths)} files. Uploading... 🚀")
        for file_path in file_paths:
            try:
                logging.info(f"Processing file: {file_path}")
                # Check file size
                file_size = os.path.getsize(file_path) / (1024 * 1024) # MB
                file_ext = os.path.splitext(file_path)[1].lower()
                
                logging.info(f"File size: {file_size}MB, Ext: {file_ext}")

                if file_size > 50:
                    logging.warning(f"File too large: {file_size}MB")
                    bot.reply_to(message, f"File {os.path.basename(file_path)} is too large ({file_size:.2f}MB). 😔")
                    continue

                with open(file_path, 'rb') as file_obj:
                    if file_ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.heic']:
                        logging.info("Sending as photo...")
                        bot.send_photo(message.chat.id, file_obj, caption="📸")
                    else:
                        logging.info("Sending as video...")
                        bot.send_video(message.chat.id, file_obj, caption="🎥", timeout=120)
                logging.info("Sent successfully.")
            except Exception as e:
                logging.error(f"Error sending {file_path}: {e}")
                bot.reply_to(message, f"Error sending {os.path.basename(file_path)}: {e}")
            finally:
                try:
                    os.remove(file_path)
                    logging.info("File removed.")
                except:
                    pass
    else:
        logging.warning("No files found.")
        bot.reply_to(message, "Sorry, I couldn't download that link. Make sure it's public and supported.")

if __name__ == "__main__":
    print("Bot is running...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Bot stopped: {e}")
