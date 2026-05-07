from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from config import ADMIN_IDS, STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_COMPLETED, PAYMENT_PAID, PAYMENT_UNPAID, ADMIN_EMAIL
from database.db import get_analytics, get_all_orders, update_order_status, update_payment_status, get_all_user_ids, get_order_by_id
from utils.logger import logger

# States for Broadcast
BROADCAST_MSG = 1

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows the admin dashboard."""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return

    stats = get_analytics()
    text = (
        "🛠 *Admin Dashboard*\n\n"
        f"👥 Total Users: {stats['total_users']}\n"
        f"📦 Total Orders: {stats['total_orders']}\n"
        f"✅ Completed: {stats['completed_orders']}\n"
    )
    
    keyboard = [
        ["📦 View All Orders", "📊 Analytics"],
        ["📢 Broadcast", "🔙 Back to Main Menu"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lists all orders with management options."""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return

    orders = get_all_orders()
    if not orders:
        await update.message.reply_text("📭 No orders found.")
        return

    for order in orders:
        text = (
            f"🆔 *Order #{order['order_id']}*\n"
            f"👤 User ID: `{order['user_id']}`\n"
            f"🔹 Service: {order['service_type']}\n"
            f"📌 Title: {order['title']}\n"
            f"📝 Desc: {order['description']}\n"
            f"💰 Budget: {order['budget']}\n"
            f"📅 Deadline: {order['deadline']}\n"
            f"📊 Status: `{order['status']}`\n"
            f"💳 Payment: `{order['payment_status']}`\n"
        )
        
        # Inline buttons for management
        keyboard = [
            [
                InlineKeyboardButton("🔄 Set In Progress", callback_data=f"status_progress_{order['order_id']}"),
                InlineKeyboardButton("✅ Set Completed", callback_data=f"status_done_{order['order_id']}")
            ],
            [
                InlineKeyboardButton("💰 Mark Paid", callback_data=f"pay_paid_{order['order_id']}"),
                InlineKeyboardButton("❌ Mark Unpaid", callback_data=f"pay_unpaid_{order['order_id']}")
            ],
            [InlineKeyboardButton("💬 Contact User", url=f"tg://user?id={order['user_id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles inline button clicks for order management."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("status_"):
        _, action, order_id = data.split("_")
        status = STATUS_IN_PROGRESS if action == "progress" else STATUS_COMPLETED
        update_order_status(order_id, status)
        await query.message.reply_text(f"✅ Order #{order_id} status updated to: {status}")
        
    elif data.startswith("pay_"):
        _, action, order_id = data.split("_")
        status = PAYMENT_PAID if action == "paid" else PAYMENT_UNPAID
        update_payment_status(order_id, status)
        await query.message.reply_text(f"✅ Order #{order_id} payment updated to: {status}")
        
        # --- AUTO-SEND EMAIL TO USER ON PAYMENT ---
        if action == "paid":
            order = get_order_by_id(order_id)
            if order:
                user_msg = (
                    "🎉 *Payment Received!* Thank you for the advance.\n\n"
                    f"📧 Please share your detailed project requirements, documents, or brand assets to our official email:\n\n"
                    f"📍 *Email:* `{ADMIN_EMAIL}`\n\n"
                    "Once received, we will begin the development immediately and share the prototype soon! 🚀"
                )
                try:
                    await context.bot.send_message(chat_id=order['user_id'], text=user_msg, parse_mode="Markdown")
                except Exception as e:
                    logger.error(f"Failed to send email info to user {order['user_id']}: {e}")

# Broadcast Logic
async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    await update.message.reply_text("📢 Send the message you want to broadcast to ALL users. Type /cancel to abort.")
    return BROADCAST_MSG

async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    user_ids = get_all_user_ids()
    
    count = 0
    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 *Important Update:*\n\n{msg}", parse_mode="Markdown")
            count += 1
        except Exception as e:
            logger.error(f"Failed to send broadcast to {uid}: {e}")
            
    await update.message.reply_text(f"✅ Broadcast sent to {count} users.")
    return ConversationHandler.END

async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Broadcast cancelled.")
    return ConversationHandler.END

broadcast_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^📢 Broadcast$"), start_broadcast)],
    states={
        BROADCAST_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_broadcast)]
    },
    fallbacks=[CommandHandler("cancel", cancel_broadcast)]
)
