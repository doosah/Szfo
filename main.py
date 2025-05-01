import logging
import threading
import sys

# Импорт Flask приложения
from app import app

# Импорт Telegram бота
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, 
    ConversationHandler, filters
)
from config import TOKEN, logger
from database import init_database
from handlers import (
    start_command, help_command, report_command, history_command,
    city_callback, task_message, data_message, photo_message,
    skip_photo_callback, confirm_callback, cancel_callback,
    text_message_handler, error_handler,
    SELECTING_CITY, ENTERING_TASK, ENTERING_DATA, SENDING_PHOTO
)

def start_telegram_bot():
    """Запуск Telegram бота в отдельном потоке"""
    # Initialize the database
    init_database()
    
    # Create the Application
    application = Application.builder().token(TOKEN).build()
    
    # Add conversation handler for the report creation process
    report_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('report', report_command)],
        states={
            SELECTING_CITY: [
                CallbackQueryHandler(city_callback, pattern=r'^city_'),
                CallbackQueryHandler(cancel_callback, pattern=r'^cancel$')
            ],
            ENTERING_TASK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, task_message),
            ],
            ENTERING_DATA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, data_message),
            ],
            SENDING_PHOTO: [
                MessageHandler(filters.PHOTO, photo_message),
                CallbackQueryHandler(skip_photo_callback, pattern=r'^skip_photo$'),
                CallbackQueryHandler(confirm_callback, pattern=r'^confirm$'),
                CallbackQueryHandler(cancel_callback, pattern=r'^cancel$')
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_callback)],
        per_message=True
    )
    
    # Add basic command handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('history', history_command))
    
    # Add the conversation handler
    application.add_handler(report_conv_handler)
    
    # Add handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot (с асинхронным методом запуска, чтобы избежать блокировки)
    logger.info("Starting the bot...")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("Bot started successfully")
    except Exception as e:
        logger.error(f"Error starting the bot: {str(e)}")
        
    logger.info("Bot stopped")

def main():
    """Основная функция для запуска приложения"""
    # Запускаем Telegram-бота через stable_bot.py
    try:
        from stable_bot import main as bot_main
        logger.info("Запуск Telegram-бота через stable_bot.py")
        bot_main()
    except Exception as e:
        logger.error(f"Ошибка при запуске Telegram-бота: {e}")
        # При запуске через gunicorn мы только экспортируем Flask приложение
        logger.info("Запуск в режиме только Flask приложения")
        pass

# Экспортируем Flask приложение для gunicorn
from app import app as flask_app

if __name__ == '__main__':
    main()
