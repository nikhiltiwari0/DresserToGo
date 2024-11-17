import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase Admin SDK
cred = credentials.Certificate("credentials/service-account.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def save_metadata_to_firestore(file_metadata):
    try:
        print(f"Saving metadata to Firestore: {file_metadata}")
        doc_ref = db.collection("Images").document()
        
        # Construct Google Drive public URL
        file_id = file_metadata["id"]
        public_url = f"https://drive.google.com/file/d/{file_id}/view"
        
        doc_ref.set({
            "fileName": file_metadata["name"],
            "fileId": file_id,
            "publicUrl": public_url,  # Google Drive link
            "uploadedAt": datetime.utcnow(),
            "beenParsed": False,
            "isLiked": False,
            "clothingType": "",
            "length": 0,
            "width": 0
        })
        print(f"Metadata saved successfully for file: {file_metadata['name']}")
    except Exception as e:
        print(f"Error saving metadata to Firestore: {e}")
        raise e

def like_image(image_id):
    try:
        image_ref = db.collection("Images").document(image_id)
        doc = image_ref.get()

        if not doc.exists:
            return "No such document!"

        data = doc.to_dict()
        if data["isLiked"]:
            image_ref.update({"isLiked": False})
            return "Image unliked"
        else:
            image_ref.update({"isLiked": True})
            return "Image liked"
    except Exception as e:
        print(f"Error liking image: {e}")
        raise e

def check_if_image_parsed(image_id):
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
    