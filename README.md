---
title: Telegram Bot
emoji: 🤖
colorFrom: blue
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
license: mit
---

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

## ☁️ Deployment Guide (Free 24/7 Hosting)

### Deploying to Hugging Face Spaces (Recommended)
This bot is pre-configured to run completely free 24/7 on Hugging Face Spaces.

1. **Push your code to GitHub**:
   Run the `update_github.bat` file to push your latest changes to your GitHub repository.
   
2. **Create a Hugging Face Space**:
   - Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click "Create new Space".
   - Select **Docker** as the SDK.
   - Choose a blank template.

3. **Link to GitHub**:
   - Go to your Space settings and link it to your GitHub repository. Hugging Face will automatically build your Dockerfile.

4. **Add Secrets (CRITICAL)**:
   - Go to your Space **Settings** -> **Variables and Secrets**.
   - Under **Secrets**, add the following (do NOT put them in public variables):
     - `BOT_TOKEN`: Your bot token from BotFather.
     - `ADMIN_IDS`: Your Telegram ID.
     - `UPI_ID`: Your UPI ID for payments.
     - `EMAIL_PASSWORD`: Your 16-letter Gmail App Password (if you want email notifications).

5. **24/7 Uptime**:
   The `main.py` file contains a built-in "Heartbeat" server on port 7860. Hugging Face will keep pinging this port, ensuring your bot never goes to sleep!

### Railway / Render

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
