import os, json, smtplib, requests
from email.mime.text import MIMEText

URL = "https://11six24.com/products/ultre-power-2.js"
VARIANT_ID = 58768903274799
PRODUCT_LINK = f"https://11six24.com/products/ultre-power-2?variant={VARIANT_ID}"
STATE_FILE = "state.json"

def is_available():
    r = requests.get(URL, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    for v in r.json()["variants"]:
        if v["id"] == VARIANT_ID:
            return v["available"], v["title"]
    raise RuntimeError("找不到該 variant，可能商品已改版")

def notify_line(msg):
    requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={"Authorization": f"Bearer {os.environ['LINE_TOKEN']}"},
        json={"to": os.environ["LINE_USER_ID"],
              "messages": [{"type": "text", "text": msg}]},
        timeout=15,
    ).raise_for_status()

def notify_email(msg):
    m = MIMEText(msg)
    m["Subject"] = "🔔 Cosmic Grape 有貨了！"
    m["From"] = os.environ["MAIL_USER"]
    m["To"] = os.environ["MAIL_TO"]
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(os.environ["MAIL_USER"], os.environ["MAIL_APP_PASSWORD"])
        s.send_message(m)

def main():
    available, title = is_available()
    prev = False
    if os.path.exists(STATE_FILE):
        prev = json.load(open(STATE_FILE)).get("available", False)

    print("MAIL_USER set:", bool(os.environ.get("MAIL_USER")),
      "| LINE_TOKEN set:", bool(os.environ.get("LINE_TOKEN")))
    
    if True:
    #if available and not prev:  # 只在狀態轉變時通知
        msg = f"✅ {title} 有庫存了，快下單！\n{PRODUCT_LINK}"
        if os.environ.get("LINE_TOKEN"): notify_line(msg)
        if os.environ.get("MAIL_USER"): notify_email(msg)

    json.dump({"available": available}, open(STATE_FILE, "w"))
    print("available =", available)

if __name__ == "__main__":
    main()
