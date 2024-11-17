const express = require("express");
const { google } = require("googleapis");
const cors = require("cors");
require("dotenv").config();

const app = express();
const port = 3000;

// Enable CORS for all requests
app.use(cors());

// Google API Credentials
const CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
const CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET;
const REFRESH_TOKEN = process.env.GOOGLE_REFRESH_TOKEN;

// Initialize OAuth2 Client
const oauth2Client = new google.auth.OAuth2(
  CLIENT_ID,
  CLIENT_SECRET,
  "https://developers.google.com/oauthplayground"
);
oauth2Client.setCredentials({
  refresh_token: REFRESH_TOKEN,
});

const drive = google.drive({ version: "v3", auth: oauth2Client });

// API Route to List Files in a Folder
app.get("/files", async (req, res) => {
  const folderId = req.query.folderId; // Expect folderId as a query parameter

  if (!folderId) {
    return res.status(400).send("Folder ID is required");
  }

  try {
    const response = await drive.files.list({
      q: `'${folderId}' in parents and trashed = false`,
      fields: "files(id, name)",
    });

    const files = response.data.files || [];

    // Log each file's ID and the constructed URL
    files.forEach((file) => {
      console.log(`File ID: ${file.id}`);
      console.log(`Constructed URI: https://drive.google.com/uc?id=${file.id}`);
    });

    res.json(files); // Send the list of files as JSON
  } catch (error) {
    console.error("Error fetching files:", error.message);
    res.status(500).send("Error fetching files");
  }
});

// Start the Server
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
