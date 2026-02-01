import requests
import base64
import asyncio
import re
from typing import List
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

# ────────────────────────────────────────────────
# لیست منابع GitHub (فقط بهترین و پایدارترین‌ها)
# ────────────────────────────────────────────────
SOURCES = [
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/all_sub.txt",
    "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/super-sub.txt",
    "https://raw.githubusercontent.com/SoliSpirit/v2ray-configs/main/all_configs.txt",
]

# ────────────────────────────────────────────────
# تنظیمات تلگرام
# ────────────────────────────────────────────────
API_ID = 35891940                    # ← عدد api_id خودت رو اینجا بگذار
API_HASH = 'dd3090e2039b0b8db6f2ae3a7b3dc6f4'   # ← api_hash خودت رو اینجا بگذار
PHONE_NUMBER = '+989399492648'      # ← شماره تلفن خودت با +98

# کانال‌های خیلی معتبر (فقط این‌ها نگه داشته شدن)
TELEGRAM_CHANNELS = [
    '@VmessProtocol',
    '@V2rayNGn',
    '@free4allVPN',
    '@PrivateVPNs',
    '@sinavm',
]

# ────────────────────────────────────────────────
# دریافت کانفیگ از یک URL (GitHub یا هر منبع دیگه)
# ────────────────────────────────────────────────
def fetch_configs_from_url(url: str) -> List[str]:
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        lines = [line.strip() for line in response.text.splitlines() if line.strip()]
        # فقط vmess و vless
        valid_prefixes = ('vmess://', 'vless://')
        valid_configs = [line for line in lines if line.startswith(valid_prefixes)]
        return valid_configs
    except Exception as e:
        print(f"خطا در دریافت از {url}: {e}")
        return []

# ────────────────────────────────────────────────
# جمع‌آوری همه کانفیگ‌ها از GitHub
# ────────────────────────────────────────────────
def collect_from_github() -> List[str]:
    all_configs = set()
    for url in SOURCES:
        configs = fetch_configs_from_url(url)
        all_configs.update(configs)
        print(f"از {url} → {len(configs)} کانفیگ")
    return list(all_configs)

# ────────────────────────────────────────────────
# دریافت کانفیگ از یک کانال تلگرام
# ────────────────────────────────────────────────
async def fetch_from_telegram(channel_username: str, limit: int = 60) -> List[str]:
    configs = set()
    client = TelegramClient('telegram_session', API_ID, API_HASH)

    try:
        await client.start(phone=PHONE_NUMBER)

        entity = await client.get_entity(channel_username)
        messages = await client(GetHistoryRequest(
            peer=entity,
            limit=limit,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            max_id=0,
            min_id=0,
            hash=0
        ))

        pattern = re.compile(r'(vmess://|vless://)[^\s<>\"]+')

        for message in messages.messages:
            if message.message:
                found = pattern.findall(message.message)
                configs.update(found)

        print(f"از کانال {channel_username} → {len(configs)} کانفیگ پیدا شد")

    except Exception as e:
        print(f"خطا در دریافت از کانال {channel_username}: {e}")

    finally:
        await client.disconnect()

    return list(configs)

# ────────────────────────────────────────────────
# ذخیره کانفیگ‌ها در فایل
# ────────────────────────────────────────────────
def save_to_files(configs: List[str]):
    if not configs:
        print("هیچ کانفیگی برای ذخیره وجود ندارد.")
        return

    # فایل متنی ساده
    with open("all_configs.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(configs))
    print(f"فایل all_configs.txt ساخته شد ({len(configs)} کانفیگ)")

    # فایل base64 برای سابسکریپشن
    content = "\n".join(configs).encode("utf-8")
    encoded = base64.b64encode(content).decode("utf-8")
    with open("all_configs_base64.txt", "w", encoding="utf-8") as f:
        f.write(encoded)
    print("فایل all_configs_base64.txt هم ساخته شد (برای سابسکریپشن لینک)")

# ────────────────────────────────────────────────
# نقطه ورود اصلی
# ────────────────────────────────────────────────
if __name__ == "__main__":
    print("شروع جمع‌آوری کانفیگ‌ها...\n")

    # ۱. از GitHub
    github_configs = collect_from_github()

    # ۲. از تلگرام
    telegram_configs = []
    loop = asyncio.get_event_loop()
    for channel in TELEGRAM_CHANNELS:
        tg_result = loop.run_until_complete(
            fetch_from_telegram(channel, limit=60)
        )
        telegram_configs.extend(tg_result)

    # ترکیب و حذف تکراری‌ها
    all_configs = github_configs + telegram_configs
    all_configs = list(set(all_configs))  # حذف دقیق تکراری‌ها

    print(f"\nتعداد کانفیگ‌های منحصربه‌فرد نهایی (GitHub + تلگرام): {len(all_configs)}")

    save_to_files(all_configs)

    print("\nپایان اجرا.")