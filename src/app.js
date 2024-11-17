const { google } = require("googleapis");
const admin = require("firebase-admin");
const fs = require("fs");
require("dotenv").config(); 

// Google API Credentials
const CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
const CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET;
const REFRESH_TOKEN = process.env.GOOGLE_REFRESH_TOKEN;

// Initialize Firebase Admin SDK
const serviceAccount = {
  type: "service_account",
  project_id: process.env.FIREBASE_PROJECT_ID,
  private_key_id: process.env.FIREBASE_PRIVATE_KEY_ID,
  private_key: process.env.FIREBASE_PRIVATE_KEY.replace(/\\n/g, "\n"), 
  client_email: process.env.FIREBASE_CLIENT_EMAIL,
  client_id: process.env.FIREBASE_CLIENT_ID,
  auth_uri: process.env.FIREBASE_AUTH_URI,
  token_uri: process.env.FIREBASE_TOKEN_URI,
  auth_provider_x509_cert_url: process.env.FIREBASE_AUTH_PROVIDER_CERT_URL,
  client_x509_cert_url: process.env.FIREBASE_CLIENT_CERT_URL,
};

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

const db = admin.firestore();

// Initialize Google OAuth2 Client
const oauth2Client = new google.auth.OAuth2(CLIENT_ID, CLIENT_SECRET, "https://developers.google.com/oauthplayground");
oauth2Client.setCredentials({
  refresh_token: REFRESH_TOKEN,
});

// function to like an image and unlike an image
async function likeImage(imageId) {
  const imageRef = db.collection("Images").doc(imageId);
  const doc = await imageRef.get();
  if (!doc.exists) {
    console.log("No such document!");
    return;
  } else {
    const data = doc.data();
    if (data.isLiked) {
      await imageRef.update({ isLiked: false });
      console.log("Image unliked");
    } else {
      await imageRef.update({ isLiked: true });
      console.log("Image liked");
    }
  }
}

// Check if image has gone through the model.

async function checkIfImageHasBeenParsed(imageId) {
  const imageRef = db.collection("Images").doc(imageId);
  const doc = await imageRef.get();
  if (!doc.exists) {
    console.log("No such document!");
    return false;
  } else {
    const data = doc.data();
    goToModel(imageId);
    return data.beenParsed;
  }
}

async function goToModel(imageId) {
  beenParsed = true;
  console.log("Image has been parsed");
}

const drive = google.drive({ version: "v3", auth: oauth2Client });

// Function to upload a file to Google Drive and place it in the FULL Folder 
async function uploadFileToDrive(filePath) {
    try {
      const fileName = filePath.split("/").pop();
      const folderId = "1H66qHlVz4idI-gMPVZi79hf7SGu6h_lD";
  
      const fileMetadata = {
        name: fileName,
        mimeType: "image/jpeg",
        parents: [folderId],
      };
  
      const media = {
        mimeType: "image/jpeg",
        body: fs.createReadStream(filePath),
      };
  
      const response = await drive.files.create({
        requestBody: fileMetadata,
        media: media,
        fields: "id, name, webViewLink",
      });
  
      console.log(`File uploaded successfully to folder 'FULL': ${response.data.name}`);
      return response.data;
    } catch (error) {
      console.error("Error uploading to Drive:", error.message);
      throw error;
    }
  }

// Function to save metadata to Firestore
async function saveToFirestore(fileMetadata) {
  try {
    const docRef = db.collection("Images").doc();
    await docRef.set({
      fileName: fileMetadata.name,
      fileId: fileMetadata.id,
      publicUrl: fileMetadata.webViewLink,
      uploadedAt: admin.firestore.FieldValue.serverTimestamp(),
      beenParsed: false,
      isLiked: false,
    });

    console.log(`File metadata saved to Firestore: ${fileMetadata.name}`);
  } catch (error) {
    console.error("Error saving to Firestore:", error.message);
    throw error;
  }
}

// Test OAuth2 Client
async function testOAuth2Client() {
  try {
    const tokenInfo = await oauth2Client.getAccessToken();
    console.log("Access token retrieved successfully:", tokenInfo.token);
  } catch (error) {
    console.error("Error authenticating OAuth2 client:", error.message);
  }
}

// Main Workflow
(async function main() {
    const filePath = "../assets/man_standing.jpg"; // Should take in image from user
    const testImageId = "tAcyON2lwHhefbn82nKh"; //  test to see if imageID parser is working
  
    try {
      console.log("Testing OAuth2 authentication...");
      await testOAuth2Client();
  
      console.log("Starting file upload...");
      const fileMetadata = await uploadFileToDrive(filePath);
  
      console.log("Saving metadata to Firestore...");
      await saveToFirestore(fileMetadata);
  
      console.log("Testing `checkIfImageHasBeenParsed`...");
      const isParsed = await checkIfImageHasBeenParsed(testImageId);
      console.log(`Has the image (ID: ${testImageId}) been parsed?`, isParsed);
  
      console.log("Workflow completed successfully!");
    } catch (error) {
      console.error("Error in main workflow:", error.message);
    }
  })();