import threading
import time
import os
import json
import random
import base64
from datetime import datetime
import locale
from curl_cffi import requests as curl_requests

VERSION = "2.6"
API_BASE = "https://discord.com/api/v10"

lock = threading.Lock()
sent_messages = 0
start_time = time.time()

CHROME_VERSIONS = [
    ("131.0.0.0", "131", "chrome131"),
    ("124.0.0.0", "124", "chrome124"),
    ("123.0.0.0", "123", "chrome123"),
    ("120.0.0.0", "120", "chrome120"),
    ("110.0.0.0", "110", "chrome110"),
]

EDGE_TARGETS = ["edge101", "edge99"]


def _rand_hex(n=32):
    return os.urandom(n // 2).hex()


def _rand_uuid_like():
    return f"{_rand_hex(8)}-{_rand_hex(4)}-{_rand_hex(4)}-{_rand_hex(4)}-{_rand_hex(12)}"


class BrowserProfile:
    def __init__(self):
        self.version_full, self.version_major, self.impersonate = random.choice(CHROME_VERSIONS)
        self.is_edge = random.random() < 0.25

        if self.is_edge:
            self.impersonate = random.choice(EDGE_TARGETS)
            self.brand = "Microsoft Edge"
            self.ua = (
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                f"(KHTML, like Gecko) Chrome/{self.version_full} Safari/537.36 "
                f"Edg/{self.version_full}"
            )
        else:
            self.brand = "Google Chrome"
            self.ua = (
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                f"(KHTML, like Gecko) Chrome/{self.version_full} Safari/537.36"
            )

        self.locale = random.choice(["en-US", "en-GB"])
        self.timezone = random.choice([
            "Asia/Ho_Chi_Minh",
            "Asia/Bangkok",
            "Asia/Singapore",
            "America/New_York",
            "Europe/London",
        ])
        self.release_channel = random.choice(["stable", "stable", "stable", "ptb"])
        self.build_number = random.randint(320000, 340000)
        self.client_launch_id = _rand_uuid_like()
        self.heartbeat_session_id = _rand_uuid_like()

    def sec_ch_ua(self):
        if self.is_edge:
            return (
                f'"Microsoft Edge";v="{self.version_major}", '
                f'"Chromium";v="{self.version_major}", '
                f'"Not_A Brand";v="24"'
            )
        return (
            f'"Google Chrome";v="{self.version_major}", '
            f'"Chromium";v="{self.version_major}", '
            f'"Not_A Brand";v="24"'
        )

    def super_properties(self):
        dev = {
            "os": "Windows",
            "browser": "Edge" if self.is_edge else "Chrome",
            "device": "",
            "system_locale": self.locale,
            "browser_user_agent": self.ua,
            "browser_version": self.version_full,
            "os_version": "10",
            "release_channel": self.release_channel,
            "client_build_number": self.build_number,
            "client_launch_id": self.client_launch_id,
            "client_heartbeat_session_id": self.heartbeat_session_id,
        }
        return base64.b64encode(
            json.dumps(dev, separators=(",", ":")).encode()
        ).decode()

    def headers(self, token=None):
        h = {
            "Accept": "*/*",
            "Accept-Language": f"{self.locale},en;q=0.9",
            "Content-Type": "application/json",
            "User-Agent": self.ua,
            "X-Super-Properties": self.super_properties(),
            "X-Discord-Locale": self.locale,
            "X-Discord-Timezone": self.timezone,
            "X-Debug-Options": "bugReporterEnabled",
            "Origin": "https://discord.com",
            "Referer": "https://discord.com/channels/@me",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-CH-UA": self.sec_ch_ua(),
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": '"Windows"',
            "Priority": "u=1, i",
            "DNT": "1",
        }
        if token:
            h["Authorization"] = token
        return h


try:
    locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, '')


def get_time():
    return datetime.now().strftime("%A | %H:%M:%S | %d/%m/%Y")


def get_uptime():
    elapsed = int(time.time() - start_time)
    h, rem = divmod(elapsed, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def get_banner():
    return r"""
  
"""


def log_info(msg):
    print(f"[SYSTEM] {msg}")


def log_success(msg):
    print(f"[SYSTEM] {msg}")


def log_warning(msg):
    print(f"[SYSTEM] {msg}")


def log_input(msg):
    return input(f"[INPUT] {msg}")


def log_message(channel_id, channel_name, server_name, content, token):
    global sent_messages
    print(f"[{get_uptime()}] [MSANG] 🍀 {channel_name}")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")
    print(get_banner())
    print("=" * 60)


def read_tokens(file_name):
    if not os.path.exists(file_name):
        log_warning(f"File '{file_name}' khong ton tai!")
        return []
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            tokens = [line.strip() for line in f if line.strip()]
            return tokens
    except Exception as e:
        log_warning(f"Loi khi doc file '{file_name}': {str(e)}")
        return []


def check_live_token(token):
    prof = BrowserProfile()
    try:
        session = curl_requests.Session(impersonate=prof.impersonate, verify=False)
        headers = prof.headers(token)
        r = session.get(f"{API_BASE}/users/@me", headers=headers, timeout=15)
        if r.status_code == 200:
            data = r.json()
            username = data.get("username", "Unknown")
            discriminator = data.get("discriminator", "0")
            if discriminator and discriminator != "0":
                return True, f"{username}#{discriminator}"
            return True, username
        return False, None
    except Exception:
        return False, None


def save_die_token(token):
    try:
        with open("die.txt", "a", encoding="utf-8") as f:
            f.write(token + "\n")
    except Exception:
        pass


def check_live_all(tokens):
    log_info(f"Dang kiem tra {len(tokens)} token...")
    live_tokens = []
    die_count = 0
    for i, token in enumerate(tokens, 1):
        ok, name = check_live_token(token)
        short = f"{token[:8]}...{token[-6:]}"
        if ok:
            log_success(f"[LIVE] [{i}/{len(tokens)}] {short} | User: {name}")
            live_tokens.append(token)
        else:
            log_warning(f"[DIE ] [{i}/{len(tokens)}] {short}")
            save_die_token(token)
            die_count += 1
    log_info(f"Ket qua: Live = {len(live_tokens)} | Die = {die_count}")
    return live_tokens


def get_channel_and_server_info(tokens, channel_id):
    for token in tokens:
        prof = BrowserProfile()
        try:
            session = curl_requests.Session(impersonate=prof.impersonate, verify=False)
            headers = prof.headers(token)
            response = session.get(
                f"{API_BASE}/channels/{channel_id}",
                headers=headers,
                timeout=15
            )
            if response.status_code == 200:
                channel_data = response.json()
                channel_name = channel_data.get("name", "Unknown Channel")
                guild_id = channel_data.get("guild_id")
                if not guild_id:
                    log_warning(f"Khong tim thay guild_id cho channel {channel_id}")
                    continue
                guild_response = session.get(
                    f"{API_BASE}/guilds/{guild_id}",
                    headers=headers,
                    timeout=15
                )
                if guild_response.status_code == 200:
                    guild_data = guild_response.json()
                    server_name = guild_data.get("name", "Unknown Server")
                    return channel_name, server_name
                else:
                    log_warning(f"Loi khi lay thong tin server cho guild_id {guild_id}: {guild_response.status_code}")
                    continue
            else:
                log_warning(f"Loi khi lay thong tin channel {channel_id}: {response.status_code}")
                continue
        except Exception as e:
            log_warning(f"Loi khi lay thong tin channel/server voi token {token[:6]}...{token[-6:]}: {str(e)}")
            continue
    return "Unknown Channel", "Unknown Server"


def get_user_input():
    clear_screen()
    log_info("Cau Hinh Spam...")

    while True:
        token_file = log_input("Nhap ten file token (vd: tokens.txt): ").strip()
        if not token_file:
            log_warning("Ten file khong duoc de trong!")
            continue
        if not os.path.exists(token_file):
            log_warning(f"File '{token_file}' khong ton tai! Thu lai.")
            continue
        break

    log_success(f"Load token tu: {token_file}")
    tokens = read_tokens(token_file)
    if not tokens:
        log_warning("Khong co token hop le trong file!")
        input("[EXIT] Nhan Enter de thoat...")
        exit(1)
    log_success(f"Tong so token: {len(tokens)}")
    tokens = check_live_all(tokens)
    if not tokens:
        log_warning("Tat ca token deu die! Khong con token nao de spam.")
        input("[EXIT] Nhan Enter de thoat...")
        exit(1)
    with open(token_file, "w", encoding="utf-8") as f:
        f.write("\n".join(tokens))
    log_success(f"Da cap nhat {len(tokens)} token live vao {token_file}")

    config = {
        "discord": {"channel_ids": [], "channel_info": {}},
        "delay": 1.0,
        "content_files": []
    }
    token_count = len(tokens)
    tokens_for_info = tokens

    log_info("Nhap ID Channel (nhap 'done' de dung):")
    while True:
        channel_id = log_input("Nhap ID Channel: ").strip()
        if channel_id.lower() == "done":
            if not config["discord"]["channel_ids"]:
                log_warning("Can it nhat 1 Channel!")
                continue
            break
        if channel_id.isdigit():
            config["discord"]["channel_ids"].append(channel_id)
            channel_name, server_name = get_channel_and_server_info(tokens_for_info, channel_id)
            config["discord"]["channel_info"][channel_id] = {"name": channel_name, "server": server_name}
            log_success(f"Them kenh: {channel_name} | Server: {server_name}")
        else:
            log_warning("ID kenh phai la so!")

    suggested_delay = token_count * 0.5
    log_info(f"Goi y delay: {suggested_delay:.1f} Vua {token_count} token)")
    default_delay = "1.0"
    log_info("Cau Hinh Delay:")
    while True:
        delay_input = log_input(f"Nhap Delay [Delay Mac Dinh: {default_delay}]: ") or default_delay
        try:
            delay = float(delay_input)
            if delay >= 0:
                config["delay"] = delay
                log_success(f"Delay: {delay}s")
                break
            log_warning("Delay phai >= 0!")
        except ValueError:
            log_warning("Delay phai la so!")

    log_info("Nhap danh sach file noi dung (nhap 'done' de dung):")
    while True:
        file_name = log_input("Nhap file noi dung: ").strip()
        if file_name.lower() == "done":
            if not config["content_files"]:
                log_warning("Can it nhat 1 file noi dung!")
                continue
            break
        if os.path.exists(file_name):
            config["content_files"].append(file_name)
            log_success(f"Them file: {file_name}")
        else:
            log_warning(f"File '{file_name}' khong ton tai!")

    config["tokens"] = tokens
    return config


def treo_datoken_thread(token_idx, all_tokens, channel_id, channel_info, contents, delay, interval):
    global sent_messages
    total_tokens = len(all_tokens)
    content_index = token_idx % len(contents)
    content = contents[content_index]
    token = all_tokens[token_idx % total_tokens]
    channel_name = channel_info.get("name", "Unknown Channel")
    server_name = channel_info.get("server", "Unknown Server")

    prof = BrowserProfile()
    session = curl_requests.Session(impersonate=prof.impersonate, verify=False)
    headers = prof.headers(token)

    time.sleep(token_idx * interval)

    while True:
        try:
            payload = {"content": content}
            response = session.post(
                f"{API_BASE}/channels/{channel_id}/messages",
                headers=headers,
                json=payload,
                timeout=15
            )
            if response.status_code == 429:
                try:
                    wait = float(response.json().get("retry_after", 5))
                except Exception:
                    wait = 5
                time.sleep(wait)
                continue
            if 200 <= response.status_code < 300:
                with lock:
                    sent_messages += 1
                    log_message(channel_id, channel_name, server_name, content, token)
            elif response.status_code in (401, 403):
                log_warning(f"Token {token[:6]}...{token[-6:]} bi die hoac khong co quyen!")
                save_die_token(token)
                return
            time.sleep(delay)
        except Exception:
            time.sleep(5)
            continue


def main():
    global start_time
    config = get_user_input()
    tokens = config["tokens"]
    contents = [open(f, "r", encoding="utf-8").read().strip() for f in config["content_files"] if os.path.exists(f)]
    if not contents:
        log_warning("Khong co file noi dung hop le!")
        input("[EXIT] Nhan Enter de thoat...")
        return
    total_tokens = len(tokens)
    delay = config["delay"]
    interval = delay / total_tokens if total_tokens > 1 else delay
    threads = []
    total_threads = 0
    clear_screen()
    start_time = time.time()
    for channel_id in config["discord"]["channel_ids"]:
        channel_info = config["discord"]["channel_info"].get(channel_id, {"name": "Unknown Channel", "server": "Unknown Server"})
        for i in range(len(tokens)):
            thread = threading.Thread(
                target=treo_datoken_thread,
                args=(i, tokens, channel_id, channel_info, contents, delay, interval),
                daemon=True
            )
            threads.append(thread)
            thread.start()
            total_threads += 1
    log_success(f"Dang Khoi Dong {total_threads} Luong...")
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()