import os, json, sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv
import requests

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "ecomind-development-key")
DB_PATH = os.path.join(os.path.dirname(__file__), "ecomind.db")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL, temperature REAL NOT NULL,
            humidity REAL NOT NULL, air_quality REAL NOT NULL,
            water_usage REAL NOT NULL, energy_usage REAL NOT NULL,
            created_at TEXT NOT NULL
        )""")
        count = con.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
        if count == 0:
            samples = [
                ("Campus Block A", 29.4, 58, 72, 420, 18.5, "2026-11-20 09:00"),
                ("Campus Block B", 31.2, 62, 118, 510, 23.0, "2026-11-21 09:00"),
                ("Library", 26.8, 55, 48, 280, 12.2, "2026-11-22 09:00"),
                ("Computer Lab", 30.1, 49, 96, 350, 31.5, "2026-11-23 09:00"),
                ("Cafeteria", 28.7, 67, 135, 620, 20.1, "2026-11-24 09:00"),
            ]
            con.executemany("""INSERT INTO readings
                (location, temperature, humidity, air_quality, water_usage, energy_usage, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""", samples)

def local_recommendations(r):
    tips = []
    if r["air_quality"] > 100:
        tips.append("Air quality needs attention: improve ventilation, check filters, and reduce indoor pollutant sources.")
    elif r["air_quality"] > 75:
        tips.append("Monitor air quality and maintain ventilation during busy periods.")
    else:
        tips.append("Air quality is currently in a comparatively good range; continue routine monitoring.")
    if r["energy_usage"] > 25:
        tips.append("Energy use is high: switch off idle equipment, use power-saving settings, and review HVAC schedules.")
    else:
        tips.append("Energy use looks moderate; continue using efficient lighting and equipment.")
    if r["water_usage"] > 500:
        tips.append("Water use is high: inspect for leaks, install low-flow fixtures, and track peak-use periods.")
    else:
        tips.append("Water use is moderate; continue checking taps and recording daily consumption.")
    if r["temperature"] > 30:
        tips.append("Temperature is elevated: check cooling efficiency, shading, and occupancy-based cooling.")
    return tips

def get_ai_advice(reading):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    prompt = (
        "You are EcoMind, an environmental sustainability analyst. Analyze these "
        "environmental readings and provide: (1) a brief status summary, (2) three "
        "practical, prioritized recommendations, and (3) one measurable follow-up "
        "metric. Avoid claiming regulatory compliance. Readings: " + json.dumps(dict(reading))
    )
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + api_key
        response = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=20)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None

@app.route("/")
def index():
    with db() as con:
        readings = con.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 8").fetchall()
        total = con.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
        averages = con.execute("""SELECT AVG(temperature) t, AVG(air_quality) a,
            AVG(water_usage) w, AVG(energy_usage) e FROM readings""").fetchone()
    latest = readings[0] if readings else None
    return render_template("index.html", readings=readings, total=total, averages=averages, latest=latest)

@app.route("/add", methods=["GET", "POST"])
def add_reading():
    if request.method == "POST":
        try:
            values = (
                request.form["location"].strip(),
                float(request.form["temperature"]),
                float(request.form["humidity"]),
                float(request.form["air_quality"]),
                float(request.form["water_usage"]),
                float(request.form["energy_usage"]),
                datetime.now().strftime("%Y-%m-%d %H:%M")
            )
            if not values[0] or any(v < 0 for v in values[1:6]):
                raise ValueError("Enter a location and non-negative measurements.")
            with db() as con:
                con.execute("""INSERT INTO readings
                    (location, temperature, humidity, air_quality, water_usage, energy_usage, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""", values)
            flash("Environmental reading saved successfully.", "success")
            return redirect(url_for("index"))
        except (ValueError, KeyError):
            flash("Please enter valid numeric values for every measurement.", "error")
    return render_template("add.html")

@app.route("/recommendations/<int:reading_id>")
def recommendations(reading_id):
    with db() as con:
        reading = con.execute("SELECT * FROM readings WHERE id=?", (reading_id,)).fetchone()
    if not reading:
        flash("Reading not found.", "error")
        return redirect(url_for("index"))
    ai_advice = get_ai_advice(reading)
    tips = local_recommendations(reading)
    return render_template("recommendations.html", reading=reading, ai_advice=ai_advice, tips=tips)

@app.route("/api/readings")
def api_readings():
    with db() as con:
        rows = con.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 30").fetchall()
    return jsonify([dict(row) for row in rows])

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
