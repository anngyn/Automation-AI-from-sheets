import os
import time
import uuid
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# Import handlers (đảm bảo các file này cũng có load_dotenv() ở đầu)
from google_sheets_handler import read_data_from_sheet
from ai_model_generator import generate_asset
from google_drive_handler import upload_file_to_drive
from notification_handler import send_email_notification, send_slack_notification
from database_logger import log_task_status, init_db
from report_generator import generate_daily_report

# Initialize database
init_db()

# Configuration variables
SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEET_RANGE = 'Sheet1!A:Z'  # Điều chỉnh dựa trên cấu trúc sheet của bạn
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
DEFAULT_DRIVE_FOLDER_NAME = "My_AI_Generated_Assets"

# --- Khối logic khởi tạo effective_drive_folder_id (Global) ---
effective_drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

# Kiểm tra ID thư mục Drive
if not effective_drive_folder_id:
    print("CRITICAL ERROR: GOOGLE_DRIVE_FOLDER_ID is not set in the .env file.")
    print("Please provide the ID of a folder shared with 'Editor' permissions to the Service Account.")
    # Send error notification and exit
    send_slack_notification("❌ Automation workflow failed: GOOGLE_DRIVE_FOLDER_ID is not set in .env file.")
    exit()  # Stop the entire process

print(f"Using Drive Folder ID configured from .env: {effective_drive_folder_id}")

def run_automation_workflow():
    print("Starting automation workflow...")

    # Kiểm tra xem effective_drive_folder_id có hợp lệ không trước khi bắt đầu
    if not effective_drive_folder_id:
        print("Error: No valid Drive folder ID to store assets. Stopping workflow.")
        send_slack_notification("❌ Automation workflow failed: No valid Drive folder ID for asset storage.")
        return 

    df_tasks = read_data_from_sheet(SPREADSHEET_ID, SHEET_RANGE)
    
    if df_tasks.empty:
        print("No tasks found in Google Sheet.")
        send_slack_notification("Automation workflow completed: No tasks found in Google Sheet.")
        return
    
    for index, row in df_tasks.iterrows():
        task_id = str(uuid.uuid4())
        description = row.get('Description', '') 
        print(f"Processing description: '{description}'")  # Log actual description being processed
        desired_output_format = row.get('Desired Output Format', '').upper()
        model_specification = row.get('Model Specification (OpenAI/Claude)', '').lower()

        asset_content = None
        asset_url = None
        status = 'failure'
        error_message = None
        temp_file_path = None

        try:
            asset_content = generate_asset(description, desired_output_format, model_specification)

            if asset_content:
                file_extension = desired_output_format.lower()
                temp_file_path = f"temp_asset_{task_id}.{file_extension}"
                with open(temp_file_path, 'wb') as f:
                    f.write(asset_content)
                
                mime_type = ""
                if desired_output_format in ["PNG", "JPG"]:
                    mime_type = f"image/{file_extension}"
                elif desired_output_format == "MP3":
                    mime_type = "audio/mpeg"

                print(f"Attempting to upload file to Drive Folder ID: {effective_drive_folder_id}")
                asset_url = upload_file_to_drive(
                    temp_file_path,
                    f"{description.replace(' ', '_')}_{task_id}.{file_extension}",
                    mime_type,
                    effective_drive_folder_id 
                )
                status = 'success'
            else:
                error_message = f"Asset generation failed for '{description}' with format {desired_output_format}. No content returned from API."
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            print(f"Error processing task {task_id}: {e}")
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        log_task_status(task_id, description, status, asset_url, error_message)

        if status == 'success':
            send_email_notification(ADMIN_EMAIL, f"[Automation Success] Task {task_id} Completed",
                                    f"Asset for '{description}' generated and stored at: {asset_url}")
            send_slack_notification(f"✅ Task {task_id} for '{description}' completed successfully. Asset URL: {asset_url}")
        else:
            send_email_notification(ADMIN_EMAIL, f"[Automation Failed] Task {task_id} Failed",
                                    f"Task for '{description}' failed. Error: {error_message}")
            send_slack_notification(f"❌ Task {task_id} for '{description}' failed. Error: {error_message}")

    print("\nAutomation workflow completed.")

# --- Phần để chạy script ---
if __name__ == "__main__":
    run_automation_workflow()

    # Tạo báo cáo hàng ngày
    print("\nGenerating daily report...")
    generate_daily_report(ADMIN_EMAIL)
