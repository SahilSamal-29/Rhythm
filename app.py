from flask import Flask, request, jsonify, render_template_string
import datetime
from textblob import TextBlob

app = Flask(__name__)

# --- In-memory storage ---
user_activity_log = []
mock_tasks = [
    {"id": 1, "title": "Write report", "source": "Work", "cognitive_load": "High"},
    {"id": 2, "title": "Read articles", "source": "Learning", "cognitive_load": "Medium"},
    {"id": 3, "title": "Check emails", "source": "Communication", "cognitive_load": "Low"},
]

# --- API Endpoints ---

@app.route('/')
def index():
    """Serves the main HTML file for the application."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Simulates fetching tasks from integrated services."""
    return jsonify({"tasks": mock_tasks})

@app.route('/api/log_activity', methods=['POST'])
def log_activity():
    """Logs user activities for the daily synthesis."""
    activity = request.json.get('activity')
    if activity:
        timestamp = datetime.datetime.now().isoformat()
        user_activity_log.append({"timestamp": timestamp, "activity": activity})
        return jsonify({"status": "success", "logged": activity}), 200
    return jsonify({"status": "error", "message": "No activity provided"}), 400

@app.route('/api/sentiment', methods=['POST'])
def analyze_sentiment():
    """
    Analyzes the sentiment of a given text using TextBlob.
    Returns polarity and subjectivity.
    """
    text_to_analyze = request.json.get('text', '')
    if not text_to_analyze:
        return jsonify({"error": "No text provided"}), 400

    blob = TextBlob(text_to_analyze)
    sentiment = {
        "polarity": round(blob.sentiment.polarity, 2),
        "subjectivity": round(blob.sentiment.subjectivity, 2)
    }
    
    # Log this activity
    timestamp = datetime.datetime.now().isoformat()
    user_activity_log.append({"timestamp": timestamp, "activity": f"Wrote a journal entry with polarity: {sentiment['polarity']}"})

    return jsonify(sentiment)

@app.route('/api/synthesis', methods=['POST'])
def generate_synthesis():
    activities = request.json.get('activities', [])

    if not activities:
        return jsonify({"summary": "No activity was logged today. Start a Flow Block or write a journal entry to see your synthesis."})

    flow_blocks = [a for a in activities if "Flow Block" in a['activity']]
    journal_entries = [a for a in activities if "journal entry" in a['activity']]

    high_energy_tasks = sum(1 for a in flow_blocks if "High" in a['activity'])
    medium_energy_tasks = sum(1 for a in flow_blocks if "Medium" in a['activity'])
    low_energy_tasks = sum(1 for a in flow_blocks if "Low" in a['activity'])

    summary_parts = []
    summary_parts.append("Here is your synthesis for today:")

    if flow_blocks:
        total_tasks = len(flow_blocks)
        summary_parts.append(f"\n\n- *Productivity*: You powered through {total_tasks} focus session{'s' if total_tasks > 1 else ''}. This included {high_energy_tasks} high-energy, {medium_energy_tasks} medium-energy, and {low_energy_tasks} low-energy tasks. Your dedication to deep work is clear.")
    
    if journal_entries:
        polarities = [float(a['activity'].split(': ')[-1]) for a in journal_entries if ': ' in a['activity']]
        avg_polarity = sum(polarities) / len(polarities) if polarities else 0
        
        sentiment_adjective = "positive"
        if avg_polarity < -0.1:
            sentiment_adjective = "challenging"
        elif avg_polarity <= 0.1:
            sentiment_adjective = "neutral"
            
        summary_parts.append(f"\n- *Well-being*: You took time for reflection. Your journal entries indicate a generally {sentiment_adjective} mindset today (average sentiment: {avg_polarity:.2f}).")

    if high_energy_tasks > 2:
        recommendation = "You tackled some major tasks today. Consider starting tomorrow with a medium-energy task to ease into your day."
    else:
        recommendation = "It was a balanced day. Tomorrow looks like a great opportunity to tackle a high-energy task in the morning when your focus is at its peak."
        
    summary_parts.append(f"\n\n- *Recommendation*: {recommendation}")

    return jsonify({"summary": "".join(summary_parts)})

# --- 2. FRONTEND (HTML Template) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Rhythm</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        h1 {
            text-align: center;
            color: white;
            font-size: 3rem;
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .timer-section {
            text-align: center;
        }
        
        .timer-display {
            font-size: 4rem;
            font-weight: bold;
            color: #667eea;
            margin: 1rem 0;
        }
        
        .timer-controls {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin: 1rem 0;
        }
        
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        button:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .task-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .task-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            border: 1px solid #eee;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .task-item:hover {
            background: #f8f9ff;
            border-color: #667eea;
        }
        
        .task-item.selected {
            background: #667eea;
            color: white;
        }
        
        .task-info h3 {
            margin-bottom: 0.5rem;
        }
        
        .task-meta {
            font-size: 0.9rem;
            color: #666;
        }
        
        .task-item.selected .task-meta {
            color: rgba(255,255,255,0.8);
        }
        
        .cognitive-load {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .cognitive-load.High {
            background: #ff6b6b;
            color: white;
        }
        
        .cognitive-load.Medium {
            background: #ffd93d;
            color: #333;
        }
        
        .cognitive-load.Low {
            background: #6bcf7f;
            color: white;
        }
        
        .journal-section {
            grid-column: 1 / -1;
        }
        
        .journal-textarea {
            width: 100%;
            height: 120px;
            padding: 1rem;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-family: inherit;
            font-size: 1rem;
            resize: vertical;
        }
        
        .synthesis-section {
            grid-column: 1 / -1;
            background: #f8f9ff;
        }
        
        .synthesis-content {
            white-space: pre-line;
            line-height: 1.6;
        }
        
        .mode-selector {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-bottom: 1rem;
        }
        
        .mode-btn {
            background: transparent;
            border: 2px solid white;
            color: white;
        }
        
        .mode-btn.active {
            background: white;
            color: #667eea;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .timer-display {
                font-size: 3rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Rhythm</h1>
        
        <div class="mode-selector">
            <button class="mode-btn active" data-mode="work">Work</button>
            <button class="mode-btn" data-mode="break">Break</button>
            <button class="mode-btn" data-mode="long-break">Long Break</button>
        </div>
        
        <div class="main-content">
            <div class="card timer-section">
                <h2>Focus Timer</h2>
                <div class="timer-display" id="timerDisplay">25:00</div>
                <div class="timer-controls">
                    <button id="startBtn">Start</button>
                    <button id="pauseBtn" disabled>Pause</button>
                    <button id="resetBtn">Reset</button>
                </div>
                <div id="currentTask" style="margin-top: 1rem; font-style: italic; color: #666;"></div>
            </div>
            
            <div class="card">
                <h2>Tasks</h2>
                <div class="task-list" id="taskList">
                    <!-- Tasks will be loaded here -->
                </div>
            </div>
            
            <div class="card journal-section">
                <h2>Journal Entry</h2>
                <textarea class="journal-textarea" id="journalText" placeholder="How are you feeling? What's on your mind?"></textarea>
                <div style="margin-top: 1rem;">
                    <button id="analyzeSentiment">Analyze Sentiment</button>
                    <button id="saveJournal">Save Entry</button>
                </div>
                <div id="sentimentResult" style="margin-top: 1rem; padding: 1rem; background: #f0f0f0; border-radius: 8px; display: none;"></div>
            </div>
            
            <div class="card synthesis-section">
                <h2>Daily Synthesis</h2>
                <button id="generateSynthesis" style="margin-bottom: 1rem;">Generate Today's Summary</button>
                <div id="synthesisContent" class="synthesis-content">
                    Click "Generate Today's Summary" to see your daily synthesis.
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const state = {
                tasks: [],
                selectedTask: null,
                timerInterval: null,
                timeLeft: 25 * 60,
                isTimerRunning: false,
                currentMode: 'work',
                activities: []
            };

            // DOM elements
            const timerDisplay = document.getElementById('timerDisplay');
            const startBtn = document.getElementById('startBtn');
            const pauseBtn = document.getElementById('pauseBtn');
            const resetBtn = document.getElementById('resetBtn');
            const taskList = document.getElementById('taskList');
            const currentTaskDiv = document.getElementById('currentTask');
            const journalText = document.getElementById('journalText');
            const analyzeSentimentBtn = document.getElementById('analyzeSentiment');
            const saveJournalBtn = document.getElementById('saveJournal');
            const sentimentResult = document.getElementById('sentimentResult');
            const generateSynthesisBtn = document.getElementById('generateSynthesis');
            const synthesisContent = document.getElementById('synthesisContent');
            const modeBtns = document.querySelectorAll('.mode-btn');

            // Timer modes
            const modes = {
                work: 25 * 60,
                break: 5 * 60,
                'long-break': 15 * 60
            };

            // Initialize
            const init = () => {
                loadTasks();
                updateTimerDisplay();
                setupEventListeners();
            };

            // Load tasks from API
            const loadTasks = () => {
                fetch('/api/tasks')
                    .then(res => res.json())
                    .then(data => {
                        state.tasks = data.tasks;
                        renderTasks();
                    })
                    .catch(err => console.error('Error loading tasks:', err));
            };

            // Render tasks
            const renderTasks = () => {
                taskList.innerHTML = '';
                state.tasks.forEach(task => {
                    const taskElement = document.createElement('div');
                    taskElement.className = 'task-item';
                    taskElement.innerHTML = `
                        <div class="task-info">
                            <h3>${task.title}</h3>
                            <div class="task-meta">
                                ${task.source} • <span class="cognitive-load ${task.cognitive_load}">${task.cognitive_load}</span>
                            </div>
                        </div>
                    `;
                    taskElement.addEventListener('click', () => selectTask(task));
                    taskList.appendChild(taskElement);
                });
            };

            // Select task
            const selectTask = (task) => {
                // Remove previous selection
                document.querySelectorAll('.task-item').forEach(item => {
                    item.classList.remove('selected');
                });
                
                // Add selection to clicked task
                event.currentTarget.classList.add('selected');
                state.selectedTask = task;
                currentTaskDiv.textContent = `Selected: ${task.title}`;
            };

            // Timer functions
            const updateTimerDisplay = () => {
                const minutes = Math.floor(state.timeLeft / 60);
                const seconds = state.timeLeft % 60;
                timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            };

            const startTimer = () => {
                if (state.isTimerRunning) return;
                
                state.isTimerRunning = true;
                state.timerInterval = setInterval(() => {
                    state.timeLeft--;
                    updateTimerDisplay();
                    
                    if (state.timeLeft <= 0) {
                        completeTimer();
                    }
                }, 1000);
                
                startBtn.disabled = true;
                pauseBtn.disabled = false;
            };

            const pauseTimer = () => {
                state.isTimerRunning = false;
                clearInterval(state.timerInterval);
                startBtn.disabled = false;
                pauseBtn.disabled = true;
            };

            const resetTimer = () => {
                state.isTimerRunning = false;
                clearInterval(state.timerInterval);
                state.timeLeft = modes[state.currentMode];
                updateTimerDisplay();
                startBtn.disabled = false;
                pauseBtn.disabled = true;
            };

            const completeTimer = () => {
                state.isTimerRunning = false;
                clearInterval(state.timerInterval);
                startBtn.disabled = false;
                pauseBtn.disabled = true;
                
                // Log activity
                const activity = `Flow Block completed: ${state.selectedTask ? state.selectedTask.title : 'No task selected'} (${state.currentMode} mode)`;
                logActivity(activity);
                
                alert('Timer completed! Great work!');
                resetTimer();
            };

            // Mode switching
            const switchMode = (mode) => {
                if (state.isTimerRunning) {
                    if (!confirm('Timer is running. Switch mode and reset timer?')) return;
                }
                
                state.currentMode = mode;
                state.timeLeft = modes[mode];
                updateTimerDisplay();
                
                // Update mode buttons
                modeBtns.forEach(btn => {
                    btn.classList.remove('active');
                    if (btn.dataset.mode === mode) {
                        btn.classList.add('active');
                    }
                });
            };

            // Activity logging
            const logActivity = (activity) => {
                fetch('/api/log_activity', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ activity })
                })
                .then(res => res.json())
                .then(data => {
                    console.log('Activity logged:', data);
                    state.activities.push({ activity, timestamp: new Date().toISOString() });
                })
                .catch(err => console.error('Error logging activity:', err));
            };

            // Sentiment analysis
            const analyzeSentiment = () => {
                const text = journalText.value.trim();
                if (!text) {
                    alert('Please enter some text to analyze.');
                    return;
                }

                fetch('/api/sentiment', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text })
                })
                .then(res => res.json())
                .then(data => {
                    sentimentResult.style.display = 'block';
                    sentimentResult.innerHTML = `
                        <strong>Sentiment Analysis:</strong><br>
                        Polarity: ${data.polarity} (${data.polarity > 0.1 ? 'Positive' : data.polarity < -0.1 ? 'Negative' : 'Neutral'})<br>
                        Subjectivity: ${data.subjectivity} (${data.subjectivity > 0.5 ? 'Subjective' : 'Objective'})
                    `;
                })
                .catch(err => console.error('Error analyzing sentiment:', err));
            };

            // Save journal entry
            const saveJournal = () => {
                const text = journalText.value.trim();
                if (!text) {
                    alert('Please enter some text to save.');
                    return;
                }

                logActivity(`Wrote a journal entry: ${text.substring(0, 50)}...`);
                journalText.value = '';
                sentimentResult.style.display = 'none';
                alert('Journal entry saved!');
            };

            // Generate synthesis
            const generateSynthesis = () => {
                fetch('/api/synthesis', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ activities: state.activities })
                })
                .then(res => res.json())
                .then(data => {
                    synthesisContent.textContent = data.summary;
                })
                .catch(err => console.error('Error generating synthesis:', err));
            };

            // Event listeners
            const setupEventListeners = () => {
                startBtn.addEventListener('click', startTimer);
                pauseBtn.addEventListener('click', pauseTimer);
                resetBtn.addEventListener('click', resetTimer);
                
                modeBtns.forEach(btn => {
                    btn.addEventListener('click', () => switchMode(btn.dataset.mode));
                });
                
                analyzeSentimentBtn.addEventListener('click', analyzeSentiment);
                saveJournalBtn.addEventListener('click', saveJournal);
                generateSynthesisBtn.addEventListener('click', generateSynthesis);
            };

            // Initialize the app
            init();
        });
    </script>
</body>
</html>
"""

# --- 3. RUN THE APPLICATION ---

if __name__ == '__main__':
    app.run(debug=True)
