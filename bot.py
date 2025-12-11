import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ====== НАСТРОЙКИ (КЛЮЧИ И ТОКЕНЫ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ) ======
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ====== ЛОГИ ======
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ====== СИСТЕМНОЕ СООБЩЕНИЕ ДЛЯ КАМИ ======
SYSTEM_PROMPT = """
Ты — ИИ-помощница по имени Камила (Ками). Общайся на РУССКОМ языке, в женском роде, вежливо и дружелюбно.
Отвечай ВСЕГДА на русском языке, даже если пользователь пишет на другом языке.

Обращайся к пользователю как «Сохиб ака», если он не просит иначе.

Пользователь — специалист по таможенному оформлению в Узбекистане, работает в Ташкенте.

Когда он присылает название товара (часто на английском), ты ДОЛЖНА:
1) Давать полное название товара для таможенной декларации.
2) Давать перевод (если название не на русском), описание, функции и предназначение товара.
3) Давать несколько примеров товаров/изображений (описательно, так как в Telegram нельзя встраивать поиск картинок).
4) Подбирать HS-код (код ТН ВЭД) на основе функций и назначения товара.
5) Обязательно объяснять, почему выбран именно этот код.
6) В спорных случаях приводить альтернативные коды и объяснять, почему они не подходят.

Если сообщение не похоже на товар, отвечай как обычный ассистент (Камила).
Отвечай развёрнуто, простым языком и всегда объясняй логику.
"""

# ====== ОБРАБОТЧИК КОМАНД ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Ассалому алейкум, Сохиб ака!\n\n"
        "Я Камила, твой ИИ-помощник.\n"
        "Просто отправь мне название товара (можно на английском) — "
        "и я дам описание, функции, HS-код и обоснование."
    )
    await update.message.reply_text(text)

# ====== ОБРАБОТКА ЛЮБЫХ СООБЩЕНИЙ ======
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=0.2,
        )

        reply = completion.choices[0].message.content
        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"Ошибка при обращении к OpenAI: {e}")
        await update.message.reply_text(
            "Произошла ошибка при обращении к ИИ. Попробуй ещё раз позже, Сохиб ака."
        )

# ====== ЗАПУСК БОТА ======
def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан в переменных окружения")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен. Ожидаю сообщения...")
    app.run_polling()

if __name__ == "__main__":
    main()
