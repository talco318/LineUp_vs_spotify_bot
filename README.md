# ![image](https://github.com/user-attachments/assets/13331f96-4ae2-4d6e-b63e-a73ec2c9f83d) LineUp_vs_spotify_bot ![image](https://github.com/user-attachments/assets/13331f96-4ae2-4d6e-b63e-a73ec2c9f83d)


 
## Description:
Are you a music enthusiast gearing up for the next Tomorrowland festival? Look no further! The Tomorrowland Playlist Analyzer Bot is your ultimate companion for making the most of this epic music event.


### **Features:**

- **Playlist Analysis:** Send the bot your Spotify playlist links, and it will analyze your playlists (V2- Multiple playlist support added!) to identify all the artists set to perform at Tomorrowland.
- **Weekend Selection Filter:** Users can filter the output by selecting their preferred weekend, ensuring they get the most relevant information for their visit.
- **Detailed Show Information:** The bot provides comprehensive details about each artist's show at the festival, including set times, stage locations, and other essential information. It also includes links to the Spotify pages of each artist (V2).
- **User-Friendly:** With a user-friendly interface on Telegram, it's easy for anyone to use, whether you're a tech whiz or a festival newbie.
- Powered by Spotify and Telegram APIs: This bot leverages the Spotify API to access playlist information and the Telegram Bot API for seamless communication.
- **Tomorrowland API (V2):** The bot uses the Tomorrowland API for real-time updates, ensuring the most accurate and up-to-date information.
- **AI-Powered Lineup Creation (New in V2! Gemini API):** The bot can create a custom lineup based on the details it provides, including walking time between stages, set times, and artist preferences.
- **Meal Suggestions (V2):** The bot can recommend nearby food options and estimate walking times to food vendors, ensuring you don't miss a beat while fueling up.
- **Personalized Recommendations (V2):** Leveraging machine learning algorithms, the bot can suggest artists and shows based on your music preferences and past festival experiences.

![image](https://github.com/talco318/LineUp_vs_spotify_bot/assets/12784722/964751cd-0878-47cb-82f8-d4d39b3c2d25)
![image](https://github.com/talco318/LineUp_vs_spotify_bot/assets/12784722/df367686-971f-46c1-9574-0703672dcfbb)


## How to Use:
* Start a chat with the [LineUp_vs_spotify_bot](https://t.me/TML_lineup_vs_spotify_bot) on Telegram.
* Send the bot the link to your Spotify playlist.
* Sit back and relax as the bot analyzes your playlist and provides you with a list of all the artists who will be performing at Tomorrowland.
* Explore additional details about each artist's show and plan your festival experience accordingly.
* Let the AI customize your lineup, receive meal recommendations, and get personalized suggestions for an unforgettable Tomorrowland journey.

## Why This Project?: 
As a music lover and a Tomorrowland enthusiast, I created this bot to enhance the festival experience for fellow music aficionados. Tomorrowland is all about discovering new artists and immersing yourself in the world of music, and this bot is designed to help you do just that.
Connect with me and let's make your Tomorrowland journey even more unforgettable! 🎵🌟


## Contributions and Feedback: 
Contributions and feedback are highly welcome! If you'd like to contribute to this project or have suggestions for improvement, please don't hesitate to reach out.

## Connect with Me: 
Feel free to connect with me on [LinkedIn](https://www.linkedin.com/in/talco318/ "Tal Cohen in LinkedIn") or through the Telegram bot. Let's share our passion for music and Tomorrowland! 🚀🎪🎉

## Running the Full Stack Application

This project includes a Flask backend and a React frontend. Follow these steps to run the application locally:

### 1. Prerequisites
* Python 3.x installed
* Node.js and npm installed
* Git (for cloning the repository)

### 2. Clone the Repository
If you haven't already, clone the repository to your local machine:
```bash
git clone <repository-url>
cd <repository-directory> # Navigate to the root directory of the project
```

### 3. Backend Setup (Flask)
The backend server provides the API endpoints for the application.

   a.  **Navigate to the root directory of the project.**
       If you're not already there, ensure your terminal is in the project's root directory.

   b.  **Install backend dependencies:**
       It's recommended to use a virtual environment.
       ```bash
       python -m venv venv
       source venv/bin/activate  # On Windows use `venv\Scripts\activate`
       pip install -r requirements.txt
       ```

   c.  **Run the Flask backend server:**
       The main Flask application file might be `app/api.py` or similar (please verify the exact file name in your project structure).
       Assuming the main file is `api.py` inside an `app` directory:
       ```bash
       python app/api.py 
       ```
       By default, the Flask server will run on `http://localhost:5000`. You should see output in the terminal indicating the server is running.

### 4. Frontend Setup (React)
The frontend is a React application that consumes the backend APIs.

   d.  **Navigate to the `frontend` directory:**
       From the root directory of the project, change to the frontend directory:
       ```bash
       cd frontend
       ```

   e.  **Install frontend dependencies:**
       ```bash
       npm install
       ```

   f.  **Run the React development server:**
       ```bash
       npm start
       ```
       This command will start the React development server, typically on `http://localhost:3000`. It should automatically open the application in your default web browser.

### 5. Accessing the Application
   g.  Once both the backend and frontend servers are running, open your web browser and navigate to:
       ```
       http://localhost:3000
       ```
       You should see the React application, which will make requests to the Flask backend running on port 5000.

### Stopping the Servers
*   To stop the React development server, go to the terminal where it's running and press `Ctrl+C`.
*   To stop the Flask backend server, go to its terminal and press `Ctrl+C`.
*   If you used a Python virtual environment, you can deactivate it by typing `deactivate`.
