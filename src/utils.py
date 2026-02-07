"""
توابع کمکی ربات
"""

import re
import hashlib
import json
import requests
from typing import Set

def replace_filembad(text: str) -> str:
    """جایگزینی filembad با TaKziBaM"""
    return text.replace('filembad', 'TaKziBaM')

def clean_config_text(text: str) -> str:
    """پاکسازی متن کانفیگ برای قابل کپی بودن"""
    text = text.strip()
    text = re.sub(r'[\n\r]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r':\s*//', '://', text)
    return text

def get_config_hash(config_text: str) -> str:
    """ایجاد هش منحصر به فرد برای کانفیگ"""
    clean = config_text.lower().strip()
    clean = re.sub(r'\s+', '', clean)
    clean = re.sub(r'@takzibam', '', clean, flags=re.IGNORECASE)
    return hashlib.md5(clean.encode()).hexdigest()

def save_to_gist(data: Set[str], gist_token: str, gist_id: str) -> bool:
    """ذخیره داده‌ها در GitHub Gist"""
    try:
        headers = {'Authorization': f'token {gist_token}'}
        url = f'https://api.github.com/gists/{gist_id}'
        
        files = {
            'sent_hashes.json': {
                'content': json.dumps(list(data))
            }
        }
        
        response = requests.patch(url, headers=headers, json={'files': files})
        return response.status_code == 200
    except Exception:
        return False

def load_from_gist(gist_token: str, gist_id: str) -> Set[str]:
    """بارگذاری داده‌ها از GitHub Gist"""
    try:
        headers = {'Authorization': f'token {gist_token}'}
        url = f'https://api.github.com/gists/{gist_id}'
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            content = data['files']['sent_hashes.json']['content']
            return set(json.loads(content))
    except Exception:
        pass
    return set()
