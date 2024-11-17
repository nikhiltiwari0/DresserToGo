import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload



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

def upload_file(file_name, file_path, folder_id):
    """Upload a file to Google Drive."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file at {file_path} does not exist.")
        
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]  # Use the passed folder ID
        }
        media = MediaFileUpload(file_path, mimetype='image/jpeg')

        print(f"Uploading file: {file_name} to folder: {folder_id}")  # Debugging
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()

        if not file:
            raise ValueError("Drive API returned None for the created file.")

        print(f"File uploaded successfully: {file}")
        return file
    except Exception as error:
        print(f"Error during file upload: {error}")
        raise error

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
        return files
    except Exception as error:
        print(f"Error listing files in folder: {error}")
        return []

def get_file_metadata(file_id):
    """Fetch metadata for a specific file in Google Drive."""
    try:
        print(f"Fetching metadata for file ID: {file_id}")  # Debugging
        file_metadata = drive_service.files().get(
            fileId=file_id,
            fields='id, name, webViewLink, mimeType, size'
        ).execute()
        print(f"Metadata for file {file_id}: {file_metadata}")  # Debugging
        return file_metadata
    except HttpError as error:
        print(f"Error fetching metadata for file {file_id}: {error}")
        return None
    
def download_file(file_id, file_name):
    """Download a file from Google Drive."""
    try:
        request = drive_service.files().get_media(fileId=file_id)
        file_path = os.path.join("downloads", file_name)

        os.makedirs("downloads", exist_ok=True)
        with open(file_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download progress: {int(status.progress() * 100)}%")

        print(f"File downloaded successfully: {file_path}")
        return file_path
    except HttpError as error:
        print(f"Error downloading file: {error}")
        raise error