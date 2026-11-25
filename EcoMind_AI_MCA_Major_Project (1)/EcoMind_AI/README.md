# EcoMind AI — Intelligent Environment Monitoring & Sustainability Recommendation System

MCA Semester III major-project starter implementation. EcoMind records environmental measurements, summarizes trends, and produces sustainability recommendations. It can use Google Gemini for generated analysis when an API key is configured; otherwise it provides transparent local rule-based suggestions.

## Features
- Dashboard with recent readings and average indicators
- Add readings for temperature, humidity, air quality, water use and energy use
- Recommendation page with a Gemini-powered analysis option
- Local recommendation fallback, so the application works without an API key
- SQLite database created automatically with sample data
- JSON endpoint at `/api/readings`

## Technology
Python 3.10+, Flask, SQLite, HTML/CSS, JavaScript, Chart.js (CDN), Google Gemini API (optional).

## Run on Windows
1. Install Python 3.10 or newer.
2. Extract the ZIP and open a terminal in the `EcoMind_AI` folder.
3. Create and activate a virtual environment:
   ```powershell
   py -m venv venv
   .\\venv\\Scripts\\activate
   ```
4. Install packages:
   ```powershell
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env`. Add a Gemini API key to `GEMINI_API_KEY` if available. The app works without it.
6. Start:
   ```powershell
   python app.py
   ```
7. Open `http://127.0.0.1:5000` in your browser.

## Project structure
```
EcoMind_AI/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── ecomind.db             # generated on first run
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── add.html
│   ├── recommendations.html
│   └── about.html
└── static/
    └── style.css
```

## Important academic notes
- The included readings are sample/demo data, not live sensor measurements.
- Entering measurements manually demonstrates the monitoring workflow. Hardware sensors (ESP32/Arduino + suitable calibrated sensors) can be added as a future enhancement.
- Gemini analysis is optional and requires an API key and internet access. Do not commit your `.env` file or share API keys.
- Thresholds in the local recommendation logic are illustrative project rules, not official environmental or health limits.
- Before submission, run the application, add your own test data, take screenshots, and adapt the report/presentation to your university's prescribed format. Be ready to explain each module and the AI integration.
