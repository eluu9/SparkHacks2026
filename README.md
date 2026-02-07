# KartWise - AI Shopping Chatbot

KartWise is an AI-powered shopping assistant that generates personalized product kits based on user prompts. It uses a multi-step agentic pipeline to clarify requests, create structured shopping kits, and find products.

This is a hackathon submission for **SparkHacks 2026** at UIC.

## How It Works

LAB uses a multi-step agentic pipeline powered by LLaMA 3.3 70B (via Groq):

1. **Clarification Gate** -- Decides if the request is too vague. If so, asks 1-3 follow-up questions. If the user has already provided budget or context, this step is skipped.
2. **Kit Generation** -- Produces a structured shopping kit with categorized sections: Essential Items, Safety/PPE, Optional Upgrades, Budget-Friendly Alternatives, and Frequently Forgotten Items.
3. **Query Building** -- Constructs optimized search queries from each item's name, specs, and synonyms.
4. **Product Search** -- Hits the Serper API (Google Shopping) to find real products. Results are cached in MongoDB with a 24-hour TTL.
5. **Match & Rank** -- Fuzzy string matching scores and ranks search results against kit items. The best match's image, price, and buy link are attached to each item.

The frontend is a chat interface. Users send messages, receive either clarifying questions or a rendered product card grid, and can browse past sessions in a sidebar.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask, Python |
| Database | MongoDB (Flask-PyMongo) |
| Auth | Firebase Auth (Google + email/password) |
| LLM | Groq (LLaMA 3.3 70B) |
| Product Search | Serper API (Google Shopping) |
| Frontend | Bootstrap 5, vanilla JS |

## Prerequisites

- Python 3.10+
- MongoDB (local instance or Atlas)
- API keys for: [Groq](https://console.groq.com/), [Serper](https://serper.dev/), [Firebase](https://console.firebase.google.com/)
- A Firebase service account key file (`firebase-key.json`)

## Installation

### Automated (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

This creates a virtual environment, installs all dependencies, and verifies project files.

### Manual

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```
FLASK_APP=wsgi.py
FLASK_DEBUG=1
SECRET_KEY=your-secret-key

MONGO_URI=mongodb://localhost:27017/ai_shopping_kit

FIREBASE_CREDENTIALS=firebase-key.json

GROQ_API_KEY=your-groq-api-key
GROQ_MODEL_NAME=llama-3.3-70b-versatile

SERPER_API_KEY=your-serper-api-key
```

Place your Firebase service account JSON as `firebase-key.json` in the project root.

## Usage

Start the server:

```bash
python wsgi.py
```

The app runs at `http://localhost:5000`.

1. Sign in with Google or create an account with email/password.
2. Type a prompt describing what you want, e.g. *"$200 home office setup"* or *"cozy winter fit under $100"*.
3. Answer any follow-up questions if the system needs clarification.
4. Browse the generated product kit -- each card shows an image, price, and a link to buy.
5. Past sessions are saved in the sidebar for quick access.

## Project Structure

```
wsgi.py                          # Entry point
app/
  __init__.py                    # Flask app factory
  extensions.py                  # Mongo, Flask-Login, Firebase init
  config.json                    # Groq model config
  models/user.py                 # User model (Firebase UID-based)
  routes/
    auth.py                      # Login, signup, logout, session
    main.py                      # Root redirect, dashboard
    kit.py                       # /api/kit/generate, /api/kit/history
  services/
    orchestrator.py              # Agentic pipeline coordinator
    planner_service.py           # Clarification gate (LLM)
    kit_service.py               # Kit generation (LLM)
    query_service.py             # Search query builder
    search_service.py            # Serper API + caching
    match_service.py             # Fuzzy match & ranking
    llm_service.py               # Groq LLM client + retry logic
    prompts/                     # System prompts for LLM agents
  schemas/                       # JSON schemas for LLM output validation
  templates/                     # Jinja2 HTML templates
  static/js/main.js              # Frontend chat logic
normalization.py                 # String normalization for matching
Dockerfile                       # Container build for Aedify/cloud deploy
```

## Deploying to Aedify.ai

This project includes a Dockerfile and is ready to deploy on [Aedify.ai](https://aedify.ai/).

1. Push the repo to GitHub.
2. Go to [Aedify.ai](https://aedify.ai/) and click **Deploy App** > **Deploy from GitHub**.
3. Select your repository. Aedify will detect the Dockerfile automatically -- check **"Use Dockerfile"** in the Detection section.
4. Set these **environment variables** in the Aedify project settings (or use "Import .env"):

   | Variable | Value |
   |----------|-------|
   | `SECRET_KEY` | A strong random string |
   | `MONGO_URI` | Your MongoDB Atlas connection string |
   | `FIREBASE_CREDENTIALS_JSON` | The full contents of your `firebase-key.json` file, pasted as a single-line JSON string |
   | `GROQ_API_KEY` | Your Groq API key |
   | `SERPER_API_KEY` | Your Serper API key |

5. Set resources (0.5 vCPU / 512 MB minimum recommended).
6. Click **Deploy Project**.

The app will build and be accessible at the URL Aedify assigns. No `PORT` configuration needed -- the Dockerfile reads it automatically.

> **Note:** For Firebase credentials, copy the entire contents of `firebase-key.json` and paste it as the value of `FIREBASE_CREDENTIALS_JSON`. The container writes it to a file at startup.