import schedule
import time
import sqlite3
from plyer import notification
from datetime import datetime

DB_NAME = "assistant.db"

# ─────────────────────────────────────────────
# CHECK REMINDERS FROM DATABASE
# ─────────────────────────────────────────────
def check_reminders():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reminders WHERE is_done = 0")
        reminders = cursor.fetchall()
        conn.close()

        # Current time in multiple formats to match user input
        now = datetime.now()
        current_formats = [
            now.strftime("%I:%M %p").lstrip("0"),   # 3:00 PM
            now.strftime("%I %p").lstrip("0"),       # 3 PM
            now.strftime("%H:%M"),                   # 15:00
            now.strftime("%I:%M%p").lstrip("0"),     # 3:00PM
            now.strftime("%I%p").lstrip("0"),        # 3PM
        ]

        print(f"[{now.strftime('%H:%M:%S')}] Checking {len(reminders)} reminder(s)...")

        for r in reminders:
            remind_time = r[2]  # time column
            if remind_time:
                remind_time_clean = remind_time.strip().lower()
                for fmt in current_formats:
                    if remind_time_clean == fmt.lower():
                        # 🔔 Fire Windows notification!
                        notification.notify(
                            title=f"⏰ Reminder: {r[1]}",
                            message=f"📌 {r[1]}\n🕐 Time: {r[2]}\n📅 Date: {r[3] or 'Today'}",
                            app_name="AI Virtual Assistant",
                            timeout=10  # notification stays for 10 seconds
                        )
                        print(f"✅ Notified: {r[1]} at {r[2]}")

                        # Mark as done so it doesn't repeat
                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE reminders SET is_done = 1 WHERE id = ?", (r[0],))
                        conn.commit()
                        conn.close()
                        break

    except Exception as e:
        print(f"❌ Error checking reminders: {e}")


# ─────────────────────────────────────────────
# CHECK SCHEDULES FROM DATABASE
# ─────────────────────────────────────────────
def check_schedules():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM schedules WHERE is_notified = 0")
        schedules = cursor.fetchall()
        conn.close()

        now = datetime.now()
        current_formats = [
            now.strftime("%I:%M %p").lstrip("0"),
            now.strftime("%I %p").lstrip("0"),
            now.strftime("%H:%M"),
        ]

        print(f"[{now.strftime('%H:%M:%S')}] Checking {len(schedules)} event(s)...")

        for s in schedules:
            event_time = s[2]
            if event_time:
                event_time_clean = event_time.strip().lower()
                for fmt in current_formats:
                    if event_time_clean == fmt.lower():
                        # 🔔 Fire notification
                        notification.notify(
                            title=f"📅 Event Now: {s[1]}",
                            message=f"📌 {s[1]}\n🕐 Time: {s[2]}\n📅 Date: {s[3] or 'Today'}",
                            app_name="AI Virtual Assistant",
                            timeout=10
                        )
                        print(f"📅 Schedule notified: {s[1]} at {s[2]}")

                        # ✅ Mark as notified so it never fires again
                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE schedules SET is_notified = 1 WHERE id = ?", (s[0],)
                        )
                        conn.commit()
                        conn.close()
                        break

    except Exception as e:
        print(f"❌ Error checking schedules: {e}")


# ─────────────────────────────────────────────
# STARTUP NOTIFICATION
# ─────────────────────────────────────────────
def startup_notification():
    notification.notify(
        title="🤖 AI Virtual Assistant",
        message="✅ Reminder service is running!\nYou will be notified for your reminders.",
        app_name="AI Virtual Assistant",
        timeout=5
    )
    print("🤖 AI Virtual Assistant - Reminder Service Started!")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%I:%M %p')}")
    print("🔔 Checking reminders every 1 minute...")
    print("📅 Checking schedules every 1 minute...")
    print("=" * 50)
    print("✋ Keep this terminal open to receive notifications!")
    print("   Press Ctrl+C to stop.\n")


# ─────────────────────────────────────────────
# MAIN — SCHEDULE & RUN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    startup_notification()

    # Check every 1 minute
    schedule.every(1).minutes.do(check_reminders)
    schedule.every(1).minutes.do(check_schedules)

    # Also run once immediately at startup
    check_reminders()
    check_schedules()

    while True:
        schedule.run_pending()
        time.sleep(30)  # Sleep 30 seconds between checks