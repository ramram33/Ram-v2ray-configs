import requests
import base64
from typing import List
import random
from urllib.parse import urlparse, parse_qs

# منابع معتبر و به‌روز (می‌تونی بعداً بیشتر اضافه کنی)
SOURCES = [
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    # اگر منبع دیگه‌ای داری که کیفیت خوبی داره، اینجا اضافه کن
]

def is_strict_vless_reality(link: str) -> bool:
    """
    فقط کانفیگ‌هایی که صریحاً security=reality دارند قبول می‌کند
    (نسخه سخت‌گیرانه برای جلوگیری از کانفیگ‌های ناقص یا جعلی)
    """
    if not link.startswith("vless://"):
        return False
    
    try:
        parsed = urlparse(link)
        query_params = parse_qs(parsed.query)
        
        # شرط اصلی و سخت‌گیرانه: حتماً security=reality باید وجود داشته باشد
        security_values = query_params.get("security", [])
        return "reality" in security_values
    except Exception:
        return False

def fetch_configs_from_url(url: str) -> List[str]:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        lines = [line.strip() for line in response.text.splitlines() if line.strip() and not line.startswith('#')]
        
        # فقط لینک‌های vless
        vless_links = [line for line in lines if line.startswith("vless://")]
        
        # فیلتر سخت‌گیرانه Reality
        reality_links = [link for link in vless_links if is_strict_vless_reality(link)]
        
        return reality_links
    except Exception as e:
        print(f"خطا در دریافت از {url}: {e}")
        return []

def collect_all_configs() -> List[str]:
    all_configs = set()  # برای حذف تکراری‌ها
    for url in SOURCES:
        configs = fetch_configs_from_url(url)
        all_configs.update(configs)
        print(f"از {url:<70} → {len(configs):>4} کانفیگ VLESS + Reality (سخت‌گیرانه)")
    return list(all_configs)

def save_to_files(configs: List[str]):
    if not configs:
        print("\nهیچ کانفیگ VLESS + Reality (با security=reality) پیدا نشد.")
        return
    
    # اگر تعداد خیلی زیاد بود، نمونه‌برداری تصادفی
    max_keep = 500   # ← این عدد رو می‌تونی تغییر بدی (200، 800، 1500 و ...)
    displayed_count = len(configs)
    
    if len(configs) > max_keep:
        configs = random.sample(configs, max_keep)
        print(f"  → نمونه‌برداری تصادفی: {len(configs)} از {displayed_count} نگه داشته شد")
    
    # ذخیره در فایل متنی معمولی
    with open("reality_strict_configs.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(configs) + "\n")
    print(f"فایل reality_strict_configs.txt ساخته شد ({len(configs)} کانفیگ)")
    
    # ذخیره نسخه base64 (برای subscribe سریع در اپ‌ها)
    content = "\n".join(configs).encode("utf-8")
    encoded = base64.b64encode(content).decode("utf-8")
    with open("reality_strict_configs_base64.txt", "w", encoding="utf-8") as f:
        f.write(encoded)
    print("فایل reality_strict_configs_base64.txt ساخته شد")

if __name__ == "__main__":
    print("شروع جمع‌آوری کانفیگ‌های VLESS + Reality (نسخه سخت‌گیرانه) ...\n")
    configs = collect_all_configs()
    print(f"\nتعداد منحصربه‌فرد پیدا شده: {len(configs)}")
    save_to_files(configs)
    print("\nپایان اجرا.\n")
