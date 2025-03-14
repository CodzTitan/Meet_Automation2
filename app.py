from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import datetime
import re

app = Flask(__name__)

# Load credentials for Google Calendar API
creds = Credentials.from_authorized_user_file("token.json")
service = build("calendar", "v3", credentials=creds)

def schedule_meeting(date, time, duration):
    start_time = datetime.datetime.strptime(f"{date} {time}", "%d/%m/%Y %I:%M%p")
    end_time = start_time + datetime.timedelta(hours=int(duration[0]))
    
    event = {
        "summary": "Scheduled Meeting",
        "start": {"dateTime": start_time.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_time.isoformat(), "timeZone": "UTC"},
        "conferenceData": {"createRequest": {"conferenceSolutionKey": {"type": "hangoutsMeet"}, "requestId": "meet123"}}
    }
    
    event = service.events().insert(calendarId="primary", body=event, conferenceDataVersion=1).execute()
    return event['hangoutLink']

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip()
    response = MessagingResponse()
    msg = response.message()
    
    pattern = r"Schedule a meeting on (\d{2}/\d{2}/\d{4}) at (\d{1,2}:\d{2}[APM]{2}) for (\d+)hour"
    match = re.search(pattern, incoming_msg)
    
    if match:
        date, time, duration = match.groups()
        meet_link = schedule_meeting(date, time, duration)
        msg.body(f"Your meeting has been scheduled:\nOn: {date}\nAt: {time}\nFor: {duration} hour(s)\nHere's the Link for the meeting:\n{meet_link}")
    else:
        msg.body("Invalid format. Please use: Schedule a meeting on <dd/mm/yyyy> at <time> for <duration>.")
    
    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
