require('dotenv').config(); // Load .env variables
const express = require('express');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { google } = require('googleapis');
const axios = require('axios');

const app = express();
const PORT = 3010;

// Middleware to parse JSON bodies
app.use(express.json());

// Paths
const downloadDir = path.join(__dirname, 'downloads');
const outputDir = path.join(__dirname, 'output');
const outputFilePath = path.join(outputDir, 'stitched.png');

// Google OAuth2 Setup
const oauth2Client = new google.auth.OAuth2(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET
);

// Set refresh token
oauth2Client.setCredentials({
  refresh_token: process.env.GOOGLE_REFRESH_TOKEN,
});

// Google Drive instance
const drive = google.drive({
  version: 'v3',
  auth: oauth2Client,
});

// Function to download images
const downloadImage = async (url, filepath) => {
  const response = await axios({
    url,
    method: 'GET',
    responseType: 'stream',
  });

  return new Promise((resolve, reject) => {
    const writer = fs.createWriteStream(filepath);
    response.data.pipe(writer);
    writer.on('finish', resolve);
    writer.on('error', reject);
  });
};

// Function to upload file to Google Drive
const uploadToGoogleDrive = async (filePath, folderId) => {
  const fileName = path.basename(filePath);

  const fileMetadata = {
    name: fileName,
    parents: [folderId], // Google Drive Folder ID
  };

  const media = {
    mimeType: 'image/png',
    body: fs.createReadStream(filePath),
  };

  const response = await drive.files.create({
    resource: fileMetadata,
    media: media,
    fields: 'id',
  });

  return response.data.id;
};

// POST endpoint to handle the full workflow
app.post('/handle-like', async (req, res) => {
  const { likedImages } = req.body;

  if (!likedImages || !Array.isArray(likedImages)) {
    return res.status(400).json({
      message: 'Invalid data. Expected likedImages array.',
    });
  }

  console.log('Received liked images:', likedImages);

  try {
    // Ensure necessary directories exist
    [downloadDir, outputDir].forEach((dir) => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });

    // Initialize an array to store the file paths
    const downloadedFilePaths = [];

    // Step 1: Download the images
    console.log('Downloading images...');
    for (const image of likedImages) {
      const filePath = path.join(downloadDir, image.name);

      console.log(`Downloading ${image.name} to ${filePath}...`);

      try {
        await downloadImage(image.url, filePath);

        // Ensure the file exists after download
        if (!fs.existsSync(filePath)) {
          throw new Error(`File not found after download: ${filePath}`);
        }

        // Add the file path to the array
        downloadedFilePaths.push(filePath);
      } catch (downloadError) {
        console.error(`Failed to download ${image.name}:`, downloadError.message);
        continue; // Skip problematic files and continue processing others
      }
    }

    console.log('All images downloaded.');

    // Step 2: Run the Python script to stitch images
    console.log('Stitching images...');
    const imageFiles = downloadedFilePaths;

    if (imageFiles.length === 0) {
      throw new Error('No images available for stitching.');
    }

    const pythonProcess = spawn('python3', [
      path.join(__dirname, 'stitch.py'),
      ...imageFiles.slice(0, 4), // Use first 4 images for stitching
      outputFilePath,
    ]);

    await new Promise((resolve, reject) => {
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          console.log('Images stitched successfully.');
          resolve();
        } else {
          reject(new Error('Python script failed to stitch images.'));
        }
      });
    });

    // Step 3: Upload the stitched image to Google Drive
    console.log('Uploading stitched image to Google Drive...');
    const googleDriveFolderId = '1HbzQv7fWIAQO2SH08HTaYODM7oK3zBYk'; // Replace with your folder ID
    const fileId = await uploadToGoogleDrive(outputFilePath, googleDriveFolderId);
    console.log(`Stitched image uploaded to Google Drive with ID: ${fileId}`);

    // Step 4: Clean up local directories
    console.log('Cleaning up...');
    fs.rmSync(downloadDir, { recursive: true, force: true });
    fs.rmSync(outputDir, { recursive: true, force: true });

    res.status(200).json({
      message: 'Workflow completed successfully.',
      googleDriveFileId: fileId,
    });
  } catch (error) {
    console.error('Error handling liked images:', error);
    res.status(500).json({ message: 'Failed to complete workflow.' });
  }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});
