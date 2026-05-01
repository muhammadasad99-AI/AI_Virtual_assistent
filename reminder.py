from database import add_reminder, get_all_reminders, delete_reminder, mark_reminder_done

# ─────────────────────────────────────────────
# REMINDER RESPONSES
# ─────────────────────────────────────────────
def handle_set_reminder(entities: dict) -> str:
    title = entities.get("title") or "Unnamed Reminder"
    time = entities.get("time") or "Not specified"
    date = entities.get("date") or "Today"

    success = add_reminder(title, time, date)
    if success:
        return (
            f"✅ **Reminder Set!**\n\n"
            f"📌 **Task:** {title}\n"
            f"🕐 **Time:** {time}\n"
            f"📅 **Date:** {date}"
        )
    return "❌ Failed to set reminder. Please try again."


def handle_view_reminders() -> str:
    reminders = get_all_reminders()
    if not reminders:
        return "📭 No reminders found. Try saying: *'Remind me to call John at 5 PM'*"

    result = "📋 **Your Reminders:**\n\n"
    for r in reminders:
        result += (
            f"🔔 **ID #{r[0]}** — {r[1]}\n"
            f"   🕐 Time: {r[2] or 'N/A'} | 📅 Date: {r[3] or 'N/A'}\n\n"
        )
    return result


def handle_delete_reminder(reminder_id: int) -> str:
    success = delete_reminder(reminder_id)
    if success:
        return f"🗑️ Reminder #{reminder_id} deleted successfully."
    return f"❌ Could not find Reminder #{reminder_id}."