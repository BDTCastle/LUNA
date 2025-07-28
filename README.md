# L.U.N.A. - Lifestyle Utility & Nurturing Assistant

**LUNA Cares for You**

L.U.N.A. is a nurturing companion API that suggests daily outfits based on weather, with personalized, toggleable nudges to make users feel cared for. It uses FastAPI, PostgreSQL, and OpenWeatherMap to deliver a seamless experience. Built for the Boot.dev 2025 Hackathon.

## Features
- **User Authentication**: Sign up and log in securely with JWT tokens (`/signup`, `/login`).
- **Weather-Based Outfit Recommendations**: Get personalized outfit suggestions based on city weather (`/recommendation`).
- **Customizable Preferences**: Users can set their location and toggle features on or off (`/preferences`).
- **Nudge History**: View past recommendations to revisit L.U.N.A.’s advice (`GET /nudges`).

## Tech Stack
- **Backend**: FastAPI (Python) for API routes and logic.
- **Database**: PostgreSQL with SQLModel for user and nudge data.
- **Authentication**: `python-jose` for JWT tokens, `passlib` for password hashing.
- **External API**: OpenWeatherMap for real-time weather data.
- **Containerization**: Docker for consistent development and deployment.

## Setup Instructions
1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/BDTCastle/luna.git](https://github.com/BDTCastle/luna.git)
    cd luna
    ```
2.  **Run the Application**:
    ```bash
    sudo docker-compose up --build -d
    ```

## API Usage Guide

Here are examples of how to use the main endpoints with `cURL`.

### 1. Sign Up
Create a new user account.

```bash
curl -X POST "http://localhost:8000/signup" \
-H "Content-Type: application/json" \
-d '{"email": "test@example.com", "password": "a_secure_password", "location": "Tokyo"}'