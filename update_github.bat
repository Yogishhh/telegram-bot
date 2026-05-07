@echo off
echo Starting Bot Fix Update...
cd /d "c:\Users\YASH\Desktop\telegram bot"

echo Configured Git identity...
git config --local user.email "yogishtr3515@gmail.com"
git config --local user.name "Yogishhh"

echo Initializing local repository...
if not exist .git (
    git init
)

echo Preparing files...
git add .
git commit -m "CRITICAL: Fixed admin crashes, added retry loop, and secured config"

echo Linking to GitHub...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/Yogishhh/telegram-bot.git

echo Sending fixed code to GitHub...
git branch -M main
git push -u origin main --force

echo DONE! Your GitHub is now fixed and updated.
echo Now we can set up the 24/7 hosting!
pause
