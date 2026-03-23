from imapclient import IMAPClient
from email import message_from_bytes
import pandas as pd
import re
from datetime import datetime
from bs4 import BeautifulSoup
from io import StringIO
import os

HOST = "imap.gmail.com"
#USERNAME = "ch.ankurjawla@gmail.com"
#PASSWORD = "lupx encd vahn kqym"
LABEL = "Allotment"
file_name = 'equity_allotment.csv'

# Redefine fetch_and_extract_tables with label removal functionality
def fetch_and_extract_tables(host, username, password, label):
    extracted_data = []
    try:
        with IMAPClient(host) as client:
            client.login(username, password)
            client.select_folder(label)
            messages = client.search('ALL')

            for msg_id in messages:
                raw_message = client.fetch(msg_id, ['RFC822'])
                email_message = message_from_bytes(raw_message[msg_id][b'RFC822'])

                email_subject = email_message['Subject'] if 'Subject' in email_message else 'No Subject'

                html_content = None
                for part in email_message.walk():
                    if part.get_content_type() == 'text/html':
                        charset = part.get_content_charset()
                        html_content = part.get_payload(decode=True).decode(charset or 'utf-8', errors='replace')
                        break

                if html_content:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    tables = soup.find_all('table')

                    email_dataframes = []
                    for table_idx, table in enumerate(tables):
                        try:
                            dfs = pd.read_html(StringIO(str(table)))
                            if dfs:
                                for df in dfs:
                                    email_dataframes.append(df)
                        except Exception as e:
                            print(f"Warning: Could not parse table {table_idx} from email (Subject: '{email_subject}'): {e}")

                    if email_dataframes:
                        extracted_data.append({
                            'email_subject': email_subject,
                            'dataframes': email_dataframes
                        })
                        # --- Add label removal here ---
                        try:
                            # IMAPClient uses flags for labels. A custom label is a flag.
                            client.remove_flags(msg_id, [label], silent=True)
                            print(f"Removed label '{label}' from email (Subject: '{email_subject}', ID: {msg_id})")
                        except Exception as e:
                            print(f"Error removing label from email (Subject: '{email_subject}', ID: {msg_id}): {e}")

                else:
                    print(f"Info: No HTML content found in email (Subject: '{email_subject}')")

    except Exception as e:
        print(f"An error occurred during email fetching or processing: {e}")

    return extracted_data

def extract_table(USERNAME,PASSWORD):
    extracted_tables_data = fetch_and_extract_tables(HOST, USERNAME, PASSWORD, LABEL)

    df_allotment = extracted_tables_data[0]['dataframes'][0]

    pattern = r'([₹$]?[\d,]+\.?\d*)\s*(.*)'

    df_allotment[['Amount_str', 'unit']] = df_allotment['Amount'].astype(str).str.extract(pattern)

    df_allotment['Amount'] = df_allotment['Amount_str'].str.replace(r'[₹$]', '', regex=True).str.replace(',', '').astype(float)
    df_allotment['unit'] = df_allotment['unit'].str.replace(' units', '', regex=False).astype(float)
    # Drop the intermediate 'Amount_str' column
    df_allotment = df_allotment.drop(columns=['Amount_str'])
    df_allotment = df_allotment.rename(columns={'Fund': 'Ticker'})
    df_allotment['Ticker'] = df_allotment['Ticker'].str.split(' Folio').str[0]
    df_allotment = df_allotment.groupby('Ticker').agg({'Amount': 'mean', 'unit': 'sum'}).reset_index() # in case there are more than one folio for same mutual fund

    if USERNAME == "ch.ankurjawla@gmail.com":
        df_allotment["Owner"] = "Ankur"
    else:
        df_allotment['Owner'] = "Gulu"

    email_subject = extracted_tables_data[0]['email_subject']
    date_pattern = r'\d{2}-\d{2}-\d{4}'
    match = re.search(date_pattern, email_subject)

    if match:
        date_str = match.group(0)
        df_allotment['Date'] = pd.to_datetime(date_str, format='%d-%m-%Y')
    else:
        df_allotment['Date'] = pd.NaT
        print("No date found in email subject.")

    return df_allotment

def push_to_csv(USERNAME,PASSWORD):
    df_allotment = extract_table(USERNAME,PASSWORD)

    if os.path.exists(file_name):
        # If file exists, append without writing header
        df_allotment.to_csv(file_name, mode='a', header=False, index=False)
        print(f"Data appended to {file_name}")
    elif 'df_allotment' in locals() and not df_allotment.empty:
        # If file does not exist, create it and write with header
        df_allotment.to_csv(file_name, mode='w', header=True, index=False)
        print(f"Data written to {file_name}")
    else:
        print("df_allotment does not exist or is empty. No data to write.")

push_to_csv(USERNAME,PASSWORD)