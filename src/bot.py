#!/usr/bin/env python3
"""
ربات مدیریت کانال تلگرام
کانفیگ‌ها را از کانال منبع گرفته و به کانال مقصد ارسال می‌کند
"""

import asyncio
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telethon import TelegramClient
from src.config import (
    API_ID, API_HASH, SOURCE_CHANNEL, TARGET_CHANNEL,
    SESSION_STRING, GIST_TOKEN, GIST_ID
)
from src.utils import (
    replace_filembad, clean_config_text, get_config_hash,
    load_from_gist, save_to_gist
)

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """تابع اصلی ربات"""
    logger.info("🚀 شروع ربات مدیریت کانال تلگرام")
    
    # بارگذاری hashهای ارسال شده
    if GIST_TOKEN and GIST_ID:
        sent_hashes = load_from_gist(GIST_TOKEN, GIST_ID)
        logger.info(f"📊 {len(sent_hashes)} هش از قبل ذخیره شده")
    else:
        sent_hashes = set()
        logger.info("📊 شروع جدید - بدون داده ذخیره شده")
    
    # ایجاد کلاینت تلگرام
    client = TelegramClient(
        'bot_session',
        API_ID,
        API_HASH,
        connection_retries=3,
        timeout=20
    )
    
    try:
        # اتصال به تلگرام
        logger.info("🔗 در حال اتصال به تلگرام...")
        
        if SESSION_STRING:
            await client.connect()
            await client.sign_in(session_string=SESSION_STRING)
            logger.info("✅ با session string وارد شد")
        else:
            await client.start()
            logger.info("✅ با start() وارد شد")
        
        # اطلاعات کاربر
        me = await client.get_me()
        logger.info(f"👤 کاربر: {me.first_name} (@{me.username})")
        
        # دریافت entity کانال‌ها
        try:
            source_entity = await client.get_entity(SOURCE_CHANNEL)
            target_entity = await client.get_entity(TARGET_CHANNEL)
            logger.info(f"📥 کانال منبع: {source_entity.title}")
            logger.info(f"📤 کانال مقصد: {target_entity.title}")
        except Exception as e:
            logger.error(f"❌ خطا در دریافت کانال‌ها: {e}")
            return
        
        # دریافت پیام‌های جدید (آخرین 30 پیام)
        messages = await client.get_messages(source_entity, limit=30)
        logger.info(f"📨 {len(messages)} پیام دریافت شد")
        
        configs_sent = 0
        proxies_sent = 0
        
        # پردازش پیام‌ها از جدید به قدیم
        for message in reversed(messages):  # از قدیم به جدید
            if message.text:
                text = message.text
                
                # الگوهای جستجو
                import re
                patterns = [
                    (r'(vless://[^\s"\']+)', 'v2ray'),
                    (r'(vmess://[^\s"\']+)', 'v2ray'),
                    (r'(trojan://[^\s"\']+)', 'v2ray'),
                    (r'(ss://[^\s"\']+)', 'v2ray'),
                    (r'(https://t\.me/proxy[^\s"\']*)', 'proxy')
                ]
                
                for pattern, config_type in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        # پاکسازی
                        clean_config = replace_filembad(match)
                        clean_config = clean_config_text(clean_config)
                        
                        if len(clean_config) < 10:
                            continue
                        
                        # بررسی تکراری
                        config_hash = get_config_hash(clean_config)
                        if config_hash in sent_hashes:
                            continue
                        
                        # ایجاد کپشن
                        if config_type == 'v2ray':
                            caption = f"کانفینگ جدید v2ray\n\n{clean_config}\n\n@{TARGET_CHANNEL.replace('@', '')}"
                        else:
                            caption = f"پروکسی جدید تلگرام\n\n{clean_config}\n\n@{TARGET_CHANNEL.replace('@', '')}"
                        
                        # ارسال
                        try:
                            await client.send_message(
                                target_entity,
                                caption,
                                link_preview=False
                            )
                            
                            # ذخیره hash
                            sent_hashes.add(config_hash)
                            
                            if config_type == 'v2ray':
                                configs_sent += 1
                            else:
                                proxies_sent += 1
                            
                            logger.info(f"✅ {config_type} ارسال شد: {clean_config[:50]}...")
                            
                            # تأخیر برای جلوگیری از محدودیت
                            await asyncio.sleep(2)
                            
                        except Exception as e:
                            logger.error(f"❌ خطا در ارسال {config_type}: {e}")
        
        logger.info(f"🎯 نتیجه: {configs_sent} کانفیگ و {proxies_sent} پروکسی ارسال شد")
        
        # ذخیره hashها در Gist
        if GIST_TOKEN and GIST_ID:
            if save_to_gist(sent_hashes, GIST_TOKEN, GIST_ID):
                logger.info(f"💾 {len(sent_hashes)} هش در Gist ذخیره شد")
            else:
                logger.error("❌ خطا در ذخیره‌سازی Gist")
        
    except Exception as e:
        logger.error(f"💥 خطای کلی: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        # قطع اتصال
        if client.is_connected():
            await client.disconnect()
            logger.info("✅ اتصال قطع شد")

if __name__ == '__main__':
    asyncio.run(main())
