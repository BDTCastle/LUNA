# LUNA

**LUNA Cares for You**

# L.U.N.A. - Lifestyle Utility & Nurturing Assistant

## Project Overview
Note to self: L.U.N.A. is my hackathon project to create a nurturing companion app that suggests daily outfits based on weather, with personalized, toggleable nudges to make users feel cared for. It uses FastAPI, PostgreSQL, and OpenWeatherMap to deliver a seamless experience.

## Features
- **User Authentication**: Sign up and log in securely with JWT tokens (`/signup`, `/login`).
- **Weather-Based Outfit Recommendations**: Get personalized outfit suggestions based on city weather and gender preferences (`/recommendation`).
- **Toggleable Nudges**: Receive optional, nurturing reminders (Whispers) with recommendations, saved to the database if enabled (`/nudges`, `/preferences`).
- **Nudge History**: View past recommendations to revisit L.U.N.A.’s advice (`GET /nudges`).

## Tech Stack
- **Backend**: FastAPI (Python) for API routes and logic.
- **Database**: PostgreSQL with SQLModel for user and nudge data.
- **Authentication**: python-jose for JWT tokens, passlib for password hashing.
- **External API**: OpenWeatherMap for real-time weather data.
- **Containerization**: Docker for consistent development and deployment.

## Setup Instructions
Note to self: These are the steps to run L.U.N.A. locally. Make sure Docker is installed!

1. Clone the repository:
   ```bash
   git clone https://github.com/BDTCastle/luna.git
   cd luna