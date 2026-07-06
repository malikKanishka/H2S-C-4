# FanPulse

A GenAI-enabled stadium operations platform built for the Hack2Skill Prompt Wars.

## Running the Application
1. Install requirements: `pip install -r requirements.txt`
2. Create `.env` from `.env.example` and set `GEMINI_API_KEY`.
3. Run `python app.py`. This will automatically initialize and seed the SQLite database.
4. Access the API at `http://localhost:5000/api/*` and the Operations Dashboard at `http://localhost:5000/dashboard`.
