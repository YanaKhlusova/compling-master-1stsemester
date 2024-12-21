import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from huggingface_hub import InferenceClient

# tg_authorization
api_id = 'your awesome token'

# hf_authorization
model_name = "Qwen/Qwen2.5-72B-Instruct"
client = InferenceClient(model_name, token='your wonderful token')

# logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO #logs info
)
logger = logging.getLogger(__name__)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: #asynchronous
    await update.message.reply_text('Привет! Вставь текст для суммаризации. Сейчас я работаю только с техническими стандартами: областью их применения, основными процессами и сокращениями в документах. ')

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: # async func for getting user message and summarizing it
    message_text = update.message.text # gets user message
        
    # summary with hf
    def llm_inference(user_text):
        """На данном этапе суммаризует разделы 'Область применения', 'Основной процесс' и подтягивает расшифровку сокращений в тексте СТО"""
        output = client.chat.completions.create(
            messages=[
                {"role": "system", "content": (
                    f"Кратко перескажи текст на русском языке."
                    f"Избегай добавления фактов, отсутствующих в оригинальном тексте, и используй только русский язык. "
                    f"Форматируй текст лаконично, делая акцент на области применения, описании основного процесса и результатах. "
                    f"Если в тексте есть сокращения, расшифруй их, используя данные после фразы: 'В настоящем стандарте используются следующие сокращения:'"
                    f"Опусти список сокращений после фразы: 'В настоящем стандарте используются следующие сокращения:'"
                    #f"Опусти список терминов после фразы: 'В настоящем стандарте применяются следующие термины с соответствующими определениями:'" # эта строка тоже не работает
                    #f"Если в тексте есть содержание или ответственность, включи эти данные в пересказ без изменений. " # Так (почти) не работает, потом изменю
                    f"Текст для суммаризации:\n\n{user_text}\n\n"
                    )

                    },
                {"role": "user",
                 "content": user_text},
                    ],
                    stream=False,
                    max_tokens=3000,
                    temperature=0.5,
                    top_p=0.1
                    )
        return output.choices[0].get('message')['content']
    response = llm_inference(message_text)
    
    # Response for user
    await update.message.reply_text(f'**Саммари**:\n\n{response}')

# Error-logger
async def error_log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning(f'Обновление {update} вызвало ошибку {context.error}')

# main func
def main() -> None:
    # app-builder
    application = ApplicationBuilder().token(api_id).build()  # my awesome token

    # /start command registration
    application.add_handler(CommandHandler("start", start))
    
    # summary-func registration
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_document)) # receives only user messages and commands

    # error-log registration
    application.add_error_handler(error_log)

    # switching the bot on
    application.run_polling()

if __name__ == "__main__":
    main()