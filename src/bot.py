import os
import re
import asyncio
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession
import hashlib

# دریافت تنظیمات از محیط
API_ID = int(os.environ.get('API_ID', 31356424))
API_HASH = os.environ.get('API_HASH', '45ef11a0374c78dc7ced3d28f5cec9b5')
SOURCE_CHANNEL = os.environ.get('SOURCE_CHANNEL', 'https://t.me/filembad')
TARGET_CHANNEL = os.environ.get('TARGET_CHANNEL', '@TaKziBaM')
SESSION_STRING = os.environ.get('SESSION_STRING', '')

print("="*50)
print("🤖 ربات مدیریت کانال تلگرام")
print("="*50)
print(f"API_ID: {API_ID}")
print(f"SOURCE: {SOURCE_CHANNEL}")
print(f"TARGET: {TARGET_CHANNEL}")

# توابع کمکی
def replace_filembad(text):
    """جایگزینی filembad با TaKziBaM"""
    if 'filembad' in text:
        text = text.replace('filembad', 'TaKziBaM')
    return text

def clean_config_text(text):
    """پاکسازی متن کانفیگ"""
    text = text.strip()
    text = re.sub(r'[\n\r]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(vless|vmess|trojan|ss|https):\s*//', r'\1://', text, flags=re.IGNORECASE)
    return text

def extract_clean_config(config_text):
    """استخراج کانفیگ تمیز"""
    config_text = re.sub(r'@TaKziBaM\s*$', '', config_text, flags=re.IGNORECASE)
    config_text = re.sub(r'@TaKziBaM', '', config_text, flags=re.IGNORECASE)
    return clean_config_text(config_text)

def get_config_hash(config_text):
    """ایجاد هش منحصر به فرد"""
    clean = config_text.lower().strip()
    clean = re.sub(r'\s+', '', clean)
    clean = re.sub(r'@takzibam', '', clean, flags=re.IGNORECASE)
    return hashlib.md5(clean.encode()).hexdigest()

async def main():
    """تابع اصلی"""
    # بررسی session string
    if not SESSION_STRING:
        print("❌ خطا: SESSION_STRING یافت نشد!")
        print("لطفاً در GitHub Secrets تنظیم کنید.")
        return
    
    # ایجاد کلاینت با StringSession
    try:
        session = StringSession(SESSION_STRING)
        client = TelegramClient(session, API_ID, API_HASH)
        
        # اتصال
        print("🔗 در حال اتصال به تلگرام...")
        await client.connect()
        
        # بررسی اعتبار session
        if not await client.is_user_authorized():
            print("❌ خطا: session string نامعتبر!")
            return
        
        # اطلاعات کاربر
        me = await client.get_me()
        print(f"✅ متصل شد: {me.first_name} (@{me.username})")
        
        # دریافت کانال‌ها
        try:
            source_entity = await client.get_entity(SOURCE_CHANNEL)
            target_entity = await client.get_entity(TARGET_CHANNEL)
            print(f"📥 کانال منبع: {source_entity.title}")
            print(f"📤 کانال مقصد: {target_entity.title}")
        except Exception as e:
            print(f"❌ خطا در دریافت کانال‌ها: {e}")
            print("مطمئن شوید ربات عضو هر دو کانال است.")
            return
        
        # بارگذاری hashهای ارسال شده قبلی (برای GitHub Actions باید ذخیره/بازیابی شود)
        sent_hashes = set()
        
        # دریافت پیام‌های جدید (آخرین 30 پیام)
        messages = await client.get_messages(source_entity, limit=30)
        print(f"📨 {len(messages)} پیام دریافت شد")
        
        configs_sent = 0
        proxies_sent = 0
        
        # پردازش پیام‌ها
        for message in messages:
            if message.text:
                text = message.text
                
                # الگوهای جستجو
                V2RAY_PATTERNS = [
                    r'(vless://[^\s"\']+)',
                    r'(vmess://[^\s"\']+)',
                    r'(trojan://[^\s"\']+)',
                    r'(ss://[^\s"\']+)'
                ]
                
                TELEGRAM_PROXY_PATTERN = r'(https://t\.me/proxy[^\s"\']*)'
                
                # جستجوی کانفیگ‌های v2ray
                for pattern in V2RAY_PATTERNS:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        clean_config = replace_filembad(match)
                        clean_config = extract_clean_config(clean_config)
                        
                        if len(clean_config) < 10:
                            continue
                        
                        config_hash = get_config_hash(clean_config)
                        
                        if config_hash not in sent_hashes:
                            sent_hashes.add(config_hash)
                            
                            caption = f"کانفینگ جدید v2ray\n\n{clean_config}\n\n@{TARGET_CHANNEL.replace('@', '')}"
                            
                            try:
                                await client.send_message(
                                    target_entity,
                                    caption,
                                    link_preview=False
                                )
                                configs_sent += 1
                                print(f"✅ کانفیگ v2ray ارسال شد: {clean_config[:50]}...")
                                await asyncio.sleep(1)
                            except Exception as e:
                                print(f"❌ خطا در ارسال کانفیگ: {e}")
                
                # جستجوی پروکسی‌های تلگرام
                proxy_matches = re.findall(TELEGRAM_PROXY_PATTERN, text, re.IGNORECASE)
                for proxy in proxy_matches:
                    clean_proxy = replace_filembad(proxy)
                    clean_proxy = extract_clean_config(clean_proxy)
                    
                    if len(clean_proxy) < 10:
                        continue
                    
                    proxy_hash = get_config_hash(clean_proxy)
                    
                    if proxy_hash not in sent_hashes:
                        sent_hashes.add(proxy_hash)
                        
                        caption = f"پروکسی جدید تلگرام\n\n{clean_proxy}\n\n@{TARGET_CHANNEL.replace('@', '')}"
                        
                        try:
                            await client.send_message(
                                target_entity,
                                caption,
                                link_preview=False
                            )
                            proxies_sent += 1
                            print(f"✅ پروکسی تلگرام ارسال شد: {clean_proxy[:50]}...")
                            await asyncio.sleep(1)
                        except Exception as e:
                            print(f"❌ خطا در ارسال پروکسی: {e}")
        
        print(f"\n🎯 نتیجه نهایی: {configs_sent} کانفیگ و {proxies_sent} پروکسی ارسال شد")
        
        # قطع اتصال
        await client.disconnect()
        print("✅ اتصال قطع شد")
        
    except Exception as e:
        print(f"💥 خطای کلی: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
