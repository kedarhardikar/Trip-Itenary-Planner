from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import re

def create_calendar_events(state: dict) -> dict:
    print("📅 Adding itinerary to calendar")

    itinerary = state.get("final_itenary", "")
    start_date = state.get("trip_start_date", "")
    
    if not itinerary or not start_date:
        print("⚠️ Missing itinerary or start date.")
        state["calendar_success"] = False
        return state

    try:
        # ✅ Extract only actual "Day X" chunks, ignore intro text
        day_chunks = re.split(r"(?=Day \d+:)", itinerary.strip())
        day_chunks = [chunk.strip() for chunk in day_chunks if re.match(r"^Day \d+:", chunk.strip())]

        if not day_chunks:
            print("⚠️ No valid day-wise itinerary chunks found.")
            state["calendar_success"] = False
            return state

        # 🔐 Authenticate with Google Calendar
        creds = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', ['https://www.googleapis.com/auth/calendar']
        ).run_local_server(port=8000)
        service = build('calendar', 'v3', credentials=creds)

        base_date = datetime.strptime(start_date, "%Y-%m-%d")

        for i, day_plan in enumerate(day_chunks):
            event_date = base_date + timedelta(days=i)

            # 🧹 Extract header and POIs
            lines = re.split(r"\n|- ", day_plan)
            lines = [line.strip() for line in lines if line.strip()]

            header = lines[0] if lines else f"Day {i+1}"
            poi_lines = "\n".join(lines[1:]) if len(lines) > 1 else "No POIs listed."

            # 📅 Create event payload
            event = {
                'summary': header,
                'description': poi_lines,
                'start': {
                    'dateTime': f"{event_date.strftime('%Y-%m-%d')}T09:00:00",
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': f"{event_date.strftime('%Y-%m-%d')}T21:00:00",
                    'timeZone': 'Asia/Kolkata',
                },
            }

            # 🚀 Push to calendar
            created_event = service.events().insert(calendarId='primary', body=event).execute()
            print(f"✅ Created event: {created_event.get('htmlLink')}")

        state["calendar_success"] = True

    except Exception as e:
        print(f"❌ Calendar error: {e}")
        state["calendar_success"] = False

    return state
