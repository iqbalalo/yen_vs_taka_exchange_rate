from apiclient.discovery import build
from googleapiclient import errors
from oauth2client import file, client, tools
from httplib2 import Http
import json
import base64
from datetime import datetime
import re

CLIENTSECRETS_LOCATION = 'client_secrets.json'
REDIRECT_URI = 'http://iqbalhossain.info/research/oauth2callback'
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

store = file.Storage('token.json')
creds = store.get()

if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('gmail', 'v1', http=creds.authorize(Http()))

user_id = 'me'
inbox = 'INBOX'

# results = service.users().labels().list(userId=user_id).execute()
results = service.users().messages().list(userId=user_id, labelIds=[inbox]).execute()
query = "from:bangla@kyodai.co.jp"


def list_messages(service, user_id, query=''):
    try:
        response = service.users().messages().list(userId=user_id,
                                                   q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages

    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return 400


def get_message_data(service, user_id, msg_id):
    try:
        msg = {}
        response = service.users().messages().get(userId=user_id, id=msg_id, format="full").execute()
        msg_payload = response['payload']
        for i in msg_payload["headers"]:
            if i['name'] == 'Date':
                d = datetime.strptime(i['value'], "%a, %d %b %Y %H:%M:%S %z")
                msg['date'] = str(d.year) + "-" + str(d.month) + "-" + str(d.day)

        content = base64.urlsafe_b64decode(msg_payload["body"]['data']).decode('utf-8')
        content = re.search(r'\d{1,2}\.\d{1,4}', content)

        if content is not None:
            content = content.group(0)
        else:
            content = None

        msg['rate'] = content

        return msg
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return 400


def extract_data_from_email_and_save_to_csv():
    msg_list = list_messages(service, user_id, query)
    j = 0
    data = []

    for i in msg_list:
        j += 1
        print(str(j) + " extracted " + str(i))

        msg = get_message_data(service, user_id, i['id'])

        if msg['rate'] is not None:
            data.append(msg)

    file = open('remittance-rate.json', "w")
    file.write(json.dumps(data))
    file.close()

    print("File saved")


extract_data_from_email_and_save_to_csv()
