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

    # Get all users in the domain | DRAFT CODE: Doesn't work yet. Probably, because I don't have the right permissions to access google's Admin SDK API.
    # SCOPES_SERVICE_ACCOUNT = ['https://www.googleapis.com/auth/admin.directory.user']
    # SERVICE_ACCOUNT_FILE = 'sze-hack-ipt-room-calendars.json'
    #
    # credentials = service_account.Credentials.from_service_account_file(
    #     SERVICE_ACCOUNT_FILE, scopes=SCOPES_SERVICE_ACCOUNT)
    #
    # # Make a GET request to retrieve a list of all users in your domain
    # directory_service = build('admin', 'directory_v1', credentials=credentials)
    # user_list = directory_service.users().list(domain='ipt.ch').execute()
    # # Instead, could also be used:   user_list = directory_service.groups().get(...).execute()
    #
    # # Print each user's primary email address and name.
    # for user in user_list['users']:
    #     print(u'{0} ({1})'.format(user['primaryEmail'],
    #                               user['name']['fullName']))


    # Prepared observed timeperiod and calendars
    period_start = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    period_end = (datetime.datetime.utcnow() + datetime.timedelta(days=14)).isoformat() + 'Z'
    calender_ids = {
        'Stephan Zehnder': 'stephan.zehnder@ipt.ch',
        'Sarah Moy de Vitry': 'sarah.moydevitry@ipt.ch',
    }

    try:
        service = build('calendar', 'v3', credentials=creds)

        for key, value in calender_ids.items():
            print(f"*** {key}'s events ({value}): ***")

            # Get events for the given mail address
            events_result = service.events().list(calendarId=value, timeMin=period_start, timeMax=period_end,
                                                  singleEvents=True, orderBy='startTime')\
                                            .execute()
            events = events_result.get('items', [])

            # Print events
            if not events:
                print('No upcoming events found.')
                continue
            for event in events:
                start = datetime.datetime.strptime(event['start'].get('dateTime'), '%Y-%m-%dT%H:%M:%S%z')
                end = datetime.datetime.strptime(event['end'].get('dateTime'), '%Y-%m-%dT%H:%M:%S%z')
                event_type = event['eventType'] if 'eventType' in event else '[No eventType]'
                event_summary = event['summary'] if 'summary' in event else '[No event description]'
                print(f"{start} (Duration: {end - start}, EventType: {event_type}): {event_summary}")

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
