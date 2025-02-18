# DresserToGo

**DresserToGo** is a mobile app developed during **CheeseHacks 2024** that leverages AI to help users categorize and create personalized outfits from images of their clothing. By splitting user-uploaded images into four distinct clothing categories, the app enables seamless outfit creation and dynamic recommendations.

## Features

- **AI-Driven Categorization**: The app uses machine learning to automatically classify clothing items into four categories: tops, bottoms, shoes, and accessories.
- **Outfit Creation**: Users can create personalized outfits by mixing and matching categorized clothing items.
- **Dynamic Recommendations**: Based on user preferences, the app generates outfit suggestions to inspire new looks.
- **Cloud-Based Storage**: All user-generated outfits and images are stored securely in the cloud, allowing for easy access and retrieval.
- **Seamless Integration**: The app is built with a user-friendly interface that integrates smoothly with the AI backend for quick and efficient clothing categorization.

## Technologies Used

- **Frontend**: React (for the user interface), TypeScript
- **Backend**: Node.js, Flask
- **Machine Learning**: Python, TensorFlow (for the AI model to classify and segment clothing items)
- **Cloud Storage**: Firebase, Google Drive APIs
- **Version Control**: Git, GitHub

## Setup Instructions

### Prerequisites
Before you begin, ensure you have the following installed:
- Node.js
- npm (or yarn)
- Python 3.x
- Firebase CLI (for setting up Firebase)

### Frontend Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/dressertogo.git
   cd dressertogo
   ```

2. Install the required frontend dependencies:
   ```bash
   npm install
   ```

3. Run the app locally:
   ```bash
   npm start
   ```
4. Open your browser and navigate to http://localhost:3000 to see the app in action.

### Backend Setup
1. Set up the backend API:
   - Make sure you have Python 3.x installed.
   - Navigate to the `backend` directory:
     ```bash
     cd backend
     ```
   - Install the required Python dependencies:
     ```bash
     pip install -r requirements.txt
     ```

2. Run the Flask server:
   ```bash
   python app.py
   ```

3. The server will be running on `http://localhost:5000`.
