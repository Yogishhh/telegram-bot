from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from config import SERVICES
from database.db import create_order
from utils.logger import logger

# States for Order Conversation
(
    SELECT_SERVICE,
    GET_TITLE,
    GET_DESCRIPTION,
    GET_BUDGET,
    GET_DEADLINE,
    GET_CONTACT,
    GET_PAYMENT_METHOD,
    CONFIRM_ORDER
) = range(8)

async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the order process based on the selected service."""
    service_text = update.message.text
    # Determine which service was selected
    service_type = None
    for key, val in SERVICES.items():
        if service_text == val:
            service_type = val
            break
    
    if not service_type:
        return ConversationHandler.END # Not a service button

    context.user_data['service_type'] = service_type
    
    await update.message.reply_text(
        f"💎 *Great Choice!* You've selected our **{service_type}** service.\n\n"
        "To provide the best results, let's capture your project vision.\n\n"
        "💡 *Step 1:* Please enter a professional **Project Title** (e.g., 'E-commerce Brand Portal'):",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return GET_TITLE

async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['title'] = update.message.text
    await update.message.reply_text(
        "📄 *Step 2:* Please provide a **Detailed Vision**. What are the key features and target audience?",
        parse_mode="Markdown"
    )
    return GET_DESCRIPTION

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['description'] = update.message.text
    await update.message.reply_text(
        "💰 *Step 3:* What is your **Estimated Investment**? (e.g., '₹5000' or 'Negotiable')",
        parse_mode="Markdown"
    )
    return GET_BUDGET

async def get_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    budget_input = update.message.text
    context.user_data['budget'] = budget_input
    
    # --- STRICT BUDGET VALIDATION ---
    from config import MIN_PRICES, SERVICES
    import re
    
    # 1. Find service key
    service_key = "website" # Default
    for k, v in SERVICES.items():
        if context.user_data['service_type'] == v:
            service_key = k
            break
    
    # 2. Extract number (handle commas like 1,000)
    clean_input = budget_input.replace(',', '')
    budget_numbers = re.findall(r'\d+', clean_input)
    user_budget = int(budget_numbers[0]) if budget_numbers else 0
    
    # 3. Detect Currency
    is_usd = any(curr in budget_input.lower() for curr in ["$", "usd", "dollar", "bucks"])
    
    # 4. Set Thresholds based on your exact rules
    if is_usd:
        min_threshold = 20 if service_key != "editing" else 5
        currency_symbol = "$"
    else:
        min_threshold = 2000 if service_key != "editing" else 500
        currency_symbol = "₹"
    
    logger.info(f"Budget Check: User input '{budget_input}', extracted {user_budget}, threshold {min_threshold}")
    
    if user_budget < min_threshold:
        await update.message.reply_text(
            f"⚠️ *Investment below minimum:* Our standard rate for this service starts at *{currency_symbol}{min_threshold}*.\n\n"
            "To maintain our quality standards, we cannot accept projects below this amount. Please enter a budget that meets the minimum or type /cancel."
        )
        return GET_BUDGET # Strictly loop back

    await update.message.reply_text(
        "📅 What is your desired *Deadline*? (e.g., '2 weeks' or 'June 1st')"
    )
    return GET_DEADLINE

async def get_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['deadline'] = update.message.text
    await update.message.reply_text(
        "📞 Please provide your *Contact Details* (Email, WhatsApp, or keep it as Telegram username):"
    )
    return GET_CONTACT

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['contact'] = update.message.text
    
    reply_markup = ReplyKeyboardMarkup([["🇮🇳 India (UPI/GPay)", "🌎 Other (Telegram Gift)"]], resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        "📍 *Final Step:* Are you paying from India or from another country?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return GET_PAYMENT_METHOD

async def get_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['payment_method'] = update.message.text
    
    # Show summary
    data = context.user_data
    summary = (
        "✅ *Order Summary*\n\n"
        f"🔹 *Service:* {data['service_type']}\n"
        f"📌 *Title:* {data['title']}\n"
        f"📝 *Description:* {data['description']}\n"
        f"💰 *Budget:* {data['budget']}\n"
        f"📅 *Deadline:* {data['deadline']}\n"
        f"📞 *Contact:* {data['contact']}\n"
        f"📍 *Payment via:* {data['payment_method']}\n\n"
        "Does everything look correct? Type 'yes' to confirm or /cancel to abort."
    )
    await update.message.reply_text(summary, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    return CONFIRM_ORDER

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        if update.message.text.lower() == 'yes':
            data = context.user_data
            order_id = create_order(
                user_id,
                data['service_type'],
                data['title'],
                data['description'],
                data['budget'],
                data['deadline'],
                data['contact']
            )
            
            # --- BUDGET CHECK ---
            from config import SERVICES, UPI_ID
            import re
            budget_numbers = re.findall(r'\d+', data['budget'])
            user_budget = int(budget_numbers[0]) if budget_numbers else 0
            
            # 2. Determine Payment Info based on Country
            if "India" in data.get('payment_method', ''):
                payment_instr = (
                    f"💰 *Advance Amount:* `₹{user_budget / 2}`\n"
                    f"📍 *UPI ID:* `{UPI_ID}`\n\n"
                    "Please send the screenshot of the payment here."
                )
                
                acceptance_text = (
                    f"🏅 *Vision Confirmed!* Your project request for **{data['service_type']}** has been officially logged.\n\n"
                    f"🔖 *Order Reference:* `#{order_id}`\n\n"
                    "🛡 *Our Premium Guarantee:* If we fail to deliver your project within the agreed timeline, we will issue a **100% Instant Refund**.\n\n"
                    "To initiate production immediately, please fulfill the **50% Commitment Advance**.\n\n"
                    f"{payment_instr}\n\n"
                    "✨ *Upon verification, we will share our exclusive briefing email for asset submission.*"
                )
                await update.message.reply_text(acceptance_text, parse_mode="Markdown")
            else:
                # --- TELEGRAM STARS INVOICE ---
                # Calculate stars: 50 stars = $1. (approx)
                # If budget is in USD: (budget / 2) * 50
                # If budget is in INR: (budget / 2 / 80) * 50
                is_usd = any(curr in data['budget'].lower() for curr in ["$", "usd", "dollar", "bucks"])
                if is_usd:
                    star_amount = int((user_budget / 2) * 50)
                else:
                    star_amount = int((user_budget / 2 / 80) * 50)
                
                # Ensure at least 1 star
                star_amount = max(star_amount, 1)

                acceptance_text = (
                    f"🏅 *Vision Confirmed!* Your project request for **{data['service_type']}** has been officially logged.\n\n"
                    f"🔖 *Order Reference:* `#{order_id}`\n\n"
                    "🛡 *Our Premium Guarantee:* If we fail to deliver your project within the agreed timeline, we will issue a **100% Instant Refund**.\n\n"
                    "📍 *International Payment:* Since you are outside India, you can pay the 50% advance directly using **Telegram Stars** below."
                )
                await update.message.reply_text(acceptance_text, parse_mode="Markdown")
                
                try:
                    from telegram import LabeledPrice
                    await context.bot.send_invoice(
                        chat_id=user_id,
                        title="Project Advance (50%)",
                        description=f"Advance payment for Order #{order_id}",
                        payload=f"order_{order_id}",
                        provider_token="", # Empty for Stars
                        currency="XTR",
                        prices=[LabeledPrice("Advance Payment", star_amount)],
                        start_parameter=f"pay_order_{order_id}"
                    )
                except Exception as invoice_err:
                    logger.error(f"Invoice Error: {invoice_err}")
                    await update.message.reply_text(
                        "💰 *Alternative Payment:* Please send a **Telegram Gift** worth 50% of your budget to this bot and share the screenshot."
                    )

            # --- NOTIFY ADMIN ---
            from config import ADMIN_IDS
            admin_text = (
                "🚨 *NEW ORDER RECEIVED!*\n\n"
                f"👤 User: {update.effective_user.first_name} (@{update.effective_user.username})\n"
                f"🆔 Order ID: `#{order_id}`\n\n"
                f"🔹 Service: {data['service_type']}\n"
                f"📌 Title: {data['title']}\n"
                f"📝 Description: {data['description']}\n"
                f"💰 Budget: {data['budget']}\n"
                f"📅 Deadline: {data['deadline']}\n"
                f"📞 Contact: {data['contact']}"
            )
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_message(chat_id=admin_id, text=admin_text, parse_mode="Markdown")
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id}: {e}")
            
            # Clear data
            context.user_data.clear()
            await update.message.reply_text("✨ Use the menu below to manage your orders or start a new request.")
            return ConversationHandler.END
        else:
            await update.message.reply_text("❌ Order cancelled. You can start over by selecting a service from the menu.")
            return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in confirm_order: {e}")
        await update.message.reply_text("⚠️ An error occurred while processing your order. Please try /start again.")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Action cancelled.")
    from handlers.user_handlers import start
    await start(update, context)
    return ConversationHandler.END

order_conv_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex(f"^({'|'.join(SERVICES.values())})$"), start_order)
    ],
    states={
        GET_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
        GET_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
        GET_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_budget)],
        GET_DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_deadline)],
        GET_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
        GET_PAYMENT_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_payment_method)],
        CONFIRM_ORDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
