from database import add_schedule, get_all_schedules, delete_schedule

# ─────────────────────────────────────────────
# SCHEDULE RESPONSES
# ─────────────────────────────────────────────
def handle_add_schedule(entities: dict) -> str:
    title = entities.get("title") or "Unnamed Event"
    time = entities.get("time") or "Not specified"
    date = entities.get("date") or "Today"

    success = add_schedule(title, time, date)
    if success:
        return (
            f"✅ **Event Scheduled!**\n\n"
            f"📌 **Event:** {title}\n"
            f"🕐 **Time:** {time}\n"
            f"📅 **Date:** {date}"
        )
    return "❌ Failed to schedule event. Please try again."


def handle_view_schedule() -> str:
    schedules = get_all_schedules()
    if not schedules:
        return "📭 No scheduled events. Try saying: *'Schedule a meeting at 3 PM tomorrow'*"

    result = "📅 **Your Schedule:**\n\n"
    for s in schedules:
        result += (
            f"📌 **ID #{s[0]}** — {s[1]}\n"
            f"   🕐 Time: {s[2] or 'N/A'} | 📅 Date: {s[3] or 'N/A'}\n\n"
        )
    return result


def handle_delete_schedule(schedule_id: int) -> str:
    success = delete_schedule(schedule_id)
    if success:
        return f"🗑️ Event #{schedule_id} deleted successfully."
    return f"❌ Could not find Event #{schedule_id}."