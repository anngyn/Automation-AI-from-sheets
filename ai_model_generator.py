import requests
import os
from dotenv import load_dotenv
from google.cloud import texttospeech_v1 as texttospeech
from google.oauth2 import service_account

# Tải các biến môi trường từ file .env
load_dotenv()

# --- Cấu hình API và đường dẫn ---
HUGGING_FACE_API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE_PATH")

# --- Khởi tạo Client ---

# Khởi tạo Google Cloud Text-to-Speech Client
tts_client = None
if GOOGLE_SERVICE_ACCOUNT_FILE and os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE):
    try:
        credentials = service_account.Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT_FILE)
        tts_client = texttospeech.TextToSpeechClient(credentials=credentials)
        print("✅ Khởi tạo Google Cloud Text-to-Speech client thành công.")
    except Exception as e:
        print(f"Lỗi khi khởi tạo Google Cloud TTS client: {e}")
else:
    print("⚠️ Cảnh báo: Biến môi trường GOOGLE_SERVICE_ACCOUNT_FILE_PATH chưa được đặt hoặc không tìm thấy tệp. Chức năng Google Cloud TTS sẽ không hoạt động.")

def generate_image_with_huggingface(description):
    """
    Tạo ảnh bằng Hugging Face Inference API.
    """
    if not HUGGING_FACE_API_TOKEN:
        print("Lỗi: HUGGING_FACE_API_TOKEN chưa được đặt.")
        return None

    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}"}
    payload = {"inputs": description}
    
    print(f"Đang gọi Hugging Face để tạo ảnh cho: {description}")
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60) # Thêm timeout để tránh treo
        response.raise_for_status()  # Báo lỗi nếu status code là 4xx hoặc 5xx
        return response.content # Trả về nội dung (bytes) của ảnh
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi Hugging Face Image API: {e}")
        # In thêm nội dung phản hồi để gỡ lỗi tốt hơn
        print(f"Nội dung phản hồi từ server: {response.text if 'response' in locals() else 'Không có phản hồi'}")
        return None

def generate_audio_with_google_cloud_tts(description):
    """
    Tạo âm thanh (MP3) bằng Google Cloud Text-to-Speech.
    """
    if not tts_client:
        print("Lỗi: Google Cloud TTS client chưa được khởi tạo.")
        return None

    synthesis_input = texttospeech.SynthesisInput(text=description)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Standard-C",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    print(f"Đang gọi Google Cloud TTS để tạo âm thanh cho: {description}")
    try:
        response = tts_client.synthesize_speech(
            request={"input": synthesis_input, "voice": voice, "audio_config": audio_config}
        )
        return response.audio_content
    except Exception as e:
        print(f"Lỗi khi gọi Google Cloud TTS: {e}")
        return None

# --- Hàm chính điều hướng ---
def generate_asset(description, desired_format, model_specification):
    """
    Tạo asset dựa trên mô tả và định dạng mong muốn.
    """
    if desired_format.upper() in ["PNG", "JPG"]:
        print(f"Attempting to generate image using Hugging Face for: {description}")
        return generate_image_with_huggingface(description)
    elif desired_format.upper() == "MP3":
        print(f"Attempting to generate audio using Google Cloud TTS for: {description}")
        return generate_audio_with_google_cloud_tts(description)
    else:
        print(f"Unsupported desired format for free APIs: {desired_format}")
        return None