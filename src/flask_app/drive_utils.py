import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Constants
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'credentials/service-account.json'

# Authenticate Google Drive API
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

def check_file_exists(file_name):
    """Check if a file with the given name exists in Google Drive."""
    try:
        query = f"name='{file_name}' and trashed=false"
        results = drive_service.files().list(q=query).execute()
        return len(results.get('files', [])) > 0
    except HttpError as error:
        print(f"An error occurred: {error}")
        return False

def upload_file(file_name, file_path):
    """Upload a file to Google Drive."""
    try:
        file_metadata = {
            'name': file_name,
            'parents': ['1H66qHlVz4idI-gMPVZi79hf7SGu6h_lD'] 
        }
        media = MediaFileUpload(file_path, mimetype='image/jpeg')

        print(f"Uploading file: {file_name} from path: {file_path}")  # Debug output
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()

        print(f"File uploaded successfully: {file.get('id')}")  # Debug output
        return file
    except Exception as error:
        print(f"Error during upload: {error}")  # Debug output
        return None
    
def list_files_in_folder(folder_id):
    """List all files in a Google Drive folder."""
    try:
        results = drive_service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        files = results.get('files', [])
        if not files:
            print("No files found in the folder.")
        else:
            for file in files:
                print(f"Found file: {file['name']} ({file['id']})")
    except Exception as error:
        print(f"Error listing files in folder: {error}")