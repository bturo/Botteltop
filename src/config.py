"""
تنظیمات ربات
"""

import os

# دریافت از محیط یا استفاده از مقادیر پیش‌فرض
API_ID = int(os.environ.get('API_ID', 31356424))
API_HASH = os.environ.get('API_HASH', '45ef11a0374c78dc7ced3d28f5cec9b5')
SOURCE_CHANNEL = os.environ.get('SOURCE_CHANNEL', 'https://t.me/filembad')
TARGET_CHANNEL = os.environ.get('TARGET_CHANNEL', '@TaKziBaM')

# برای GitHub Actions
SESSION_STRING = os.environ.get('SESSION_STRING', '')
GIST_TOKEN = os.environ.get('GIST_TOKEN', '')
GIST_ID = os.environ.get('GIST_ID', '')

# تنظیمات دیگر
CHECK_INTERVAL = 300  # ثانیه - هر 5 دقیقه
MAX_MESSAGES = 30     # تعداد پیام‌های بررسی شده
