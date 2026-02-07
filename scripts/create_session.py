#!/usr/bin/env python3
"""
اسکریپت ایجاد session string برای ربات
"""

import asyncio
from telethon import TelegramClient
import sys

async def create_session():
    """ایجاد session string"""
    print("🔧 ایجاد session string برای ربات تلگرام")
    print("="*50)
    
    # دریافت اطلاعات از کاربر
    api_id = input("API ID (31356424): ").strip()
    if not api_id:
        api_id = 31356424
    else:
        api_id = int(api_id)
    
    api_hash = input("API Hash (45ef11a0374c78dc7ced3d28f5cec9b5): ").strip()
    if not api_hash:
        api_hash = '45ef11a0374c78dc7ced3d28f5cec9b5'
    
    # ایجاد کلاینت
    client = TelegramClient('session_generator', api_id, api_hash)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            print("\n📱 وارد کردن اطلاعات ورود:")
            phone = input("شماره تلفن (با +): ").strip()
            
            await client.send_code_request(phone)
            print("✅ کد ارسال شد")
            
            code = input("کد 5 رقمی: ").strip()
            await client.sign_in(phone, code)
        
        # دریافت session string
        session_string = client.session.save()
        
        print("\n" + "="*50)
        print("✅ SESSION STRING ایجاد شد:")
        print("="*50)
        print(session_string)
        print("="*50)
        
        print("\n📋 دستورالعمل:")
        print("1. به GitHub Repo خود بروید")
        print("2. Settings > Secrets > Actions")
        print("3. New repository secret")
        print("4. نام: SESSION_STRING")
        print("5. مقدار: session string بالا")
        
    except Exception as e:
        print(f"❌ خطا: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(create_session())
