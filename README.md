# Rhythm – Focus, Tasks, and Mindfulness

Rhythm is a lightweight Flask web app that combines a focus timer, simple task management, journaling with sentiment analysis, and mindfulness tools (including a proper 4-7-8 breathing guide).

## Working demo
https://drive.google.com/file/d/1REUu2x-Dk8Uf3STc9_RkBnhBAFH53adf/view?usp=drive_link

## Quick Start

### Prerequisites
- Python 3.9+
- pip

### Install
```bash
# from the project root
pip install -r requirements.txt
```

### Run
```bash
python app.py
```
The app starts on `http://127.0.0.1:5000`.

## Features
- Focus timer with Work/Break/Long Break modes
- Task list with:
  - Search-as-you-type
  - Filter by cognitive load (All/High/Medium/Low)
  - Add new tasks via + button
  - Delete tasks with a small transparent button on each row
  - Click to select a task for the timer
- Journal with TextBlob-based sentiment analysis
- Daily synthesis summarizing your activity patterns
- Mindfulness tools:
  - Daily tips
  - 4-7-8 breathing exercise with accurate per-second countdown
- Light/Dark theme with top-right toggle (preference persists)
- Customizable focus timer minutes per mode (persists per mode)

## Project Structure
```
AI-PM app/
├─ app.py            # Flask app + HTML/CSS/JS (render_template_string)
├─ requirements.txt  # Python dependencies
└─ README.md
```

## API Reference
Base URL: `http://127.0.0.1:5000`

- GET `/api/tasks`
  - Response: `{ "tasks": [{ id, title, source, cognitive_load }] }`

- POST `/api/tasks`
  - Body: `{ "title": string, "source": string (optional), "cognitive_load": "High"|"Medium"|"Low" }`
  - Response: `201 { status: "success", task }`

- DELETE `/api/tasks/:id`
  - Response: `200 { status: "success", deleted_id }` or `404` if not found

- POST `/api/log_activity`
  - Body: `{ "activity": string }`
  - Logs a user activity for synthesis

- POST `/api/sentiment`
  - Body: `{ "text": string }`
  - Response: `{ polarity: number, subjectivity: number }`

- GET `/api/mindfulness_tip`
  - Response: `{ tip, time_period, timestamp }`

- POST `/api/breathing_exercise`
  - Body: `{ type: "4-7-8" | "box" | "calm" }`
  - Response: meta for the breathing exercise used by the UI

- POST `/api/synthesis`
  - Body: `{ activities: [{ timestamp, activity }] }`
  - Response: `{ summary: string }`

## Using the App
- Tasks: type in the search box to filter; use the dropdown to filter by load; click `+` to add a task; click the small 🗑️ to delete; click a task row (not the buttons) to select it.
- Timer: Start/Pause/Reset. Completing a timer logs a Flow Block with the selected task and energy. You can set custom minutes per mode via the "Set minutes" field; values persist.
- Journal: Write a note and click Analyze Sentiment. The result logs polarity for synthesis.
- Mindfulness: Get a tip or start the breathing exercise. The 4-7-8 timer shows a per-second countdown through each step.
- Theme: Use the top-right toggle to switch between light and dark. Preference persists locally.

## Images
<img width="1951" height="2005" alt="image" src="https://github.com/user-attachments/assets/fa411c56-5b54-4fa7-9a40-0796a4a87308" />


## Development Notes
- All data is in-memory; restarting the server resets tasks and logs.
- The app starts with no tasks by default.
- Frontend is embedded in `app.py` via `render_template_string` for simplicity.
- TextBlob uses pretrained rules; no external model download is required.

## Troubleshooting
- If port 5000 is busy, stop the other process or set `FLASK_RUN_PORT`.
- If TextBlob is missing, ensure `pip install -r requirements.txt` ran without errors.
- Git push rejected (behind remote): `git fetch origin && git pull --rebase origin main` then resolve conflicts and `git push`.
- Cannot connect to GitHub over HTTPS: check network/proxy; consider switching to SSH remote.

## License
MIT
