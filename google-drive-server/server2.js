const express = require("express");
const { google } = require("googleapis");
const multer = require("multer");
const fs = require("fs");
require("dotenv").config();

const app = express();
const port = 3005;

// Google API Credentials
const CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
const CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET;
const REFRESH_TOKEN = process.env.GOOGLE_REFRESH_TOKEN;

// Initialize Google OAuth2 Client
const oauth2Client = new google.auth.OAuth2(
  CLIENT_ID,
  CLIENT_SECRET,
  "https://developers.google.com/oauthplayground"
);
oauth2Client.setCredentials({
  refresh_token: REFRESH_TOKEN,
});

const drive = google.drive({ version: "v3", auth: oauth2Client });

// Multer configuration for file uploads (files stored temporarily in "uploads/" folder)
const upload = multer({ dest: "uploads/" });

// Function to upload a file to Google Drive
async function uploadFileToDrive(filePath, fileName, folderId) {
  try {
    const fileMetadata = {
      name: fileName, // Name of the file in Google Drive
      parents: [folderId], // Specify the folder ID
    };

    const media = {
      mimeType: "image/png", // Update MIME type if needed
      body: fs.createReadStream(filePath), // Read file from the temporary location
    };

    const response = await drive.files.create({
      resource: fileMetadata,
      media: media,
      fields: "id", // Return only the file ID
    });

    console.log(`File uploaded successfully: ${response.data.id}`);
    return response.data.id;
  } catch (error) {
    console.error("Error uploading file to Drive:", error.message);
    throw error;
  }
}

// API endpoint to handle file uploads
app.post("/upload", upload.single("image"), async (req, res) => {
  try {
    const folderId = "19Z01yVweJrThQxL_U0fO58Ao-fCk9nwN"; // Replace with your Google Drive folder ID
    const filePath = req.file.path; // File's temporary path on the server
    const fileName = req.file.originalname; // Original name of the file

    console.log(`Uploading file "${fileName}" to folder ID: ${folderId}...`);
    const fileId = await uploadFileToDrive(filePath, fileName, folderId);

    // Clean up the temporary file
    fs.unlinkSync(filePath);

    res.status(200).json({
      message: "File uploaded successfully",
      fileId: fileId,
    });
  } catch (error) {
    console.error("Error handling file upload:", error.message);
    res.status(500).json({ error: "Failed to upload file" });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
