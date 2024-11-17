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

    if not file_name or not file_path:
        return jsonify({"error": "file_name and file_path are required"}), 400

    try:
        uploaded_file = upload_file(file_name, file_path)
        if not uploaded_file:
            return jsonify({"error": "Failed to upload file to Google Drive"}), 500

        save_metadata_to_firestore(uploaded_file)
        return jsonify({
            "message": "File uploaded and metadata saved successfully",
            "file_id": uploaded_file.get("id"),
            "public_url": uploaded_file.get("webViewLink", "No URL available")
        }), 200
    except FileNotFoundError as fnf_error:
        return jsonify({"error": str(fnf_error)}), 400
    except HttpError as http_error:
        return jsonify({"error": f"Google Drive API error: {http_error}"}), 500
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
    Download a file from Google Drive by its ID, process it with AI, 
    and return the results.
    """
    data = request.get_json()
    file_id = data.get("file_id")

    if not file_id:
        return jsonify({"error": "file_id is required"}), 400

    try:
        # Fetch file metadata and download the file
        file_name = f"{file_id}.jpg"
        downloaded_file_path = download_file(file_id, file_name)

        # Pass the downloaded file to the AI model
        results = service_model(downloaded_file_path)

        # Optionally, clean up the downloaded file after processing
        if os.path.exists(downloaded_file_path):
            os.remove(downloaded_file_path)

        return jsonify({
            "message": "Image processed successfully",
            "results": results
        }), 200
    except FileNotFoundError as fnf_error:
        return jsonify({"error": str(fnf_error)}), 400
    except HttpError as http_error:
        return jsonify({"error": f"Google Drive API error: {http_error}"}), 500
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
@routes.route("/process_and_upload", methods=["POST"])
def process_and_upload():
    """
    Process a local image using AI, generate new images, and upload them
    to their respective folders in Google Drive.
    """
    data = request.get_json()
    file_path = data.get("/assets/man_s tanding")  # Path to the image on your computer

    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Valid file_path is required"}), 400

    try:
        # Run the AI processing (generate cropped images)
        results = service_model(file_path)

        # Upload each generated image to its corresponding folder
        uploaded_files = []
        for result in results:
            cropped_file_name = result["file_name"]
            folder_id = result["folder_id"]

            # Upload the file to Google Drive
            uploaded_file = upload_file(cropped_file_name, cropped_file_name, folder_id)

            # Save metadata of uploaded files
            uploaded_files.append({
                "file_name": cropped_file_name,
                "folder_id": folder_id,
                "file_id": uploaded_file.get("id"),
                "webViewLink": uploaded_file.get("webViewLink", "No URL available")
            })

            # Optionally, clean up local cropped images after upload
            if os.path.exists(cropped_file_name):
                os.remove(cropped_file_name)

        return jsonify({
            "message": "Images processed and uploaded successfully",
            "uploaded_files": uploaded_files
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500