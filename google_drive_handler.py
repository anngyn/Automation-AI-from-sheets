import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

load_dotenv() 

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE_PATH")

def get_drive_service():
    print(f"[INFO] Authenticating with file: '{SERVICE_ACCOUNT_FILE}'") 
    
    if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Error: Credential file not found at '{SERVICE_ACCOUNT_FILE}'. Please check GOOGLE_SERVICE_ACCOUNT_FILE_PATH in .env")

    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        print("[INFO] Authentication and service creation successful.") 
        return service
    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}") 

def upload_file_to_drive(file_path, file_name, mime_type, folder_id):
    print(f"[INFO] Starting to upload file '{file_name}' to folder '{folder_id}'.") 
    
    service = get_drive_service()
    
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webContentLink',
            supportsAllDrives=True  #
        ).execute()
        
        print(f"[INFO] File uploaded successfully. URL: {file.get('webContentLink')}")
        return file.get('webContentLink')
    except HttpError as error:
        print(f"[ERROR] *** Google Drive API reported HttpError: {error} ***")
        raise error
        
def create_folder_with_service_account(folder_name):
    """Create a folder owned by the Service Account (Not recommended)."""
    print(f"[WARNING] Creating folder '{folder_name}' owned by Service Account. This folder will not be able to contain files.")
    service = get_drive_service()
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    try:
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    except HttpError as error:
        print(f"Error creating folder using service account: {error}")
        return None
