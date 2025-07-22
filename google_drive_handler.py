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
    print(f"[DEBUG] Đang xác thực với file: '{SERVICE_ACCOUNT_FILE}'") 
    
    if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Lỗi: Không tìm thấy tệp credentials tại '{SERVICE_ACCOUNT_FILE}'. Vui lòng kiểm tra biến GOOGLE_SERVICE_ACCOUNT_FILE_PATH trong .env")

    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        print("[DEBUG] Xác thực và tạo service thành công.") 
        return service
    except Exception as e:
        print(f"[DEBUG] Lỗi khi xác thực: {e}") 

def upload_file_to_drive(file_path, file_name, mime_type, folder_id):
    print(f"[DEBUG] Bắt đầu tải tệp '{file_name}' lên thư mục '{folder_id}'.") 
    
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
        
        print(f"[DEBUG] Tải tệp thành công. URL: {file.get('webContentLink')}")
        return file.get('webContentLink')
    except HttpError as error:
        print(f"[DEBUG] *** API Google Drive báo lỗi HttpError: {error} ***")
        raise error
        
def create_folder_with_service_account(folder_name):
    """Tạo thư mục do Service Account sở hữu (Không khuyến khích sử dụng)."""
    print(f"[CẢNH BÁO] Đang tạo thư mục '{folder_name}' do Tài khoản Dịch vụ sở hữu. Thư mục này sẽ không thể chứa tệp.")
    service = get_drive_service()
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    try:
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    except HttpError as error:
        print(f"Lỗi khi tạo thư mục bằng tài khoản dịch vụ: {error}")
        return None