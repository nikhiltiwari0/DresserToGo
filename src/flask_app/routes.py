from flask import Blueprint, jsonify, request
from src.flask_app.drive_utils import check_file_exists, list_files_in_folder, upload_file

# Blueprint for routes
routes = Blueprint('routes', __name__)

@routes.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask API. Use the `/check` endpoint with POST requests."

@routes.route('/check', methods=['GET', 'POST'])
def check_and_upload():
    list_files_in_folder('1H66qHlVz4idI-gMPVZi79hf7SGu6h_lD')
    if request.method == 'GET':
        return jsonify({
            "message": "This endpoint only accepts POST requests.",
            "example_payload": {
                "file_name": "example.jpg",
                "file_path": "path/to/your/file.jpg"
            }
        }), 405

    file_name = request.json.get('file_name')
    file_path = request.json.get('file_path')

    if not file_name or not file_path:
        return jsonify({"error": "file_name and file_path are required"}), 400

    print(f"Received file_name: {file_name}, file_path: {file_path}")  # Debug log

    if check_file_exists(file_name):
        print("File already exists on Drive.")  # Debug log
        return jsonify({"message": "File already exists"}), 400
    else:
        print("File does not exist. Uploading...")  # Debug log
        uploaded_file = upload_file(file_name, file_path)
        if uploaded_file:
            print(f"File uploaded successfully: {uploaded_file}")  # Debug log
            return jsonify({
                "message": "File uploaded successfully",
                "file_id": uploaded_file.get('id')
            }), 200
        else:
            print("File upload failed.")  # Debug log
            return jsonify({"error": "File upload failed"}), 500