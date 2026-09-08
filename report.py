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
        return {
            "last_members": None,
            "daily": {},
            "weekly": {},
            "monthly": {}
        }

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN تنظیم نشده است.")

    if not CHANNEL_ID:
        raise RuntimeError("CHANNEL_ID تنظیم نشده است.")

    if not ADMIN_ID:
        raise RuntimeError("ADMIN_ID تنظیم نشده است.")

    now = datetime.now(timezone.utc)
    data = load_data()

    channel = telegram(
        "getChat",
        {"chat_id": CHANNEL_ID}
    )

    channel_name = channel.get("title", "کانال")

    current_members = int(
        telegram(
            "getChatMemberCount",
            {"chat_id": CHANNEL_ID}
        )
    )

    previous_members = data.get("last_members")

    growth = 0

    if previous_members is not None:
        growth = current_members - int(previous_members)

    new_members = max(growth, 0)
    left_members = max(-growth, 0)

    day_key = now.strftime("%Y-%m-%d")
    week_key = now.strftime("%Y-W%W")
    month_key = now.strftime("%Y-%m")

    daily = data.setdefault("daily", {})
    weekly = data.setdefault("weekly", {})
    monthly = data.setdefault("monthly", {})

    daily.setdefault(day_key, {"new": 0, "left": 0})
    weekly.setdefault(week_key, {"new": 0, "left": 0})
    monthly.setdefault(month_key, {"new": 0, "left": 0})

    daily[day_key]["new"] += new_members
    daily[day_key]["left"] += left_members

    weekly[week_key]["new"] += new_members
    weekly[week_key]["left"] += left_members

    monthly[month_key]["new"] += new_members
    monthly[month_key]["left"] += left_members

    data["last_members"] = current_members
    data["last_update"] = now.isoformat()

    save_data(data)

    today_new = daily[day_key]["new"]
    today_left = daily[day_key]["left"]

    week_new = weekly[week_key]["new"]
    week_left = weekly[week_key]["left"]

    month_new = monthly[month_key]["new"]
    month_left = monthly[month_key]["left"]

    report = (
        f"🤖 گزارش هوشمند کانال\n\n"
        f"📢 {channel_name}\n\n"
        f"👥 اعضای فعلی: {current_members:,}\n\n"
        f"🟢 عضو جدید این ساعت: +{new_members}\n"
        f"🔴 خارج شده این ساعت: -{left_members}\n"
        f"📈 رشد خالص: {growth:+d}\n\n"
        f"📅 امروز\n"
        f"🟢 ورود: +{today_new}\n"
        f"🔴 خروج: -{today_left}\n"
        f"📈 رشد: {today_new - today_left:+d}\n\n"
        f"📆 این هفته\n"
        f"🟢 ورود: +{week_new}\n"
        f"🔴 خروج: -{week_left}\n"
        f"📈 رشد: {week_new - week_left:+d}\n\n"
        f"🗓 این ماه\n"
        f"🟢 ورود: +{month_new}\n"
        f"🔴 خروج: -{month_left}\n"
        f"📈 رشد: {month_new - month_left:+d}\n\n"
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
