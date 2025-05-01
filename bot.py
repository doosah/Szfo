"""
Скрипт для запуска только Telegram-бота
"""
import os
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, 
    ConversationHandler, filters
)

from config import TOKEN, logger, ADMIN_IDS
from database import init_database
from handlers import (
    start_command, help_command, report_command, history_command,
    city_callback, task_message, data_message, photo_message,
    skip_photo_callback, confirm_callback, cancel_callback,
    text_message_handler, error_handler,
    SELECTING_CITY, ENTERING_TASK, ENTERING_DATA, SENDING_PHOTO
)

async def main():
    """Запуск Telegram бота"""
    # Инициализируем базу данных
    init_database()
    
    # Создаем приложение бота
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчик диалога для создания отчетов
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
    
    # Добавляем базовые обработчики команд
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('history', history_command))
    
    # Добавляем обработчик диалога
    application.add_handler(report_conv_handler)
    
    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота и логируем информацию
    logger.info("Starting the bot...")
    logger.info(f"Admin IDs configured: {ADMIN_IDS}")
    
    # Инициализация и запуск бота
    await application.initialize()
    await application.start()
    
    logger.info("Bot is running. Press Ctrl+C to stop")
    
    # Бесконечный цикл опроса обновлений с корректной обработкой ошибок
    try:
        # Запускаем опрос сервера Telegram для получения обновлений
        await application.updater.start_polling(
            poll_interval=0.5,
            timeout=10,
            bootstrap_retries=-1,
            read_timeout=15,
            write_timeout=15,
            allowed_updates=Update.ALL_TYPES
        )
        
        # Блокируем выполнение, пока бот работает
        await application.updater.stop.wait()
        
    except Exception as e:
        logger.error(f"Critical error in bot: {e}")
    finally:
        # Убедимся, что бот корректно остановлен при выходе
        await application.stop()
        logger.info("Bot stopped gracefully")

if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")