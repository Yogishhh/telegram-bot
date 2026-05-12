import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token (Get from @BotFather)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# List of Admin Telegram IDs
admin_ids_raw = os.getenv("ADMIN_IDS", "710917327")
ADMIN_IDS = [int(i.strip()) for i in admin_ids_raw.split(",") if i.strip().isdigit()]

# UPI ID for Manual Payments
UPI_ID = os.getenv("UPI_ID", "yogishtr3515@oksbi")

# Admin Email for Requirements
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "visualsbyyogzz@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))

# Hidden Minimum Prices (In INR)
MIN_PRICES = {
    "website": 2000,
    "android": 2000,
    "design": 2000,
    "automation": 2000,
    "ppt_pdf": 2000,
    "editing": 500
}

# Database File Path
DB_PATH = "database/bot_database.db"

# Service Categories
SERVICES = {
    "website": "🌐 Website Development",
    "android": "🤖 Android App",
    "design": "🎨 UI/UX Design",
    "automation": "⚙️ Automation Scripts",
    "ppt_pdf": "📄 PPT & PDF Work",
    "editing": "🖼 Image Editing"
}

# Order Statuses
STATUS_PENDING = "Pending"
STATUS_IN_PROGRESS = "In Progress"
STATUS_COMPLETED = "Completed"

# Payment Statuses
PAYMENT_UNPAID = "Unpaid"
PAYMENT_PAID = "Paid"
