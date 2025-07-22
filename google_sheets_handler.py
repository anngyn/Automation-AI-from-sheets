# Ví dụ đơn giản về việc đọc Google Sheets
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
def get_sheets_service():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    # Lấy đường dẫn từ biến môi trường
    SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE_PATH") 

    if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Service account file not found at {SERVICE_ACCOUNT_FILE}. Please check GOOGLE_SERVICE_ACCOUNT_FILE_PATH in your .env")

    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service
def read_data_from_sheet(spreadsheet_id, range_name):
    service = get_sheets_service()
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
        return pd.DataFrame()
    
    headers = values[0]
    data = values[1:]
    df = pd.DataFrame(data, columns=headers)
    return df

# Example usage:
spreadsheet_id = '1oUmIYN-E9PzFnWo-2HFiMCa4WYlp3zI7lWcIjmOhLVQ'
range_name = 'Sheet1!A:E'
df_input = read_data_from_sheet(spreadsheet_id, range_name)

