import telebot
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Add ffmpeg to PATH manually if on Windows and path exists
if os.name == 'nt':
    FFMPEG_PATH = r"C:\Users\admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
    if os.path.exists(FFMPEG_PATH):
        os.environ["PATH"] += os.pathsep + FFMPEG_PATH
    else:
        logging.warning(f"ffmpeg not found at {FFMPEG_PATH}")

from downloader import download_video
from utils import split_video

import logging

# Configure logging
logging.basicConfig(
    filename='bot_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- CONFIGURATION ---
# Get this from @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    logging.error("BOT_TOKEN not found in environment variables.")
    print("Error: BOT_TOKEN not found. Make sure the BOT_TOKEN environment variable is set in your Render Dashboard (or .env file locally).")
    exit(1) 

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    logging.info(f"Received start command from {message.from_user.username}")
    try:
        bot.reply_to(message, "Hello! Send me a link from TikTok, Instagram, Facebook, or YouTube, and I'll try to download it for you.")
    except Exception as e:
        logging.error(f"Error sending welcome message: {e}")

@bot.message_handler(func=lambda message: True) # Catch all text messages
def handle_message(message):
    url = message.text.strip()
    logging.info(f"Received message: {url} from {message.from_user.username}")
    
    # Basic validation (naive)
    if not url.startswith("http"):
        logging.warning("Invalid URL received")
        try:
            bot.reply_to(message, "That doesn't look like a valid link. Please send a URL starting with http/https.")
        except Exception as e:
            logging.error(f"Error sending invalid URL message: {e}")
        return

    try:
        bot.reply_to(message, "Downloading... Please wait. ⏳")
    except Exception as e:
        logging.error(f"Error sending downloading message: {e}")
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
                    logging.info(f"File {file_path} is larger than 50MB ({file_size:.2f}MB). Splitting...")
                    bot.reply_to(message, f"File is large ({file_size:.2f}MB). Splitting into parts... 🔪")
                    
                    try:
                        parts = split_video(file_path, max_size_mb=49)
                        if not parts:
                             bot.reply_to(message, "Failed to split video. 😔")
                             continue
                             
                        for i, part_path in enumerate(parts):
                             logging.info(f"Sending part {i+1}/{len(parts)}: {part_path}")
                             with open(part_path, 'rb') as part_file:
                                 bot.send_video(message.chat.id, part_file, caption=f"Part {i+1} of {len(parts)} 📦", timeout=600)
                             
                             # Clean up part
                             try:
                                 os.remove(part_path)
                             except:
                                 pass
                    except Exception as e:
                        logging.error(f"Error splitting/sending parts: {e}")
                        bot.reply_to(message, f"Error processing large file: {e}")

                else:
                    # Send normally if <= 50MB
                    with open(file_path, 'rb') as file_obj:
                        if file_ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.heic']:
                            logging.info("Sending as photo...")
                            bot.send_photo(message.chat.id, file_obj, caption="📸")
                        else:
                            logging.info("Sending as video...")
                            bot.send_video(message.chat.id, file_obj, caption="🎥", timeout=600)
                
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
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"Bot stopped: {e}")
