#!/usr/bin/env python3
"""
تست اتصال به تلگرام
"""

import asyncio
from telethon import TelegramClient

async def test():
    print("🔍 تست اتصال به تلگرام")
    
    client = TelegramClient('test', 31356424, '45ef11a0374c78dc7ced3d28f5cec9b5')
    
    try:
        await client.start()
        me = await client.get_me()
        print(f"✅ موفق! شما: {me.first_name}")
        
        # تست کانال
        try:
            channel = await client.get_entity('https://t.me/filembad')
            print(f"✅ کانال یافت شد: {channel.title}")
        except:
            print("⚠️ کانال یافت نشد")
        
        await client.disconnect()
        print("✅ تست کامل شد")
        
    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == '__main__':
    asyncio.run(test())
