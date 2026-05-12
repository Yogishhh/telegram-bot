import os
import sys
import time
import socket
import logging
import asyncio
import traceback
from threading import Thread
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, PicklePersistence
from telegram.request import HTTPXRequest

# 1. FORCE IPv4 (Fixes Hugging Face DNS/Timeout issues)
try:
    orig_getaddrinfo = socket.getaddrinfo
    def patched_getaddrinfo(*args, **kwargs):
        responses = orig_getaddrinfo(*args, **kwargs)
        return [res for res in responses if res[0] == socket.AF_INET]
    socket.getaddrinfo = patched_getaddrinfo
    logger_msg = "Forced IPv4 for all network requests."
except Exception as e:
    logger_msg = f"Failed to force IPv4: {e}"

# 2. Project Imports
from config import BOT_TOKEN
from database.db import init_db
from handlers.user_handlers import start, my_orders, show_support, handle_message
from handlers.order_handlers import order_conv_handler
from handlers.admin_handlers import admin_panel, view_orders, handle_callback, broadcast_handler
from utils.logger import logger

# Log the IPv4 status
logger.info(logger_msg)

# --- KEEP-ALIVE SERVER (Hugging Face Heartbeat) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is active and healthy! 🚀"

def run_flask():
    port = int(os.environ.get("PORT", 7860))
    logger.info(f"Starting heartbeat server on port {port}")
    try:
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask server error: {e}")

def start_keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- MAIN BOT LOGIC ---
async def start_bot():
    """Builds and starts the bot with robust settings."""
    try:
        # Initialize Database
        logger.info("Initializing database...")
        init_db()
        
        if not BOT_TOKEN:
            logger.error("CRITICAL: BOT_TOKEN is missing!")
            return

        # 3. CONFIGURE ROBUST REQUEST (60s timeouts)
        # Using HTTPXRequest for fine-grained control
        request_config = HTTPXRequest(
            connect_timeout=60,
            read_timeout=60,
            write_timeout=60,
            pool_timeout=60,
            http_version="1.1" 
        )

        # 4. BUILD APPLICATION
        # Simplified to avoid any attribute errors in different library versions
        persistence = PicklePersistence(filepath="database/bot_persistence.pickle")
        application = (
            ApplicationBuilder()
            .token(BOT_TOKEN)
            .persistence(persistence)
            .request(request_config)
            .get_updates_request(request_config)
            .build()
        )

        # 5. REGISTER HANDLERS
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.Regex("^📦 My Orders$"), my_orders))
        application.add_handler(MessageHandler(filters.Regex("^💬 Support$"), show_support))
        application.add_handler(order_conv_handler)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(MessageHandler(filters.Regex("^🛠 Admin Panel$"), admin_panel))
        application.add_handler(MessageHandler(filters.Regex("^📦 View All Orders$"), view_orders))
        application.add_handler(MessageHandler(filters.Regex("^📊 Analytics$"), admin_panel))
        application.add_handler(MessageHandler(filters.Regex("^🔙 Back to Main Menu$"), start))
        application.add_handler(broadcast_handler)
        application.add_handler(CallbackQueryHandler(handle_callback))

        # 6. RUN POLLING
        logger.info("Bot authorization successful. Starting polling...")
        
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        
        logger.info("Bot is ONLINE and 24/7 stable.")
        
        # Keep process alive
        while True:
            await asyncio.sleep(3600)

    except Exception as e:
        logger.error(f"CRITICAL STARTUP ERROR: {e}")
        logger.error(traceback.format_exc())
        await asyncio.sleep(10)
        sys.exit(1)

if __name__ == "__main__":
    start_keep_alive()
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Bot exited: {e}")
