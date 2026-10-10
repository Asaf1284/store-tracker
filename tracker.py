import os
import json
import requests

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

try:
    with open("items.json", "r") as f:
        TARGET_ITEMS = json.load(f)
except Exception as e:
    print(f"[-] Error loading items.json: {e}")
    TARGET_ITEMS = []

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def notify_discord(item_name, url):
    if not DISCORD_WEBHOOK_URL:
        print("[-] Discord Webhook URL is missing!")
        return
        
    payload = {
        "embeds": [{
            "title": "🚨 ITEM RESTOCKED!",
            "description": f"**{item_name}** appears to be back in stock!",
            "url": url,
            "color": 5814783
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"[-] Failed to send Discord alert: {e}")

def check_stock():
    if not TARGET_ITEMS:
        print("[*] No items to track.")
        return

    for item in TARGET_ITEMS:
        name = item.get("name")
        url = item.get("url")
        out_of_stock_text = item.get("out_of_stock_text", "").lower()

        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code == 200:
                html = res.text.lower()

                # Anti-bot / CAPTCHA guard for Walmart
                if "robot or human" in html or "blocked" in html:
                    print(f"[-] Blocked by anti-bot page on {name}, skipping.")
                    continue

                # If out-of-stock phrase is gone, trigger restock alert
                if out_of_stock_text not in html:
                    print(f"[!] {name} IS IN STOCK!")
                    notify_discord(name, url)
                else:
                    print(f"[*] {name} still out of stock.")
            else:
                print(f"[-] Status code {res.status_code} for {name}")
        except Exception as e:
            print(f"[-] Error checking {name}: {e}")

if __name__ == "__main__":
    check_stock()
