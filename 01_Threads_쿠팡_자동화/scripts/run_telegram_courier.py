import os
import sys

sys.path.insert(0, os.path.abspath('.'))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from services.telegram_courier_service import TelegramCourierService

if __name__ == '__main__':
    courier = TelegramCourierService()
    courier.start_polling()
