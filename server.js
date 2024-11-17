const { google } = require('googleapis');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process'); // For running Python scripts

// Configuration
const FOLDER_ID = "19Z01yVweJrThQxL_U0fO58Ao-fCk9nwN"; // Google Drive folder ID to monitor
const POLL_INTERVAL = 1000; // Poll interval in milliseconds
const KEYFILE = path.join(__dirname, 'credentials/service-account.json'); // Path to service account credentials
const ASSETS_DIR = path.join(__dirname, 'assets'); // Directory to save downloaded files

// Initialize the Google Drive API client
async function initializeDriveService() {
    const auth = new google.auth.GoogleAuth({
        keyFile: KEYFILE,
        scopes: ['https://www.googleapis.com/auth/drive']
    });
    return google.drive({ version: 'v3', auth });
}

// List files in the folder
async function listFilesInFolder(driveService, folderId) {
    try {
        const response = await driveService.files.list({
            q: `'${folderId}' in parents and trashed = false`,
            fields: 'files(id, name, createdTime)',
            orderBy: 'createdTime desc',
            spaces: 'drive',
        });
        return response.data.files || [];
    } catch (error) {
        console.error("Error listing files:", error.message);
        return [];
    }
}

// Download the latest file from Google Drive
async function downloadFile(driveService, fileId, fileName) {
    const filePath = path.join(ASSETS_DIR, fileName);
    const dest = fs.createWriteStream(filePath);

    console.log(`Downloading file: ${fileName}...`);

    try {
        const response = await driveService.files.get(
            { fileId, alt: 'media' },
            { responseType: 'stream' }
        );

        response.data.pipe(dest);

        await new Promise((resolve, reject) => {
            dest.on('finish', resolve);
            dest.on('error', reject);
        });

        console.log(`File saved to: ${filePath}`);
        return filePath;
    } catch (error) {
        console.error(`Error downloading file ${fileName}:`, error.message);
        return null;
    }
}

// Run the ML script with the downloaded file
function processWithML(filePath) {
    console.log(`Processing file with ML module: ${filePath}`);

    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python3', ['src/ml_module/main.py', '--file_path', filePath]);

        pythonProcess.stdout.on('data', (data) => {
            console.log(`ML output: ${data.toString()}`);
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`ML error: ${data.toString()}`);
        });

        pythonProcess.on('close', (code) => {
            if (code === 0) {
                console.log(`ML module successfully processed: ${filePath}`);
                resolve();
            } else {
                reject(new Error(`ML module failed with exit code ${code}`));
            }
        });
    });
}

// Monitor the folder for the latest file
async function monitorLatestFile() {
    const driveService = await initializeDriveService();
    let lastFileId = null; // Track the ID of the latest file

    // Ensure the assets directory exists
    if (!fs.existsSync(ASSETS_DIR)) {
        fs.mkdirSync(ASSETS_DIR, { recursive: true });
    }

    console.log(`Monitoring Google Drive folder: ${FOLDER_ID}`);

    setInterval(async () => {
        try {
            const files = await listFilesInFolder(driveService, FOLDER_ID);

            if (files.length > 0) {
                const latestFile = files[0]; // Get the most recent file
                if (latestFile.id !== lastFileId) {
                    console.log(`New file detected: ${latestFile.name} (ID: ${latestFile.id})`);
                    lastFileId = latestFile.id; // Update the last file ID

                    // Download the latest file
                    const filePath = await downloadFile(driveService, latestFile.id, latestFile.name);

                    // Run the ML API
                    if (filePath) {
                        try {
                            await processWithML(filePath);
                        } catch (error) {
                            console.error(`Error processing with ML module: ${error.message}`);
                        }
                    }
                }
            }
        } catch (error) {
            console.error("Error while monitoring folder:", error.message);
        }
    }, POLL_INTERVAL);
}

// Start monitoring
monitorLatestFile().catch(console.error);