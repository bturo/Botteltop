import os
import re
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaDocument
import hashlib
from collections import deque
import time

# دریافت تنظیمات از متغیرهای محیطی (GitHub Secrets)
API_ID = int(os.environ.get('API_ID', 31356424))
API_HASH = os.environ.get('API_HASH', '45ef11a0374c78dc7ced3d28f5cec9b5')
SOURCE_CHANNEL = os.environ.get('SOURCE_CHANNEL', 'https://t.me/filembad')
TARGET_CHANNEL = os.environ.get('TARGET_CHANNEL', '@TaKziBaM')
SESSION_STRING = os.environ.get('SESSION_STRING', '')  # دریافت session string از Secrets

print("="*50)
print("🤖 ربات مدیریت کانال تلگرام")
print(f"API_ID: {API_ID}")
print(f"SOURCE: {SOURCE_CHANNEL}")
print(f"TARGET: {TARGET_CHANNEL}")
print(f"SESSION_STRING: {'✅ دارد' if SESSION_STRING else '❌ ندارد'}")
print("="*50)

# ایجاد دایرکتوری برای فایل‌های موقت
TEMP_DIR = 'temp_configs'
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# صف‌های ذخیره سازی - حداکثر 10 آیتم
config_queue = deque(maxlen=10)  # کانفیگ‌های v2ray و پروکسی
file_counter = 1

# ست‌های هش برای جلوگیری از تکراری
sent_hashes = set()
last_send_time = 0
SEND_INTERVAL = 120  # هر 120 ثانیه یکبار

# الگوهای شناسایی کانفیگ‌ها
V2RAY_PATTERNS = [
    r'(vless://[^\s"\']+)',
    r'(vmess://[^\s"\']+)',
    r'(trojan://[^\s"\']+)',
    r'(ss://[^\s"\']+)'
]

TELEGRAM_PROXY_PATTERN = r'(https://t\.me/proxy[^\s"\']*)'

# جایگزینی filembad با TaKziBaM
def replace_filembad(text):
    # جایگزینی filembad در هر جای متن
    if 'filembad' in text:
        text = text.replace('filembad', 'TaKziBaM')
    return text

# پاکسازی متن برای قابل کپی بودن
def clean_config_text(text):
    # حذف کاراکترهای غیرمجاز و فاصله‌های اضافی
    text = text.strip()
    text = re.sub(r'[\n\r]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    # حذف فاصله بعد از : در vless://
    text = re.sub(r'(vless|vmess|trojan|ss|https):\s*//', r'\1://', text, flags=re.IGNORECASE)
    return text

# استخراج خالص کانفیگ از متن
def extract_clean_config(config_text):
    # حذف @TaKziBaM از انتهای کانفیگ
    config_text = re.sub(r'@TaKziBaM\s*$', '', config_text, flags=re.IGNORECASE)
    config_text = re.sub(r'@TaKziBaM', '', config_text, flags=re.IGNORECASE)
    return clean_config_text(config_text)

# ایجاد هش منحصر به فرد
def get_config_hash(config_text):
    # نرمال‌سازی کانفیگ برای تشخیص بهتر تکراری
    clean = config_text.lower().strip()
    clean = re.sub(r'\s+', '', clean)  # حذف تمام فاصله‌ها
    clean = re.sub(r'@takzibam', '', clean, flags=re.IGNORECASE)  # حذف تگ
    return hashlib.md5(clean.encode()).hexdigest()

# کلاینت تلگرام - با StringSession اگر SESSION_STRING وجود داشته باشد
if SESSION_STRING:
    from telethon.sessions import StringSession
    session = StringSession(SESSION_STRING)
    client = TelegramClient(session, API_ID, API_HASH)
else:
    # حالت fallback: از فایل session استفاده کن
    client = TelegramClient('channel_admin_session', API_ID, API_HASH)

# تابع برای ارسال کانفیگ‌ها هر 120 ثانیه
async def process_queue():
    global last_send_time
    
    while True:
        current_time = time.time()
        
        # اگر 120 ثانیه گذشته و صف خالی نیست
        if config_queue and (current_time - last_send_time >= SEND_INTERVAL):
            item_type, item_data = config_queue.popleft()
            item_hash = get_config_hash(item_data)
            
            # دوباره چک کن که تکراری نباشه
            if item_hash not in sent_hashes:
                try:
                    if item_type == 'v2ray':
                        caption = f"کانفینگ جدید v2ray\n\n{item_data}\n\n@{TARGET_CHANNEL.replace('@', '')}"
                    elif item_type == 'proxy':
                        caption = f"پروکسی جدید تلگرام\n\n{item_data}\n\n@{TARGET_CHANNEL.replace('@', '')}"
                    
                    await client.send_message(
                        TARGET_CHANNEL,
                        caption,
                        link_preview=False
                    )
                    
                    sent_hashes.add(item_hash)
                    last_send_time = current_time
                    print(f"✅ {item_type} ارسال شد (باقی مانده در صف: {len(config_queue)})")
                    
                    await asyncio.sleep(2)  # تاخیر کوتاه
                    
                except Exception as e:
                    print(f"❌ خطا در ارسال {item_type}: {e}")
                    # اگر خطا خورد، آیتم را برگردان به ابتدای صف
                    config_queue.appendleft((item_type, item_data))
        
        await asyncio.sleep(10)  # چک کردن هر 10 ثانیه

# هندلر پیام‌ها
@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handle_new_message(event):
    global file_counter
    
    message = event.message
    print(f"📩 پیام جدید دریافت شد")
    
    # پردازش متن پیام برای کانفیگ‌ها و پروکسی‌ها
    if message.text:
        text = message.text
        
        # جستجوی کانفیگ‌های v2ray
        for pattern in V2RAY_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # جایگزینی filembad با TaKziBaM
                clean_config = replace_filembad(match)
                clean_config = extract_clean_config(clean_config)
                
                # بررسی اینکه کانفیگ خالی نباشد
                if not clean_config or len(clean_config) < 10:
                    continue
                
                # ایجاد هش
                config_hash = get_config_hash(clean_config)
                
                # بررسی تکراری نبودن
                if config_hash not in sent_hashes:
                    # بررسی وجود در صف
                    already_in_queue = any(
                        get_config_hash(item_data) == config_hash 
                        for _, item_data in config_queue
                    )
                    
                    if not already_in_queue:
                        config_queue.append(('v2ray', clean_config))
                        print(f"➕ کانفیگ v2ray به صف اضافه شد: {clean_config[:50]}...")
        
        # جستجوی پروکسی‌های تلگرام
        proxy_matches = re.findall(TELEGRAM_PROXY_PATTERN, text, re.IGNORECASE)
        for proxy in proxy_matches:
            # جایگزینی filembad با TaKziBaM
            clean_proxy = replace_filembad(proxy)
            clean_proxy = extract_clean_config(clean_proxy)
            
            # بررسی اینکه پروکسی خالی نباشد
            if not clean_proxy or len(clean_proxy) < 10:
                continue
            
            # ایجاد هش
            proxy_hash = get_config_hash(clean_proxy)
            
            # بررسی تکراری نبودن
            if proxy_hash not in sent_hashes:
                # بررسی وجود در صف
                already_in_queue = any(
                    get_config_hash(item_data) == proxy_hash 
                    for _, item_data in config_queue
                )
                
                if not already_in_queue:
                    config_queue.append(('proxy', clean_proxy))
                    print(f"➕ پروکسی به صف اضافه شد: {clean_proxy[:50]}...")
        
        print(f"📊 وضعیت صف: {len(config_queue)} آیتم")
    
    # پردازش فایل‌ها - در لحظه ارسال می‌شود
    elif message.media:
        try:
            # دانلود فایل برای بررسی
            temp_path = os.path.join(TEMP_DIR, f"temp_{file_counter}")
            await client.download_media(message, temp_path)
            
            # بررسی پسوند فایل
            file_name = message.file.name if message.file else f"file_{file_counter}"
            
            # بررسی پسوند‌های مورد نظر
            if file_name and file_name.lower().endswith(('.npvt', '.hat', '.nptv')):
                # تعیین نوع کانفیگ بر اساس پسوند
                if file_name.lower().endswith(('.npvt', '.nptv')):
                    file_type = 'نپستر'
                    ext = 'npvt'
                else:
                    file_type = 'هاتونل'
                    ext = 'hat'
                
                # ایجاد نام جدید
                new_name = f"{TARGET_CHANNEL.replace('@', '')} ({file_counter}).{ext}"
                new_path = os.path.join(TEMP_DIR, new_name)
                
                # تغییر نام فایل
                os.rename(temp_path, new_path)
                
                # آماده کردن کپشن
                caption = f"کانفینگ جدید {file_type}\n@{TARGET_CHANNEL.replace('@', '')}"
                
                # ارسال فایل به کانال مقصد در لحظه
                await client.send_file(
                    TARGET_CHANNEL,
                    new_path,
                    caption=caption
                )
                
                # حذف فایل موقت
                os.remove(new_path)
                
                file_counter += 1
                print(f"📁 فایل کانفیگ ارسال شد: {new_name}")
            else:
                # حذف فایل موقت اگر پسوند مورد نظر نبود
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            print(f"❌ خطا در پردازش فایل: {e}")

# نمایش وضعیت
async def show_status():
    while True:
        await asyncio.sleep(30)
        if config_queue:
            next_send_in = max(0, SEND_INTERVAL - (time.time() - last_send_time))
            print(f"\n📊 وضعیت:")
            print(f"   آیتم‌ها در صف: {len(config_queue)}")
            print(f"   ارسال بعدی در: {int(next_send_in)} ثانیه")
            if config_queue:
                print(f"   آیتم بعدی: {config_queue[0][0]}")
            print("-" * 40)

async def main():
    global last_send_time
    
    # دریافت اطلاعات جلسه
    if SESSION_STRING:
        # اگر session string داریم، فقط connect کنیم
        await client.connect()
        
        # بررسی اعتبار session
        if not await client.is_user_authorized():
            print("❌ خطا: session string نامعتبر است!")
            return
    else:
        # اگر session string نداریم، از client.start استفاده کنیم
        await client.start()
    
    # دریافت اطلاعات کانال‌ها
    print("=" * 50)
    print("🤖 ربات مدیریت کانال در حال اجرا است...")
    print(f"   📥 دریافت از: {SOURCE_CHANNEL}")
    print(f"   📤 ارسال به: {TARGET_CHANNEL}")
    print("=" * 50)
    
    # بررسی اتصال
    try:
        me = await client.get_me()
        print(f"   👤 ورود به عنوان: {me.first_name} (@{me.username if me.username else 'بدون یوزرنیم'})")
    except:
        print("   ⚠️ مشکل در دریافت اطلاعات کاربر")
    
    print("\n⚙️  تنظیمات:")
    print(f"   • هر {SEND_INTERVAL} ثانیه یک کانفیگ ارسال می‌شود")
    print("   • فایل‌ها در لحظه ارسال می‌شوند")
    print("   • جلوگیری کامل از ارسال تکراری")
    print(f"   • filembad → TaKziBaM جایگزینی می‌شود")
    print("=" * 50)
    print("🎯 در حال گوش دادن به پیام‌های جدید...\n")
    
    # تنظیم زمان شروع
    last_send_time = time.time() - SEND_INTERVAL  # اجازه ارسال فوری
    
    # شروع توابع کمکی
    asyncio.create_task(process_queue())
    asyncio.create_task(show_status())
    
    # اجرای ربات
    await client.run_until_disconnected()

if __name__ == '__main__':
    # تنظیم لوپ
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n🛑 ربات متوقف شد.")
    except Exception as e:
        print(f"\n💥 خطای غیرمنتظره: {e}")
    finally:
        loop.close()
