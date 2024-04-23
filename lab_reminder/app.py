import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from linebot import LineBotApi
from linebot.models import TextSendMessage

# Set up Google Calendar API credentials
credentials = service_account.Credentials.from_service_account_file(
    'path/to/your/credentials.json',
    scopes=['https://www.googleapis.com/auth/calendar.readonly']
)

# Set up LINE API credentials
line_token = 'your_line_token'
line_bot_api = LineBotApi(line_token)

# Set up Google Calendar API service
service = build('calendar', 'v3', credentials=credentials)

# Get the list of events from the primary calendar
now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
events_result = service.events().list(calendarId='primary', timeMin=now).execute()
events = events_result.get('items', [])

# Check each event for a deadline and send a LINE notification if found
for event in events:
    if 'deadline' in event['summary'].lower():
        message = f"Deadline: {event['summary']}"
        line_bot_api.push_message('your_line_user_id', TextSendMessage(text=message))