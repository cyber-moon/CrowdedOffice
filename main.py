from __future__ import print_function

import datetime
import os.path

import matplotlib.pyplot as plt
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
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

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Calendar ID's
        calender_ids = {
            'ElGouna': 'c_188ar585ebl7ui6ln4tvulcjjhv0s@resource.calendar.google.com',
            'Malaga': 'c_188d7slmj3sc2jbplcmev2hidrmqu@resource.calendar.google.com',
            'Belek': 'ipt.ch_33363733393132373131@resource.calendar.google.com',
            'Marrakesch': 'ipt.ch_3731323233333736323633@resource.calendar.google.com',
            'Valencia': 'ipt.ch_383239323032343934@resource.calendar.google.com'
        }

        # create list containing an entry for each day within the next 14 days
        next14days_dates = [datetime.date.today() + datetime.timedelta(days=x) for x in range(14)]
        next14days_count = [0] * 14
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        upcoming_event_dates = []
        for key, value in calender_ids.items():
            print(key, value)
            events_result = service.events().list(calendarId=value, timeMin=now, timeMax=(datetime.datetime.utcnow()+datetime.timedelta(days=14)).isoformat()+'Z',
                                                  singleEvents=True,
                                                  orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')
                return

            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                upcoming_event_dates.append(start)
                # Get the timedelta from now to the event, respecting the timezone offset
                timedelta = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z') - datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
                if 0 <= timedelta.days < 14:
                    next14days_count[timedelta.days-1] += 1
                print(timedelta.days, start, event['summary'])

        next14days = zip(next14days_dates, next14days_count)
        print(next14days)

        # Bar plot the next14 days, labeling the bars with its date
        df = pd.DataFrame(next14days, columns=['date', 'count'])
        df.plot(kind='bar', figsize=(20, 10), x='date', y='count')
        plt.show()

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
