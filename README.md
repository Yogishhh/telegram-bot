# 🚀 Telegram Freelance Service Marketplace Bot

A production-ready Telegram bot for managing freelance service requests, order tracking, and administration.

## 🛠 Features
- **Service Intake**: Multi-step flow for Website, Android, Design, and Automation requests.
- **Order Tracking**: Users can view their order history and status.
- **Admin Panel**: Manage orders, update status, track analytics, and broadcast messages.
- **Manual Payments**: UPI-based payment flow with manual verification.
- **Modular Design**: Clean Python code using `python-telegram-bot`.

---

## 🚀 Setup Instructions

### 1. Get a Telegram Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram.
2. Use `/newbot` to create your bot.
3. Copy the **API Token**.

### 2. Get your Admin ID
1. Message [@userinfobot](https://t.me/userinfobot) to find your Telegram User ID.

### 3. Local Installation
1. Clone or download this project.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Update `config.py` (or create a `.env` file):
   - `BOT_TOKEN`: Your API Token.
   - `ADMIN_IDS`: Your User ID (comma-separated if multiple).
   - `UPI_ID`: Your payment ID.

### 4. Run the Bot
```bash
python main.py
```

---

## ☁️ Deployment Guide

### Railway / Render (Easiest)
1. Push this code to a GitHub repository.
2. Connect the repository to [Railway](https://railway.app/) or [Render](https://render.com/).
3. Add environment variables:
   - `BOT_TOKEN`
   - `ADMIN_IDS`
   - `UPI_ID`
4. Set the start command to: `python main.py`

### VPS (Ubuntu/Linux)
1. Install Python and Pip.
2. Clone the repo and install requirements.
3. Run with `nohup` or `screen` to keep it active:
   ```bash
   nohup python main.py &
   ```
4. Or better, use **PM2** or a **Systemd** service for auto-restart.

---

## 📂 Project Structure
- `main.py`: Entry point.
- `config.py`: Configuration & Settings.
- `handlers/`: Logic for User, Order, and Admin flows.
- `database/`: Database schema and queries.
- `utils/`: Logging and helper functions.

---

## 🛡️ License
This project is intended for professional freelance use. Modify and scale as needed!
