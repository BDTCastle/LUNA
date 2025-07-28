L.U.N.A. - Lifestyle Utility & Nurturing Assistant

LUNA Cares for You

What Is This Thing?
This is my project for the Boot.dev 2025 Hackathon. The idea was to build a "reverse giga pet"—an app that takes care of you instead of the other way around.

L.U.N.A. is a backend API that acts as a sassy and supportive companion. It checks the weather for my location and gives me a personalized outfit recommendation for the day. The coolest part is the background scheduler I built that allows L.U.N.A. to be proactive, creating these little bits of advice (which I call "Whispers") automatically.

What It Does (The Features)

Secure User Accounts: I built a full signup and login system using JWTs so every user's data is private(This was hard as hell and it made my head hurt).

Sassy Outfit Recommendations: The core feature. It checks the real-time weather for a user's location and generates a personalized, supportive (and a little sassy) outfit suggestion.

User Preferences: Users can set their default location so they don't have to enter it every time.

Proactive Nudges: This was the fun part. I added a background scheduler (APScheduler) that automatically runs a job to create a "Whisper" for users who want them. It proves the app can think for itself(This was actually easier than I thought it was going to be, the advanced python scheduler documentation was really thorough and easy to adapt).

How I Built It (The Tech Stack)

Here's the tech stack I used to bring L.U.N.A. to life:

Backend: Python with FastAPI

Database: PostgreSQL with SQLModel (as the ORM)(This was so complicated, I thought I would never get it working)

Authentication: passlib for password hashing and python-jose for JWTs

External APIs: OpenWeatherMap for real-time weather

Containerization: Docker, to make sure it runs anywhere(this was a godsend recommendation from google)

How to Run It
Note to Judges: Running this should be super easy, as long as you have Docker installed!

Clone the Repository:
git clone https://github.com/BDTCastle/luna.git
cd luna

Run with Docker:
docker compose up --build -d

The API will be available at http://localhost:8000.

How to Use the API
Here's a quick guide on how to use the main endpoints with cURL.

Sign Up a New User
curl -X POST -H "Content-Type: application/json" -d '{"email": "test@example.com", "password": "a_secure_password", "location": "Tokyo"}' "http://localhost:8000/signup"

Log In to Get a Token
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "username=test@example.com&password=a_secure_password" "http://localhost:8000/login"
You'll need to copy the access_token from the response for the next steps.

Update Your Location
curl -X PATCH -H "Authorization: Bearer YOUR_TOKEN_HERE" -H "Content-Type: application/json" -d '{"location": "New York"}' "http://localhost:8000/preferences"

Get a Recommendation
curl -X GET -H "Authorization: Bearer YOUR_TOKEN_HERE" "http://localhost:8000/recommendation"

Check for Automatic Nudges
Wait a minute for the scheduler to run, then check for any Whispers L.U.N.A. created for you.
curl -X GET -H "Authorization: Bearer YOUR_TOKEN_HERE" "http://localhost:8000/nudges"