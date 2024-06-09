#!/usr/bin/python3

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import os
from xml.etree import ElementTree
from datetime import datetime, timedelta
from config import OUT_FILE_NAME, START_DATE, END_DATE

SENDER = "RaiffeisenOnline@raiffeisenbank.rs"
start_date = None
end_date = None
out_file_name = None

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
service = None
creds = None
file_header = None


def parse_xml(binary_data):
    """
    Extracts data from XML and converts into dictionary
    :param binary_data:
    :return: dict
    """
    dict_data = {}

    root = ElementTree.fromstring(binary_data)
    for child in root:
        if child.tag == "Zaglavlje":
            dict_data[child.tag] = child.attrib
        elif child.tag == "Stavke":
            if child.tag not in dict_data:
                dict_data[child.tag] = [child.attrib]
            else:
                xml_data = dict_data[child.tag]
                dict_data[child.tag].append(child.attrib)

    return dict_data


def get_mail_attachment(mail_id):
    """
    Checks if there is attachment and if it is XML file type, extracts data
    :param mail_id:
    :return: data contained in XML if any.
    """
    attachment_data = None
    msg_date = None

    try:
        message = service.users().messages().get(userId="me", id=mail_id).execute()
        # Set message date
        timestamp = int(message["internalDate"])//1000
        msg_date = datetime.fromtimestamp(timestamp)

        # Process attachment
        for part in message['payload']['parts']:
            if part['filename']:
                file_extension = part['filename'][-3:].upper()
                if file_extension == "XML":

                    if 'data' in part['body']:
                        data = part['body']['data']
                    else:
                        att_id = part['body']['attachmentId']
                        att = service.users().messages().attachments().get(
                            userId="me", messageId=mail_id, id=att_id).execute()
                        data = att['data']
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                    attachment_data = parse_xml(file_data)

    except HttpError as error:
        print(f"ERROR retrieving email ID: {mail_id}.\n\t{error}")

    return msg_date, attachment_data


def list_mail(page_token=None):
    """
    Lists all email messages from configured sender
    :param page_token:
    :return:
    """
    global service
    global creds

    next_page_token = None
    msg_id_list = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", q=f"from:{SENDER}", pageToken=page_token, maxResults=10).execute()
        msg_id_list = results.get("messages", [])
        next_page_token = results.get("nextPageToken", [])

    except HttpError as error:
        print(f"ERROR listing emails from {SENDER}:\n\t{error}")

    return msg_id_list, next_page_token


def shape_data(data_dict, file_name):
    """
    The data is expected in a specific dictionary with keys "Zaglavlje" and "Stavke".
    The data in "Zaglavlje" that we need is "BrojIzvoda", "DatumIzvoda", "KomitentNaziv" and "Partija".
    This data needs to be appended to every item in list under key "Stavke".
    :param data_dict:
    :return: Saves data to a CSV file
    """
    global file_header

    out_file = open(file_name, "a")
    try:
        header_data = data_dict["Zaglavlje"]
        for data_item in data_dict["Stavke"]:
            data_item["BrojIzvoda"] = header_data["BrojIzvoda"]
            data_item["DatumIzvoda"] = header_data["DatumIzvoda"]
            data_item["KomitentNaziv"] = header_data["KomitentNaziv"]
            data_item["Partija"] = header_data["Partija"]

            if not file_header:
                header_row = ""
                file_header = []
                for key in data_item.keys():
                    file_header.append(key)

                file_header = sorted(file_header)

                for key in file_header:
                    if not header_row:
                        header_row = f'"{key}"'
                    else:
                        header_row = f'{header_row},"{key}"'

                header_row = f"{header_row},\n"

                out_file.write(header_row)

            data_row = None
            for key in file_header:
                if not data_row:
                    data_row = f'"{data_item[key]}"'
                else:
                    data_row = f'{data_row},"{data_item[key]}"'

            data_row = f"{data_row},\n"

            out_file.write(data_row)

    except Exception as e:
        print(f"ERROR parsing data: {data_dict}", e)

    finally:
        out_file.close()


def init_cfg():
    global start_date
    global end_date
    global out_file_name

    try:
        start_date = datetime.strptime(START_DATE, '%d.%m.%Y')
        end_date = datetime.strptime(END_DATE, '%d.%m.%Y')

        if start_date < end_date:
            temp = end_date
            end_date = start_date
            start_date = temp

        out_file_name = f"{OUT_FILE_NAME}_{end_date.strftime('%d.%m.%Y')}_{start_date.strftime('%d.%m.%Y')}.csv"
        print(out_file_name)
        file = open(out_file_name, "w")
        file.close()

    except Exception as e:
        print("ERROR in configuration:", e)
        exit()


if __name__ == "__main__":
    init_cfg()

    message_date = start_date
    next_page_id = None

    while message_date > end_date:
        message_id_list, next_page_id = list_mail(page_token=next_page_id)

        for item in message_id_list:
            message_date, data = get_mail_attachment(item["id"])
            if data:
                print(f"Processed email from date {message_date}")
                shape_data(data, out_file_name)

    input("\nPress Enter to continue...")
