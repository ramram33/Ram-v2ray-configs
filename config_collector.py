import requests
import base64
from typing import List

# لیست منابع GitHub – فقط معتبر و فعال‌ها
SOURCES = [
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/all_sub.txt",
    "https://raw.githubusercontent.com/SoliSpirit/v2ray-configs/main/all_configs.txt",
]

def fetch_configs_from_url(url: str) -> List[str]:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        lines = [line.strip() for line in response.text.splitlines() if line.strip()]
        valid_prefixes = ('vmess://', 'vless://')
        valid_configs = [line for line in lines if line.startswith(valid_prefixes)]
        return valid_configs
    except Exception as e:
        print(f"خطا در دریافت از {url}: {e}")
        return []

def collect_all_configs() -> List[str]:
    all_configs = set()
    for url in SOURCES:
        configs = fetch_configs_from_url(url)
        all_configs.update(configs)
        print(f"از {url} → {len(configs)} کانفیگ")
    return list(all_configs)

def save_to_files(configs: List[str]):
    if not configs:
        print("هیچ کانفیگی برای ذخیره وجود ندارد.")
        return

    with open("all_configs.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(configs))
    print(f"فایل all_configs.txt ساخته شد ({len(configs)} کانفیگ)")

    content = "\n".join(configs).encode("utf-8")
    encoded = base64.b64encode(content).decode("utf-8")
    with open("all_configs_base64.txt", "w", encoding="utf-8") as f:
        f.write(encoded)
    print("فایل all_configs_base64.txt ساخته شد")

if __name__ == "__main__":
    print("شروع جمع‌آوری کانفیگ‌ها...\n")
    configs = collect_all_configs()
    print(f"\nتعداد کانفیگ‌های منحصربه‌فرد: {len(configs)}")
    save_to_files(configs)
    print("\nپایان اجرا.")
