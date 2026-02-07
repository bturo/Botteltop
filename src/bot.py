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
from telethon.sessions import StringSession
from src.config import (
    API_ID, API_HASH, SOURCE_CHANNEL, TARGET_CHANNEL,
    SESSION_STRING
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
    
    if not SESSION_STRING:
        logger.error("❌ SESSION_STRING یافت نشد!")
        return
    
    # ایجاد کلاینت تلگرام با StringSession
    try:
        session = StringSession(SESSION_STRING)
        client = TelegramClient(
            session,
            API_ID,
            API_HASH,
            connection_retries=3,
            timeout=20
        )
        
        # اتصال به تلگرام
        logger.info("🔗 در حال اتصال به تلگرام...")
        await client.connect()
        
        # بررسی اینکه آیا session معتبر است
        if not await client.is_user_authorized():
            logger.error("❌ session string نامعتبر است!")
            return
        
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
        
        # دریافت پیام‌های جدید (آخرین 20 پیام)
        messages = await client.get_messages(source_entity, limit=20)
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
                        clean_config = match.replace('filembad', 'TaKziBaM')
                        clean_config = clean_config.strip()
                        clean_config = re.sub(r'[\n\r]+', '', clean_config)
                        clean_config = re.sub(r'\s+', ' ', clean_config)
                        
                        if len(clean_config) < 10:
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
        
    except Exception as e:
        logger.error(f"💥 خطای کلی: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        # قطع اتصال
        try:
            if client and client.is_connected():
                await client.disconnect()
                logger.info("✅ اتصال قطع شد")
        except:
            pass

if __name__ == '__main__':
    asyncio.run(main())
