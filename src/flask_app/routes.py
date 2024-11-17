from flask import Blueprint, request, jsonify
from .firestore_utils import like_image, check_if_image_parsed, save_metadata_to_firestore
from .drive_utils import upload_file

routes = Blueprint("routes", __name__)

@routes.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to the Flask API. Use `/upload` to upload images and `/like` to like/unlike an image."
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
        save_metadata_to_firestore(uploaded_file)
        return jsonify({"message": "File uploaded and metadata saved successfully", "file_id": uploaded_file["id"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@routes.route("/like/<image_id>", methods=["POST"])
def like_unlike_image(image_id):
    try:
        message = like_image(image_id)
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/check/<image_id>", methods=["GET"])
def check_parsed(image_id):
    try:
        parsed = check_if_image_parsed(image_id)
        return jsonify({"image_id": image_id, "been_parsed": parsed}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500