from __future__ import print_function

import datetime
import os.path

import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Prepared observed timeperiod and calendars
    period_start = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    period_end = (datetime.datetime.utcnow() + datetime.timedelta(days=14)).isoformat() + 'Z'
    # start of next month
    # get the current date
    current_date = datetime.datetime.utcnow()

    # get the first day of next month
    next_month = current_date.replace(day=1) + datetime.timedelta(days=32)
    first_day_next_month = next_month.replace(day=1)
    overnext_month = first_day_next_month + datetime.timedelta(days=32)
    last_day_next_month = overnext_month.replace(day=1) - datetime.timedelta(days=1)


    # format the first day of next month as an ISO formatted date
    period_start = first_day_next_month.isoformat() + 'Z'
    period_end = last_day_next_month.isoformat() + 'Z'

    print(f"*** Events from {period_start} to {period_end} ***")

    with (open('calender_ids.csv')) as f:
        calender_ids = f.read().splitlines()

    # calender_ids = ['stephan.zehnder@ipt.ch', 'sarah.moydevitry@ipt.ch']

    df_out_of_office = pd.DataFrame(columns=['email', 'start', 'duration', 'eventType', 'summary'])

    try:
        service = build('calendar', 'v3', credentials=creds)

        for email in calender_ids:
            print(f"*** {email}'s events: ***")

            # Get events for the given mail address
            events_result = service.events().list(calendarId=email, timeMin=period_start, timeMax=period_end,
                                                  singleEvents=True, orderBy='startTime')\
                                            .execute()
            events = events_result.get('items', [])

            # Print events
            if not events:
                print('No upcoming events found.')
                continue
            for event in events:
                if 'start' not in event or 'end' not in event or 'eventType' not in event or 'summary' not in event:
                    continue
                start, end = None, None
                if 'dateTime' in event['start'] or 'dateTime' in event['end']:
                    start = datetime.datetime.strptime(event['start'].get('dateTime'), '%Y-%m-%dT%H:%M:%S%z')
                    end = datetime.datetime.strptime(event['end'].get('dateTime'), '%Y-%m-%dT%H:%M:%S%z')
                else:
                    start = datetime.datetime.strptime(event['start'].get('date'), '%Y-%m-%d')
                    end = datetime.datetime.strptime(event['end'].get('date'), '%Y-%m-%d')
                event_type = event['eventType'] if 'eventType' in event else '[No eventType]'
                if event_type == "outOfOffice":
                    event_summary = event['summary'] if 'summary' in event else '[No event description]'
                    df_out_of_office = pd.concat([df_out_of_office, pd.DataFrame({'email': email, 'start': start, 'duration': end-start, 'eventType': event_type, 'summary': event_summary}, index=[0])])

    except HttpError as error:
        print('An error occurred: %s' % error)

    # Print out of office events
    print(f"*** Out of office events from {period_start} to {period_end} ***")
    pd.options.display.max_rows = 100
    pd.options.display.max_columns = 10
    print(df_out_of_office)

    df_out_of_office.to_csv('out_of_office.csv', index=False, sep='\t')


if __name__ == '__main__':
    main()
