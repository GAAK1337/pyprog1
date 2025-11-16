from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
import os

os.makedirs('files', exist_ok=True)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"Ваш ID: {user_id}")

async def doctor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = 'waiting_id'
    await update.message.reply_text("Введите ID пациента:")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id in user_data and user_data[user_id] == 'waiting_id':
        user_data[user_id] = text  # Сохраняем ID пациента
        await update.message.reply_text("Теперь отправьте файл")
    else:
        # Пациент ищет свои файлы
        patient_files = [f for f in os.listdir('files') if f.startswith(str(user_id) + "_")]
        for filename in patient_files:
            with open(f"files/{filename}", 'rb') as f:
                await update.message.reply_document(f)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in user_data and user_data[user_id] != 'waiting_id':
        patient_id = user_data[user_id]
        file = await update.message.document.get_file()
        filename = f"{patient_id}_{update.message.document.file_name}"
        
        await file.download_to_drive(f"files/{filename}")
        
        try:
            with open(f"files/{filename}", 'rb') as f:
                await context.bot.send_document(patient_id, f)
            await update.message.reply_text("✅ Отправлено!")
        except:
            await update.message.reply_text("❌ Ошибка")
        
        del user_data[user_id]

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("doctor", doctor))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()