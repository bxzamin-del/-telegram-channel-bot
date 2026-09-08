# -telegram-channel-bot
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# تنظیمات
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_ID and str(update.effective_user.id) != str(ADMIN_ID):
        await update.message.reply_text("⛔ دسترسی ندارید.")
        return

    await update.message.reply_text(
        "🤖 دستیار مدیریت کانال فعال شد!\n\n"
        "📊 داشبورد آماری به‌زودی آماده می‌شود."
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_ID and str(update.effective_user.id) != str(ADMIN_ID):
        await update.message.reply_text("⛔ دسترسی ندارید.")
        return

    await update.message.reply_text(
        "📊 آمار کانال\n\n"
        "👥 ممبر: در حال اتصال...\n"
        "📥 دانلود: در حال اتصال...\n"
        "📈 رشد: در حال محاسبه..."
    )

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN تنظیم نشده است.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
