from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import os
import threading
from flask import Flask

# ---------- keep_alive для Replit ----------
app_web = Flask(__name__)

@app_web.get("/")
def home():
    return "Bot is running!"

def _run_web():
    app_web.run(host="0.0.0.0", port=8080)

def keep_alive():
    threading.Thread(target=_run_web, daemon=True).start()


# ---------- КОНФИГ: порядок и красивые названия ----------
# Укажи ИМЕНА ФАЙЛОВ ровно как в панели слева в Replit:
ORDER = [
    "4, 5 статья ЗОКД.mp4",
    "14 статья ЗОКД.mp4",
    "16, 11, 6 статья ЗОКД.mp4",
    "Возражения.mp4",
    "Возражения 2 часть.mp4",
    "Санкции.mp4",
    "Санкции 2 часть.mp4"
]

# Как отображать подписи на кнопках (необязательно для всех)
TITLES = {
    "4, 5 статья ЗОКД.mp4": "4–5 статья ЗОКД",
    "Санкции.mp4": "Санкции",
    "Санкции часть 2.mp4": "Санкции — часть 2",
}

def get_videos():
    """Собираем итоговый список: сначала в нужном порядке из ORDER (если файл есть),
    затем все остальные .mp4, которых нет в ORDER — по алфавиту."""
    all_mp4 = [f for f in os.listdir(".") if f.lower().endswith(".mp4")]
    ordered_existing = [f for f in ORDER if f in all_mp4]
    rest = sorted([f for f in all_mp4 if f not in ordered_existing])
    return ordered_existing + rest

def pretty_name(file_name: str) -> str:
    # Подпись на кнопке: из словаря TITLES, иначе берём имя файла без .mp4
    return TITLES.get(file_name, os.path.splitext(file_name)[0])

def menu_keyboard():
    files = get_videos()
    buttons = [[InlineKeyboardButton(f"🎥 {pretty_name(f)}", callback_data=f"video::{f}")]
               for f in files]
    return InlineKeyboardMarkup(buttons)


# ---------- Команды ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Выбери урок из списка:", reply_markup=menu_keyboard())


# ---------- Кнопки ----------
async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("video::"):
        file_name = query.data.split("::", 1)[1]
        try:
            with open(file_name, "rb") as f:
                await query.message.reply_video(f, caption=f"🎥 {pretty_name(file_name)}")
        except Exception as e:
            await query.message.reply_text(f"⚠️ Не удалось отправить {file_name}: {e}")
        finally:
            await query.message.reply_text("Выбери другое видео:", reply_markup=menu_keyboard())


# ---------- Запуск ----------
def main():
    keep_alive()  # для Replit
    TOKEN = "8314917201:AAGm_Ax9pKl8NOX5_XQncUKcHKogpdAf6JY"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_button))

    print("📂 Файлы в проекте:", os.listdir("."))
    print("✅ Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()