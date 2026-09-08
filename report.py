import os
import json
import requests
from datetime import datetime, timezone

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = os.getenv("ADMIN_ID")

DATA_FILE = "stats.json"


def telegram(method, data):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    response = requests.post(url, data=data, timeout=30)
    response.raise_for_status()
    result = response.json()

    if not result.get("ok"):
        raise RuntimeError(result)

    return result["result"]


def load_data():
    if not os.path.exists(DATA_FILE):
        return None

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN تنظیم نشده است.")

    if not CHANNEL_ID:
        raise RuntimeError("CHANNEL_ID تنظیم نشده است.")

    if not ADMIN_ID:
        raise RuntimeError("ADMIN_ID تنظیم نشده است.")

    now = datetime.now(timezone.utc)

    channel = telegram(
        "getChat",
        {"chat_id": CHANNEL_ID}
    )

    title = channel.get("title", "کانال")

    members = telegram(
        "getChatMemberCount",
        {"chat_id": CHANNEL_ID}
    )

    current_count = int(members)

    old = load_data()

    new_members = 0
    left_members = 0

    if old:
        previous_count = int(old.get("members", current_count))

        difference = current_count - previous_count

        if difference > 0:
            new_members = difference
        elif difference < 0:
            left_members = abs(difference)

    # آمار روزانه
    today = now.strftime("%Y-%m-%d")

    daily = {}
    weekly = {}
    monthly = {}

    if old:
        daily = old.get("daily", {})
        weekly = old.get("weekly", {})
        monthly = old.get("monthly", {})

    if today not in daily:
        daily[today] = 0

    daily[today] += new_members

    week_key = now.strftime("%Y-W%W")

    if week_key not in weekly:
        weekly[week_key] = 0

    weekly[week_key] += new_members

    month_key = now.strftime("%Y-%m")

    if month_key not in monthly:
        monthly[month_key] = 0

    monthly[month_key] += new_members

    save_data({
        "members": current_count,
        "last_update": now.isoformat(),
        "daily": daily,
        "weekly": weekly,
        "monthly": monthly
    })

    report = (
        f"📊 گزارش کانال\n\n"
        f"📢 {title}\n\n"
        f"👥 کل ممبر: {current_count:,}\n\n"
        f"🟢 عضو جدید: +{new_members}\n"
        f"🔴 خارج شده: -{left_members}\n"
        f"📈 رشد خالص: {new_members - left_members:+d}\n\n"
        f"📅 امروز: +{daily[today]}\n"
        f"📆 این هفته: +{weekly[week_key]}\n"
        f"🗓 این ماه: +{monthly[month_key]}\n\n"
        f"⏰ گزارش بعدی: ۱ ساعت دیگر"
    )

    telegram(
        "sendMessage",
        {
            "chat_id": ADMIN_ID,
            "text": report
        }
    )

    print("✅ Report sent successfully.")


if __name__ == "__main__":
    main()
