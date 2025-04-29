import logging
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Включение логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Состояния разговора
CHOOSING, TYPING_MESSAGE = range(2)

# Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["📢 Предложение", "❗ Ошибка", "📝 Другое"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "👋 Привет! Выбери, с чем ты хочешь обратиться:",
        reply_markup=markup
    )
    return CHOOSING

# Обработка выбора пользователя
async def choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["choice"] = text
    await update.message.reply_text(
        f"✍️ Хорошо! Напиши, что ты хочешь отправить по теме: {text}",
        reply_markup=ReplyKeyboardRemove()
    )
    return TYPING_MESSAGE

# Получение сообщения и отправка админу
async def received_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    choice = context.user_data.get("choice", "Без категории")

    message_to_admin = (
        f"📩 Новое сообщение от @{user.username or user.first_name}:\n\n"
        f"📌 Категория: {choice}\n"
        f"📝 Сообщение: {text}"
    )

    # Отправка админу
    await context.bot.send_message(chat_id=ADMIN_ID, text=message_to_admin)

    # Ответ пользователю
    await update.message.reply_text("✅ Спасибо! Мы получили твоё сообщение.")
    return ConversationHandler.END

# Команда отмены
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Основной запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choice_handler)],
            TYPING_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("🚀 Бот запущен брат")
    app.run_polling()
