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

    response = requests.post(
        url,
        data=data,
        timeout=30
    )

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

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )


def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN تنظیم نشده است."
        )

    if not CHANNEL_ID:
        raise RuntimeError(
            "CHANNEL_ID تنظیم نشده است."
        )

    if not ADMIN_ID:
        raise RuntimeError(
            "ADMIN_ID تنظیم نشده است."
        )

    now = datetime.now(timezone.utc)

    data = load_data()

    # -------------------------
    # اطلاعات کانال
    # -------------------------

    channel = telegram(
        "getChat",
        {
            "chat_id": CHANNEL_ID
        }
    )

    channel_name = channel.get(
        "title",
        "کانال"
    )

    # -------------------------
    # تعداد اعضا
    # -------------------------

    current_members = int(
        telegram(
            "getChatMemberCount",
            {
                "chat_id": CHANNEL_ID
            }
        )
    )

    previous_members = data.get(
        "last_members"
    )

    # -------------------------
    # محاسبه رشد
    # -------------------------

    growth = 0

    if previous_members is not None:
        growth = (
            current_members
            - int(previous_members)
        )

    new_members = max(
        growth,
        0
    )

    left_members = max(
        -growth,
        0
    )

    # -------------------------
    # تاریخ‌ها
    # -------------------------

    day_key = now.strftime(
        "%Y-%m-%d"
    )

    week_key = now.strftime(
        "%Y-W%W"
    )

    month_key = now.strftime(
        "%Y-%m"
    )

    daily = data.setdefault(
        "daily",
        {}
    )

    weekly = data.setdefault(
        "weekly",
        {}
    )

    monthly = data.setdefault(
        "monthly",
        {}
    )

    # -------------------------
    # آمار روزانه
    # -------------------------

    if day_key not in daily:

        daily[day_key] = {
            "new": 0,
            "left": 0
        }

    daily[day_key]["new"] += new_members

    daily[day_key]["left"] += left_members

    # -------------------------
    # آمار هفتگی
    # -------------------------

    if week_key not in weekly:

        weekly[week_key] = {
            "new": 0,
            "left": 0
        }

    weekly[week_key]["new"] += new_members

    weekly[week_key]["left"] += left_members

    # -------------------------
    # آمار ماهانه
    # -------------------------

    if month_key not in monthly:

        monthly[month_key] = {
            "new": 0,
            "left": 0
        }

    monthly[month_key]["new"] += new_members

    monthly[month_key]["left"] += left_members

    # -------------------------
    # ذخیره
    # -------------------------

    data["last_members"] = current_members

    data["last_update"] = now.isoformat()

    save_data(data)

    # -------------------------
    # وضعیت کانال
    # -------------------------

    if growth >= 20:

        status = "🟢 رشد عالی"

    elif growth > 0:

        status = "🟢 رشد مثبت"

    elif growth == 0:

        status = "🟡 بدون تغییر"

    else:

        status = "🔴 کاهش اعضا"

    # -------------------------
    # گزارش
    # -------------------------

    today_new = daily[day_key]["new"]

    today_left = daily[day_key]["left"]

    today_growth = (
        today_new
        - today_left
    )

    week_new = weekly[week_key]["new"]

    week_left = weekly[week_key]["left"]

    week_growth = (
        week_new
        - week_left
    )

    month_new = monthly[month_key]["new"]

    month_left = monthly[month_key]["left"]

    month_growth = (
        month_new
        - month_left
    )

    report = f"""
🤖 گزارش هوشمند کانال

📢 {channel_name}

━━━━━━━━━━━━━━

👥 اعضای فعلی:
{current_members:,}

🟢 عضو جدید این ساعت:
+{new_members}

🔴 خارج شده این ساعت:
-{left_members}

📈 رشد خالص:
{growth:+d}

━━━━━━━━━━━━━━

📅 امروز

🟢 ورود: +{today_new}
🔴 خروج: -{today_left}
📈 رشد: {today_growth:+d}

━━━━━━━━━━━━━━

📆 این هفته

🟢 ورود: +{week_new}
🔴 خروج: -{week_left}
📈 رشد: {week_growth:+d}

━━━━━━━━━━━━━━

🗓 این ماه

🟢 ورود: +{month_new}
🔴 خروج: -{month_left}
📈 رشد: {month_growth:+d}

━━━━━━━━━━━━━━

🚦 وضعیت:
{status}

⏰ گزارش بعدی: ۱ ساعت دیگر
"""

    # -------------------------
    # ارسال تلگرام
    # -------------------------

    telegram(
        "sendMessage",
        {
            "chat_id": ADMIN_ID,
            "text": report.strip()
        }
    )

    print(
        "✅ Report sent successfully."
    )


if __name__ == "__main__":
    main()
