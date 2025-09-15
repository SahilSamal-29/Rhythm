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

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Adds a new task to the in-memory list."""
    data = request.json or {}
    title = (data.get('title') or '').strip()
    source = (data.get('source') or '').strip() or 'Me'
    cognitive_load = (data.get('cognitive_load') or '').strip().capitalize() or 'Medium'

    if not title:
        return jsonify({"status": "error", "message": "Title is required"}), 400

    if cognitive_load not in {"High", "Medium", "Low"}:
        return jsonify({"status": "error", "message": "cognitive_load must be High, Medium, or Low"}), 400

    next_id = (max([t["id"] for t in mock_tasks]) + 1) if mock_tasks else 1
    new_task = {"id": next_id, "title": title, "source": source, "cognitive_load": cognitive_load}
    mock_tasks.append(new_task)
    return jsonify({"status": "success", "task": new_task}), 201

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

@app.route('/api/breathing_exercise', methods=['POST'])
def start_breathing_exercise():
    """Starts a guided breathing exercise."""
    exercise_type = request.json.get('type', '4-7-8')
    
    exercises = {
        '4-7-8': {
            'name': '4-7-8 Breathing',
            'description': 'Inhale for 4, hold for 7, exhale for 8',
            'cycles': 4,
            'instructions': [
                "Breathe in slowly through your nose for 4 counts",
                "Hold your breath for 7 counts", 
                "Exhale slowly through your mouth for 8 counts",
                "Repeat this cycle 4 times"
            ]
        },
        'box': {
            'name': 'Box Breathing',
            'description': 'Equal inhale, hold, exhale, hold',
            'cycles': 5,
            'instructions': [
                "Inhale for 4 counts",
                "Hold for 4 counts",
                "Exhale for 4 counts", 
                "Hold for 4 counts",
                "Repeat 5 times"
            ]
        },
        'calm': {
            'name': 'Calming Breath',
            'description': 'Slow, deep breathing for relaxation',
            'cycles': 6,
            'instructions': [
                "Take a slow, deep breath in for 5 counts",
                "Exhale slowly for 6 counts",
                "Focus on the rhythm of your breathing",
                "Repeat 6 times"
            ]
        }
    }
    
    exercise = exercises.get(exercise_type, exercises['4-7-8'])
    
    # Log this mindfulness activity
    timestamp = datetime.datetime.now().isoformat()
    user_activity_log.append({
        "timestamp": timestamp, 
        "activity": f"Completed {exercise['name']} breathing exercise"
    })
    
    return jsonify(exercise)

@app.route('/api/mindfulness_tip', methods=['GET'])
def get_mindfulness_tip():
    """Returns a personalized mindfulness tip based on time of day and recent activity."""
    current_hour = datetime.datetime.now().hour
    
    tips = {
        'morning': [
            "Start your day with gratitude. Write down three things you're grateful for.",
            "Take 5 deep breaths before checking your phone or email.",
            "Set an intention for your day. What do you want to focus on?",
            "Do a quick body scan - notice how you feel physically and emotionally."
        ],
        'afternoon': [
            "Take a mindful walk. Notice the sounds, smells, and sensations around you.",
            "Practice the 5-4-3-2-1 grounding technique: 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
            "Do a quick breathing exercise to reset your energy.",
            "Check in with yourself - how is your stress level? What do you need right now?"
        ],
        'evening': [
            "Reflect on one good thing that happened today.",
            "Practice progressive muscle relaxation before bed.",
            "Write down any worries or thoughts to clear your mind.",
            "Do a gentle stretching routine to release tension."
        ]
    }
    
    if current_hour < 12:
        time_period = 'morning'
    elif current_hour < 18:
        time_period = 'afternoon'
    else:
        time_period = 'evening'
    
    import random
    tip = random.choice(tips[time_period])
    
    return jsonify({
        "tip": tip,
        "time_period": time_period,
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/api/synthesis', methods=['POST'])
def generate_synthesis():
    activities = request.json.get('activities', [])

    if not activities:
        return jsonify({"summary": "No activity was logged today. Start a Flow Block, try a breathing exercise, or write a journal entry to see your synthesis."})

    flow_blocks = [a for a in activities if "Flow Block" in a['activity']]
    journal_entries = [a for a in activities if "journal entry" in a['activity']]
    breathing_exercises = [a for a in activities if "breathing exercise" in a['activity']]

    high_energy_tasks = sum(1 for a in flow_blocks if "High" in a['activity'])
    medium_energy_tasks = sum(1 for a in flow_blocks if "Medium" in a['activity'])
    low_energy_tasks = sum(1 for a in flow_blocks if "Low" in a['activity'])

    summary_parts = []
    summary_parts.append("Here is your synthesis for today:")

    if flow_blocks:
        total_tasks = len(flow_blocks)
        summary_parts.append(f"\n\n- *Productivity*: You powered through {total_tasks} focus session{'s' if total_tasks > 1 else ''}. This included {high_energy_tasks} high-energy, {medium_energy_tasks} medium-energy, and {low_energy_tasks} low-energy tasks. Your dedication to deep work is clear.")
    
    if breathing_exercises:
        summary_parts.append(f"\n- *Mindfulness*: Great job taking care of your mental well-being! You completed {len(breathing_exercises)} breathing exercise{'s' if len(breathing_exercises) > 1 else ''} today. This shows you're prioritizing both productivity and peace of mind.")
    
    if journal_entries:
        # Extract polarities from journal entries that have sentiment data
        polarities = []
        for entry in journal_entries:
            if 'polarity:' in entry['activity']:
                try:
                    # Extract polarity value from entries like "Wrote a journal entry with polarity: 0.5"
                    polarity_str = entry['activity'].split('polarity: ')[-1]
                    polarities.append(float(polarity_str))
                except (ValueError, IndexError):
                    continue
        
        avg_polarity = sum(polarities) / len(polarities) if polarities else 0
        
        sentiment_adjective = "positive"
        if avg_polarity < -0.1:
            sentiment_adjective = "challenging"
        elif avg_polarity <= 0.1:
            sentiment_adjective = "neutral"
            
        summary_parts.append(f"\n- *Well-being*: You took time for reflection. Your journal entries indicate a generally {sentiment_adjective} mindset today (average sentiment: {avg_polarity:.2f}).")

    # Enhanced AI recommendations based on activity patterns
    if high_energy_tasks > 2 and len(breathing_exercises) == 0:
        recommendation = "You tackled some major tasks today! Consider adding a breathing exercise to your routine to help manage stress and maintain balance."
    elif len(breathing_exercises) > 0 and high_energy_tasks == 0:
        recommendation = "You focused on mindfulness today. Tomorrow might be a great time to tackle a high-energy task while maintaining your calm mindset."
    elif high_energy_tasks > 2 and len(breathing_exercises) > 0:
        recommendation = "Excellent balance! You're successfully combining productivity with mindfulness. Keep up this integrated approach."
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
                <div style="display:flex; gap:0.5rem; margin-bottom:0.75rem; align-items:center;">
                    <input id="taskSearch" placeholder="Search tasks..." style="flex:1; padding:0.6rem 0.8rem; border:1px solid #333; background:#111; color:#eee; border-radius:8px;" />
                    <button id="addTaskBtn" title="Add task" style="width:42px; height:42px; display:flex; align-items:center; justify-content:center; font-size:1.2rem;">+</button>
                </div>
                <select id="loadFilter" style="width:100%; padding:0.6rem 0.8rem; border-radius:8px; margin-bottom:0.75rem;">
                    <option value="all">All Loads</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                </select>
                <div class="task-list" id="taskList"></div>
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
            
            <div class="card">
                <h2>Mindfulness</h2>
                <div style="margin-bottom: 1rem;">
                    <button id="getMindfulnessTip" style="margin-right: 0.5rem;">Get Daily Tip</button>
                    <button id="startBreathing">Breathing Exercise</button>
                </div>
                <div id="mindfulnessContent" style="padding: 1rem; background: #f8f9ff; border-radius: 8px; min-height: 100px;">
                    Click "Get Daily Tip" for personalized mindfulness advice.
                </div>
                <div id="breathingExercise" style="margin-top: 1rem; padding: 1rem; background: #e8f5e8; border-radius: 8px; display: none;">
                    <h3 id="breathingTitle"></h3>
                    <p id="breathingDescription"></p>
                    <div id="breathingInstructions"></div>
                    <div id="breathingTimer" style="font-size: 2rem; text-align: center; margin: 1rem 0; color: #2d5a2d;"></div>
                    <button id="startBreathingTimer" style="display: none;">Start Exercise</button>
                </div>
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
                activities: [],
                currentExercise: null,
                breathingTimerHandle: null,
                breathingStepInterval: null
            };

            // DOM elements
            const timerDisplay = document.getElementById('timerDisplay');
            const startBtn = document.getElementById('startBtn');
            const pauseBtn = document.getElementById('pauseBtn');
            const resetBtn = document.getElementById('resetBtn');
            const taskList = document.getElementById('taskList');
            const taskSearch = document.getElementById('taskSearch');
            const loadFilter = document.getElementById('loadFilter');
            const addTaskBtn = document.getElementById('addTaskBtn');
            const currentTaskDiv = document.getElementById('currentTask');
            const journalText = document.getElementById('journalText');
            const analyzeSentimentBtn = document.getElementById('analyzeSentiment');
            const saveJournalBtn = document.getElementById('saveJournal');
            const sentimentResult = document.getElementById('sentimentResult');
            const generateSynthesisBtn = document.getElementById('generateSynthesis');
            const synthesisContent = document.getElementById('synthesisContent');
            const modeBtns = document.querySelectorAll('.mode-btn');
            
            // Mindfulness elements
            const getMindfulnessTipBtn = document.getElementById('getMindfulnessTip');
            const startBreathingBtn = document.getElementById('startBreathing');
            const mindfulnessContent = document.getElementById('mindfulnessContent');
            const breathingExercise = document.getElementById('breathingExercise');
            const breathingTitle = document.getElementById('breathingTitle');
            const breathingDescription = document.getElementById('breathingDescription');
            const breathingInstructions = document.getElementById('breathingInstructions');
            const breathingTimer = document.getElementById('breathingTimer');
            const startBreathingTimerBtn = document.getElementById('startBreathingTimer');

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
                const query = (taskSearch.value || '').toLowerCase();
                const filter = loadFilter.value;

                const filtered = state.tasks.filter(t => {
                    const matchesQuery = t.title.toLowerCase().includes(query) || (t.source || '').toLowerCase().includes(query);
                    const matchesLoad = filter === 'all' ? true : t.cognitive_load === filter;
                    return matchesQuery && matchesLoad;
                });

                filtered.forEach(task => {
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
                    taskElement.addEventListener('click', (event) => selectTask(task, event));
                    taskList.appendChild(taskElement);
                });
            };

            // Select task
            const selectTask = (task, event) => {
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
                const energy = state.selectedTask ? state.selectedTask.cognitive_load : 'Unknown';
                const activity = `Flow Block completed: ${state.selectedTask ? state.selectedTask.title : 'No task selected'} (${state.currentMode} mode, ${energy} energy)`;
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
                    // Log activity with polarity so synthesis can use it
                    logActivity(`Wrote a journal entry with polarity: ${data.polarity}`);
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

            // Mindfulness functions
            const getMindfulnessTip = () => {
                fetch('/api/mindfulness_tip')
                    .then(res => res.json())
                    .then(data => {
                        mindfulnessContent.innerHTML = `
                            <strong>${data.time_period.charAt(0).toUpperCase() + data.time_period.slice(1)} Mindfulness Tip:</strong><br>
                            ${data.tip}
                        `;
                    })
                    .catch(err => console.error('Error getting mindfulness tip:', err));
            };

            const startBreathingExercise = () => {
                // Always use 4-7-8 per request
                const chosenType = '4-7-8';
                fetch('/api/breathing_exercise', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ type: chosenType })
                })
                .then(res => res.json())
                .then(data => {
                    breathingExercise.style.display = 'block';
                    breathingTitle.textContent = data.name;
                    breathingDescription.textContent = data.description;
                    breathingInstructions.innerHTML = data.instructions.map(instruction => 
                        `<div style="margin: 0.5rem 0;">• ${instruction}</div>`
                    ).join('');
                    startBreathingTimerBtn.style.display = 'inline-block';
                    breathingTimer.textContent = 'Ready to begin';
                    state.currentExercise = data;
                })
                .catch(err => console.error('Error starting breathing exercise:', err));
            };

            const startBreathingTimer = () => {
                const data = state.currentExercise;
                if (!data) {
                    alert('Please load the breathing exercise first.');
                    return;
                }

                // Configure durations per step in seconds
                // For 4-7-8: Inhale 4, Hold 7, Exhale 8
                const stepLabels = ['Inhale', 'Hold', 'Exhale'];
                const stepDurations = [4, 7, 8];
                const totalCycles = data.cycles || 4;

                // Cleanup any existing timers
                if (state.breathingTimerHandle) clearTimeout(state.breathingTimerHandle);
                if (state.breathingStepInterval) clearInterval(state.breathingStepInterval);

                startBreathingTimerBtn.disabled = true;
                startBreathingTimerBtn.textContent = 'In Progress...';

                let currentCycle = 1;
                let currentStepIndex = 0;

                const runStep = () => {
                    if (currentCycle > totalCycles) {
                        if (state.breathingStepInterval) clearInterval(state.breathingStepInterval);
                        breathingTimer.textContent = 'Exercise Complete! 🧘‍♀️';
                        startBreathingTimerBtn.disabled = false;
                        startBreathingTimerBtn.textContent = 'Start Again';
                        return;
                    }

                    const label = `${stepLabels[currentStepIndex]} (Cycle ${currentCycle}/${totalCycles})`;
                    let secondsLeft = stepDurations[currentStepIndex];
                    breathingTimer.textContent = `${label}: ${secondsLeft}s`;

                    if (state.breathingStepInterval) clearInterval(state.breathingStepInterval);
                    state.breathingStepInterval = setInterval(() => {
                        secondsLeft -= 1;
                        breathingTimer.textContent = `${label}: ${secondsLeft}s`;
                    }, 1000);

                    state.breathingTimerHandle = setTimeout(() => {
                        clearInterval(state.breathingStepInterval);
                        currentStepIndex += 1;
                        if (currentStepIndex >= stepLabels.length) {
                            currentStepIndex = 0;
                            currentCycle += 1;
                        }
                        runStep();
                    }, stepDurations[currentStepIndex] * 1000);
                };

                runStep();
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
                
                // Mindfulness event listeners
                getMindfulnessTipBtn.addEventListener('click', getMindfulnessTip);
                startBreathingBtn.addEventListener('click', startBreathingExercise);
                startBreathingTimerBtn.addEventListener('click', startBreathingTimer);

                // Task interactions
                taskSearch.addEventListener('input', renderTasks);
                loadFilter.addEventListener('change', renderTasks);
                addTaskBtn.addEventListener('click', async () => {
                    const title = prompt('Task title:');
                    if (!title) return;
                    const source = prompt('Source (e.g., me, work):', 'me') || 'me';
                    const load = prompt('Cognitive load (High/Medium/Low):', 'Medium') || 'Medium';
                    try {
                        const res = await fetch('/api/tasks', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ title, source, cognitive_load: load })
                        });
                        const data = await res.json();
                        if (!res.ok) {
                            alert(data.message || 'Failed to add task');
                            return;
                        }
                        state.tasks.push(data.task);
                        renderTasks();
                    } catch (e) {
                        console.error('Error adding task:', e);
                        alert('Error adding task');
                    }
                });
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
