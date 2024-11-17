from flask import Blueprint, request, jsonify
from .firestore_utils import like_image, check_if_image_parsed, save_metadata_to_firestore
from .drive_utils import upload_file, get_file_metadata, list_files_in_folder, download_file
from googleapiclient.errors import HttpError
from src.ml_module.main import DRIVE_FOLDERS, service_model  # Import the AI function
import os

routes = Blueprint("routes", __name__)

@routes.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to the Flask API. Use `/upload` to upload images, `/like` to like/unlike an image, and `/drive` to fetch files."
    })

@routes.route("/upload", methods=["POST"])
def upload_image():
    data = request.get_json()
    file_name = data.get("file_name")
    file_path = data.get("file_path")
    folder_id = data.get("folder_id")

    if not file_name or not file_path or not folder_id:
        return jsonify({"error": "file_name, file_path, and folder_id are required"}), 400

    try:
        uploaded_file = upload_file(file_name, file_path, folder_id)
        if not uploaded_file:
            return jsonify({"error": "Failed to upload file to Google Drive"}), 500

        return jsonify({
            "message": "File uploaded successfully",
            "file_id": uploaded_file.get("id"),
            "public_url": uploaded_file.get("webViewLink", "No URL available")
        }), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500

@routes.route("/like/<image_id>", methods=["POST"])
def like_unlike_image(image_id):
    """
    Toggles the like/unlike state of an image in Firestore.
    """
    try:
        message = like_image(image_id)
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/check/<image_id>", methods=["GET"])
def check_parsed(image_id):
    """
    Checks if an image has been parsed.
    """
    try:
        parsed = check_if_image_parsed(image_id)
        return jsonify({"image_id": image_id, "been_parsed": parsed}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/drive", methods=["GET"])
def list_drive_files():
    """
    Lists files from a specific Google Drive folder.
    """
    folder_id = request.args.get("folder_id")  # Example: Pass folder_id as a query parameter
    if not folder_id:
        return jsonify({"error": "folder_id is required"}), 400

    try:
        files = list_files_in_folder(folder_id)
        return jsonify({"files": files}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/drive/<file_id>", methods=["GET"])
def fetch_file_metadata(file_id):
    """
    Fetches metadata for a specific file in Google Drive.
    """
    try:
        file_metadata = get_file_metadata(file_id)
        return jsonify({"file_metadata": file_metadata}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@routes.route("/ai/process", methods=["POST"])
def process_file_with_ai():
    """
    Process files in the downloads folder based on their last character
    and upload them to their respective folders in Google Drive.
    """
    data = request.get_json()
    folder_mapping = {
        "0": "1OavV3D6tBao6KG13QjPQH4r3PI5TSv3A",  # Head
        "1": "16BKpECjxVN_N7HTtQJoaqQkCKnjmH1zz",  # Top
        "2": "1IDRD1B5mVN-Oo6HimMsM49zWlCbI1Wnu",  # Pants
        "3": "10iDngJ1k7MZw4yIJifHeJ158XIZp5M0R",  # Shoes
    }

    downloads_dir = "downloads"

    try:
        uploaded_files = []

        # Iterate over files in the downloads folder
        for file_name in os.listdir(downloads_dir):
            file_path = os.path.join(downloads_dir, file_name)

            # Ensure it's a valid file
            if not os.path.isfile(file_path):
                continue

            # Extract the last character before the file extension
            last_char = os.path.splitext(file_name)[0][-1]

            # Determine the folder ID based on the last character
            folder_id = folder_mapping.get(last_char)
            if not folder_id:
                print(f"Invalid classification for file {file_name}. Skipping.")
                continue

            # Upload the file to the correct Google Drive folder
            uploaded_file = upload_file(
                file_name=file_name,
                file_path=file_path,
                folder_id=folder_id
            )
            print(f"Uploaded file: {uploaded_file}")

            # Add to the list of uploaded files
            uploaded_files.append({
                "file_name": file_name,
                "folder_id": folder_id,
                "file_id": uploaded_file.get("id"),
                "webViewLink": uploaded_file.get("webViewLink", "No URL available")
            })

            # Delete the file locally after upload
            if os.path.exists(file_path):
                os.remove(file_path)

        return jsonify({
            "message": "Files processed and uploaded successfully",
            "uploaded_files": uploaded_files
        }), 200

    except Exception as error:
        print(f"Error processing files: {error}")
        return jsonify({"error": str(error)}), 500
    

@routes.route("/ai/process_and_upload", methods=["POST"])
def process_file_with_ai_and_upload():
    """
    Process files in the 'downloads' directory and upload each file to 
    a specified Google Drive folder based on its key in the data.
    """
    try:
        data = request.get_json()

        if not data or 'folder_mappings' not in data:
            return jsonify({"error": "Invalid input. 'folder_mappings' required"}), 400

        folder_mappings = data["folder_mappings"]  # Expected to be a dict of file_name -> folder_id

        # Get list of files in the 'downloads' directory
        downloads_path = "downloads"
        if not os.path.exists(downloads_path):
            return jsonify({"error": f"Directory '{downloads_path}' not found"}), 400

        files = [f for f in os.listdir(downloads_path) if os.path.isfile(os.path.join(downloads_path, f))]

        if not files:
            return jsonify({"error": "No files found in the 'downloads' directory"}), 400

        uploaded_files = []
        for file_name in files:
            full_path = os.path.join(downloads_path, file_name)
            folder_id = folder_mappings.get(file_name)

            if not folder_id:
                print(f"Skipping {file_name}: No folder ID provided in 'folder_mappings'")
                continue

            # Upload the file to the specified folder
            uploaded_file = upload_file(file_name, full_path, folder_id)
            uploaded_files.append({
                "file_name": file_name,
                "folder_id": folder_id,
                "file_id": uploaded_file.get("id"),
                "webViewLink": uploaded_file.get("webViewLink", "No URL available")
            })

            # Delete the local file after upload
            os.remove(full_path)

        return jsonify({
            "message": "Files processed, uploaded, and cleaned up successfully",
            "uploaded_files": uploaded_files
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500