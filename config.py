import os
import logging

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)
logger = logging.getLogger(__name__)

# Bot token from environment variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

# Admin IDs - should be configured via environment variables
# Multiple IDs can be provided as comma-separated values
ADMIN_IDS = []
admin_ids_str = os.getenv("ADMIN_IDS")
if admin_ids_str:
    try:
        ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",")]
    except ValueError:
        logger.error("Invalid ADMIN_IDS format. Use comma-separated integers.")
else:
    # Default admin ID for development/testing only
    logger.warning("ADMIN_IDS environment variable is not set, using default admin ID")
    ADMIN_IDS = [269896292]  # Ваш Telegram ID

# City list
CITIES = [
    "Архангельск",
    "Вологда", 
    "Великий Новгород",
    "Сыктывкар Лесопарковая",
    "Сыктывкар Октябрьский",
    "Петрозаводск",
    "Мурманск",
    "Череповец"
]

# Conversation states for ConversationHandler
SELECTING_CITY = 0
ENTERING_TASK = 1
ENTERING_DATA = 2
SENDING_PHOTO = 3
