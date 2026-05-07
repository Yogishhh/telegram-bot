import sys
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN
from database.db import init_db
from handlers.user_handlers import start, my_orders, show_support, handle_message
from handlers.order_handlers import order_conv_handler
from handlers.admin_handlers import admin_panel, view_orders, handle_callback, broadcast_handler
from utils.logger import logger

from flask import Flask
from threading import Thread

# --- KEEP-ALIVE SERVER ---
import os
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and healthy! 🚀"

def run():
    # Render provides the port via the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting keep-alive server on port {port}")
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True # Ensure thread dies when main thread dies
    t.start()

def main():
    """Starts the bot."""
    try:
        # Initialize Database
        logger.info("Initializing database...")
        init_db()
        
        # Start the keep-alive server
        keep_alive()
        
        # Check for Bot Token
        if not BOT_TOKEN or "YOUR_BOT" in BOT_TOKEN:
            logger.error("Please set your BOT_TOKEN in config.py or Environment Variables!")
            return
            
        # Build Application
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # --- User Handlers ---
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.Regex("^📦 My Orders$"), my_orders))
        application.add_handler(MessageHandler(filters.Regex("^💬 Support$"), show_support))
        
        # Order Conversation (Priority)
        application.add_handler(order_conv_handler)
        
        # Support Logger (Catch-all text messages - Low Priority)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # --- Admin Handlers ---
        application.add_handler(MessageHandler(filters.Regex("^🛠 Admin Panel$"), admin_panel))
        application.add_handler(MessageHandler(filters.Regex("^📦 View All Orders$"), view_orders))
        application.add_handler(MessageHandler(filters.Regex("^📊 Analytics$"), lambda u, c: admin_panel(u, c)))
        application.add_handler(MessageHandler(filters.Regex("^🔙 Back to Main Menu$"), start))
        
        # Admin Broadcast
        application.add_handler(broadcast_handler)
        
        # Callback Query (for inline buttons)
        application.add_handler(CallbackQueryHandler(handle_callback))
        
        # --- Error Handling ---
        async def error_handler(update, context):
            logger.error(f"Update {update} caused error {context.error}")
            
        application.add_error_handler(error_handler)
        
        # Run with retry logic
        logger.info("Bot is starting...")
        import time
        while True:
            try:
                application.run_polling()
            except Exception as e:
                logger.error(f"Bot polling crashed: {e}")
                logger.info("Restarting bot in 10 seconds...")
                time.sleep(10)
    except Exception as e:
        logger.error(f"CRITICAL ERROR DURING STARTUP: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
