import requests
import base64
import subprocess
import re
from typing import List
from urllib.parse import urlparse

# لیست منابع GitHub – معتبر و فعال
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

def extract_host(config: str) -> str:
    """استخراج hostname یا IP از رشته vmess:// یا vless://"""
    try:
        parsed = urlparse(config)
        if parsed.scheme in ('vmess', 'vless'):
            # برای vless://uuid@host:port?...
            # یا vmess://base64json
            if parsed.netloc:
                host_port = parsed.netloc.split('@')[-1].split(':')[0]
                return host_port
            # اگر base64 بود (vmess معمولاً)
            elif parsed.path:
                # ساده: اولین چیزی که شبیه IP یا دامنه باشه
                match = re.search(r'@(.*?):', config)
                if match:
                    return match.group(1)
        return ""
    except:
        return ""

def get_ping_ms(host: str, timeout_sec=2) -> float:
    """ping ساده به host و برگرداندن ms (اگر موفق نبود -1)"""
    if not host:
        return -1
    try:
        # دستور ping کراس‌پلتفرم (ویندوز: -n 1 -w timeout_ms, لینوکس/mac: -c 1 -W sec)
        cmd = ['ping', '-c', '1', '-W', str(timeout_sec), host] if 'win' not in subprocess.getoutput('uname') else ['ping', '-n', '1', '-w', str(timeout_sec*1000), host]
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True, timeout=timeout_sec+3)
        # استخراج زمان (time=xx ms یا time<1ms)
        match = re.search(r'time[=<](\d+\.?\d*) ?ms', output, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return -1
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception):
        return -1

def filter_low_ping_configs(configs: List[str], max_ping_ms: int = 1000) -> List[str]:
    good = []
    bad = 0
    for cfg in configs:
        host = extract_host(cfg)
        if not host:
            bad += 1
            continue
        ping = get_ping_ms(host)
        if 0 < ping <= max_ping_ms:
            good.append(cfg)
            print(f"نگه داشته شد → ping {ping:.1f} ms → {cfg[:80]}...")
        else:
            bad += 1
            print(f"حذف شد → ping {ping if ping > 0 else 'timeout'} → {cfg[:80]}...")
    print(f"\nحذف شده: {bad} تا | نگه داشته شده: {len(good)} تا")
    return good

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
    print(f"\nتعداد اولیه: {len(configs)}")

    # فیلتر پینگ
    configs = filter_low_ping_configs(configs, max_ping_ms=1000)
    print(f"تعداد بعد از فیلتر پینگ: {len(configs)}")

    save_to_files(configs)
    print("\nپایان اجرا.")
