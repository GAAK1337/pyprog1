from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import os

os.makedirs('files', exist_ok=True)
BOT_TOKEN = "8543761148:AAGhLO-ju6OApLsPcgiLOG9nuO-hdcl0RUE"

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton("PUSH", callback_data='push_button')],
        [InlineKeyboardButton("👨‍⚕️ Я врач", callback_data='role_doctor')],
        [InlineKeyboardButton("👤 Я пациент", callback_data='role_patient')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)  # Используем правильное имя переменной
    
    await update.message.reply_text(
        f"Ваш ID: {user_id}", 
        reply_markup=reply_markup  # Используем reply_markup вместо markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == 'push_button':
        await query.edit_message_text(f"✅ Кнопка нажата!\nВаш ID: {user_id}")
    
    elif query.data == 'role_doctor':
        user_data[user_id] = 'waiting_id'
        await query.edit_message_text("👨‍⚕️ Режим врача\n\nВведите ID пациента:")
    
    elif query.data == 'role_patient':
        await query.edit_message_text(f"👤 Режим пациента\n\nВаш ID: {user_id}")

async def doctor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = 'waiting_id'
    await update.message.reply_text("Введите ID пациента:")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id in user_data and user_data[user_id] == 'waiting_id':
        user_data[user_id] = text
        await update.message.reply_text("Теперь отправьте файл")
    else:
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
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()