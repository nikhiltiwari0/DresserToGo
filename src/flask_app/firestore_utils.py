import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase Admin SDK
cred = credentials.Certificate("credentials/service-account.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def save_metadata_to_firestore(file_metadata, clothing_data=None):
    """
    Save file metadata to Firestore, with optional clothing data.

    Args:
        file_metadata (dict): Metadata of the file uploaded to Google Drive.
        clothing_data (list): List of dictionaries containing clothing data (optional).
    """
    try:
        # Validate that required fields exist in file_metadata
        if not file_metadata.get("id") or not file_metadata.get("name"):
            raise ValueError("Missing required fields 'id' or 'name' in file_metadata.")

        print(f"Saving metadata to Firestore: {file_metadata}")
        doc_ref = db.collection("Images").document()

        # Construct Google Drive public URL
        file_id = file_metadata["id"]
        public_url = f"https://drive.google.com/file/d/{file_id}/view"

        # Prepare metadata
        metadata = {
            "fileName": file_metadata["name"],
            "fileId": file_id,
            "publicUrl": public_url,  # Google Drive link
            "uploadedAt": datetime.utcnow(),
            "beenParsed": False,
            "isLiked": False,
            "clothingType": "",
            "length": 0,
            "width": 0
        }

        # Add clothing data if provided
        if clothing_data:
            metadata.update({"clothingData": clothing_data})

        # Save to Firestore
        doc_ref.set(metadata)
        print(f"Metadata saved successfully for file: {file_metadata['name']}")
    except ValueError as ve:
        print(f"Validation error: {ve}")
        raise ve
    except Exception as e:
        print(f"Error saving metadata to Firestore: {e}")
        raise e

def save_clothing_items(image_id, clothing_items):
    """
    Save clothing items to Firestore under the associated image.

    Args:
        image_id (str): ID of the image document.
        clothing_items (list): List of clothing item metadata dictionaries.
    """
    try:
        image_ref = db.collection("Images").document(image_id)
        doc = image_ref.get()

        if not doc.exists:
            print("No such image document!")
            return

        # Update Firestore with clothing items
        image_ref.update({"clothingItems": clothing_items})
        print(f"Clothing items saved for image ID: {image_id}")
    except Exception as e:
        print(f"Error saving clothing items: {e}")
        raise e

def like_image(image_id):
    """
    Toggle the like status of an image.

    Args:
        image_id (str): ID of the image document.

    Returns:
        str: Message indicating whether the image was liked or unliked.
    """
    try:
        image_ref = db.collection("Images").document(image_id)
        doc = image_ref.get()

        if not doc.exists:
            return "No such document!"

        data = doc.to_dict()
        is_liked = not data.get("isLiked", False)
        image_ref.update({"isLiked": is_liked})
        return "Image liked" if is_liked else "Image unliked"
    except Exception as e:
        print(f"Error liking image: {e}")
        raise e

def check_if_image_parsed(image_id):
    """
    Check if the image has been parsed.

    Args:
        image_id (str): ID of the image document.

    Returns:
        bool: True if the image has been parsed, False otherwise.
    """
    try:
        image_ref = db.collection("Images").document(image_id)
        doc = image_ref.get()

        if not doc.exists:
            return False

        data = doc.to_dict()
        return data.get("beenParsed", False)
    except Exception as e:
        print(f"Error checking if image is parsed: {e}")
        raise e
    