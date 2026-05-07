from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from config import SERVICES, ADMIN_IDS, UPI_ID
from database.db import add_user, get_user_orders, add_support_message
from utils.logger import logger

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message and the main menu."""
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    
    logger.info(f"User {user.id} started the bot.")
    
    welcome_text = (
        f"👑 *Welcome to Nexus Software Studio, {user.first_name}!*\n\n"
        "Transforming your ideas into digital excellence. We provide premium solutions for Web, App, and Design projects.\n\n"
        "✨ *Select a service below to begin your journey:* "
    )
    
    keyboard = [
        [KeyboardButton(SERVICES["website"]), KeyboardButton(SERVICES["android"])],
        [KeyboardButton(SERVICES["ppt_pdf"]), KeyboardButton(SERVICES["editing"])],
        [KeyboardButton(SERVICES["design"]), KeyboardButton(SERVICES["automation"])],
        [KeyboardButton("📦 My Orders"), KeyboardButton("💬 Support")]
    ]
    
    if user.id in ADMIN_IDS:
        keyboard.append([KeyboardButton("🛠 Admin Panel")])
        
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows the user's order history."""
    user_id = update.effective_user.id
    orders = get_user_orders(user_id)
    
    if not orders:
        await update.message.reply_text("📦 You haven't placed any orders yet. Select a service to start!")
        return
    
    text = "📊 *Project Portfolio Summary*\n\n"
    for order in orders:
        text += (
            f"💠 *Order #{order['order_id']}*\n"
            f"📁 Category: {order['service_type']}\n"
            f"📌 Project: {order['title']}\n"
            f"🕒 Status: _{order['status']}_\n"
            f"💳 Payment: _{order['payment_status']}_\n"
            "━━━━━━━━━━━━━━━━━━\n"
        )
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows support contact info."""
    text = (
        "🤝 *Concierge Support*\n\n"
        "Our team is dedicated to your success. If you have specific inquiries or need assistance with an existing project, please reach out.\n\n"
        "📥 *Message us below, and a lead consultant will respond shortly.*"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles any random message sent to the bot."""
    user = update.effective_user
    msg_text = update.message.text
    
    # NEW: Trigger main menu if user types common keywords
    if msg_text.lower() in ["start", "menu", "hi", "hello", "hey"]:
        await start(update, context)
        return

    # Ignore if it's a menu button text (those are handled by other handlers)
    if msg_text in SERVICES.values() or msg_text in ["📦 My Orders", "💳 Payment Info", "💬 Support", "🛠 Admin Panel"]:
        return

    # 1. Save to Database
    add_support_message(user.id, msg_text)
    
    # 2. Professional Auto-Reply
    reply = (
        "📩 *Inquiry Acknowledged*\n\n"
        "Thank you for reaching out to **Nexus Software Studio**. Your message has been logged in our system, and our specialists will review it shortly.\n\n"
        "⚡ *Need to start a new project?* Use the menu buttons below to initiate a formal intake."
    )
    await update.message.reply_text(reply, parse_mode="Markdown")
    
    # 3. Notify Admin
    admin_notify = (
        "💬 *NEW SUPPORT MESSAGE*\n\n"
        f"👤 From: {user.first_name} (@{user.username})\n"
        f"🆔 ID: `{user.id}`\n\n"
        f"📝 Message:\n_{msg_text}_"
    )
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=admin_notify, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to notify admin of support msg: {e}")
