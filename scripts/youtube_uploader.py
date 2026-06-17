import os
import sys
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

def get_authenticated_service():
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = os.path.join("config", "client_secrets.json")
    token_file = os.path.join("config", "youtube_token.pickle")

    credentials = None
    if os.path.exists(token_file):
        with open(token_file, "rb") as f:
            credentials = pickle.load(f)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            credentials = flow.run_local_server(port=0)
        with open(token_file, "wb") as f:
            pickle.dump(credentials, f)

    return googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

def upload_to_youtube(video_path, title, description, tags, privacy="private"):
    print(f"Bắt đầu Upload Video lên YouTube...")
    print(f"File: {video_path}")
    print(f"Tiêu đề: {title}")
    
    if not os.path.exists(os.path.join("config", "client_secrets.json")):
        print("LỖI: Không tìm thấy file client_secrets.json. Hãy vào Google Cloud Console tải về.")
        return False
        
    print("Đang xác thực OAuth 2.0...")
    try:
        youtube = get_authenticated_service()
        
        request_body = {
            "snippet": {
                "categoryId": "22",
                "title": title,
                "description": description,
                "tags": tags
            },
            "status": {
                "privacyStatus": privacy
            }
        }
        
        print("Đang tải video lên. Vui lòng chờ...")
        mediaFile = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        response_upload = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=mediaFile
        ).execute()

        print(f"Upload Thành Công! Video ID: {response_upload.get('id')}")
        return True
    except Exception as e:
        print(f"LỖI UPLOAD YOUTUBE: {str(e)}")
        if 'quotaExceeded' in str(e) or 'uploadLimitExceeded' in str(e): return 2
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python youtube_uploader.py <video_path> <title> [description] [tag1,tag2,...]")
        sys.exit(1)

    video_path = sys.argv[1]
    title = sys.argv[2]
    description = sys.argv[3] if len(sys.argv) > 3 else "Video tạo bởi FlowKit V13.0 - AI Studio"
    tags_input = sys.argv[4] if len(sys.argv) > 4 else "FlowKit,AI"
    tags = [t.strip() for t in tags_input.split(',') if t.strip()]
    
    result = upload_to_youtube(video_path, title, description, tags)
    if result == 2:
        sys.exit(2)
    elif not result:
        sys.exit(1)
