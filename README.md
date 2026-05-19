# 🎬 Video Prompt Generator — Multi-Agent AI System

> A multi-agent AI pipeline that reads scene descriptions from a PDF and
> automatically generates **individual Runway-ready prompts per scene**
> plus one **master video prompt** for the full video.

---

## 📌 Table of Contents

1. [Project Overview](#1-project-overview)
2. [How It Works — The Big Picture](#2-how-it-works--the-big-picture)
3. [Agent Architecture — Detailed](#3-agent-architecture--detailed)
4. [Project Structure](#4-project-structure)
5. [Setup Instructions](#5-setup-instructions)
6. [How to Run](#6-how-to-run)
7. [How to Use the App](#7-how-to-use-the-app)
8. [Input Format](#8-input-format)
9. [Output Format](#9-output-format)
10. [Design Patterns Used](#10-design-patterns-used)
11. [Tech Stack](#11-tech-stack)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Project Overview

### What does this project do?
This project takes a **PDF file containing scene descriptions** (like a script or storyboard notes) and uses **multiple AI agents** working together to generate professional **Runway AI video prompts**.

### Why multiple agents instead of one?
In the original single-agent version, one AI did everything — read the PDF, analyzed scenes, wrote prompts. That works, but it has problems:
- One agent doing too many jobs = less focused, lower quality output
- No way to improve specific parts without redoing everything
- Slower, less organized

In this multi-agent version:
- Each agent is a **specialist** with one clear job
- Agents pass their output to the next agent like an **assembly line**
- A **critic agent** checks quality and loops until the output is good enough
- Scene analysis runs **in parallel** — all 10 scenes analyzed at the same time (faster ⚡)

---

## 2. How It Works — The Big Picture

```
You upload a PDF
        ↓
① PDF Reader Agent reads and extracts text
        ↓
② Scene Analyzer Agent analyzes ALL scenes simultaneously (parallel ⚡)
        ↓
③a Theme Finder Agent → finds overall theme & mood
③b Connection Finder Agent → finds links between scenes
③c Story Flow Agent → maps the narrative arc
        ↓
④ Prompt Writer Agent → writes 1 prompt per scene + 1 master prompt
        ↓
⑤ Prompt Critic Agent → reviews quality, loops back if not good enough 🔁
        ↓
You get: 10 scene prompts + 1 master video prompt
```

---

## 3. Agent Architecture — Detailed

### Agent 1 — PDF Reader Agent
| Property | Details |
|----------|---------|
| **Pattern** | Sequential |
| **Job** | Opens the PDF and extracts all text |
| **Input** | File path to the PDF |
| **Output** | `{ "raw_text": "...", "pages": 10 }` |
| **File** | `agents.py` → `pdf_reader_agent()` |
| **Tool used** | `read_pdf()` from `tools.py` |

---

### Agent 2 — Scene Analyzer Agent
| Property | Details |
|----------|---------|
| **Pattern** | Parallel ⚡ |
| **Job** | Splits text into individual scenes and analyzes all of them at the same time |
| **Input** | Raw text from Agent 1 |
| **Output** | List of JSON objects, one per scene |
| **File** | `agents.py` → `scene_analyzer_agent()` |

**Example output for one scene:**
```json
{
  "scene": 1,
  "subject": "young woman",
  "location": "golden beach",
  "mood": "peaceful",
  "emotion": "solitude",
  "colors": "orange, pink, gold",
  "visual_theme": "nature and reflection",
  "time_of_day": "sunset"
}
```

---

### Agent 3a — Theme Finder Agent
| Property | Details |
|----------|---------|
| **Pattern** | Sequential |
| **Job** | Reads all scene analyses and identifies the overall theme and mood of the entire video |
| **Input** | List of scene analyses from Agent 2 |
| **Output** | `{ "overall_theme": "...", "overall_mood": "...", "visual_style": "...", "color_palette": "...", "narrative_arc": "..." }` |
| **Why it matters** | Without a consistent theme, the final prompt would feel disconnected and random |

---

### Agent 3b — Connection Finder Agent
| Property | Details |
|----------|---------|
| **Pattern** | Sequential |
| **Job** | Finds what visually or thematically links consecutive scenes together |
| **Input** | List of scene analyses from Agent 2 |
| **Output** | List of connections: `[{ "from_scene": 1, "to_scene": 2, "connection": "..." }]` |
| **Why it matters** | Helps the Prompt Writer create smooth transitions between scenes |

---

### Agent 3c — Story Flow Agent
| Property | Details |
|----------|---------|
| **Pattern** | Sequential |
| **Job** | Writes a narrative guide describing how the story should progress start to finish |
| **Input** | Theme + connections + scene count |
| **Output** | A short paragraph (plain text) describing the narrative arc |
| **Why it matters** | Without story flow guidance, the video would feel like random scenes stitched together |

---

### Agent 4 — Prompt Writer Agent
| Property | Details |
|----------|---------|
| **Pattern** | Sequential |
| **Job** | Writes one Runway prompt per scene AND one master prompt for the full video |
| **Input** | Scene analyses + theme + connections + story flow |
| **Output** | `{ "scene_prompts": [...], "master_prompt": "..." }` |
| **Why it matters** | This is the core output — individual prompts let you generate each scene in Runway separately, the master prompt is for one long continuous video |

---

### Agent 5 — Prompt Critic Agent
| Property | Details |
|----------|---------|
| **Pattern** | Loop 🔁 |
| **Job** | Reviews all prompts for quality. If not good enough, sends back for improvement. Loops until approved or max iterations hit. |
| **Input** | Prompts from Agent 4 |
| **Output** | Final approved prompts |
| **Approval threshold** | Score ≥ 7 out of 10 |
| **Max iterations** | 3 (adjustable in the UI sidebar) |

**How the loop works:**
```
Critic evaluates prompts
    → Score >= 7? → APPROVED ✅ → exit loop
    → Score < 7?  → send feedback to Prompt Writer → rewrite → evaluate again
    → Hit max iterations? → return best version so far → exit loop
```

---

## 4. Project Structure

```
VIDEO_PROMPT_GENERATOR_MULTI/
│
├── app.py                  # Streamlit web UI — the interface you see in the browser
├── agents.py               # All 7 agents + run_pipeline() coordinator function
├── tools.py                # PDF reading utility used by Agent 1
├── create_test_pdf.py      # Script to generate a sample test PDF (optional)
├── requirements.txt        # All Python libraries needed
├── .env                    # Your secret API key (never share or commit this!)
└── README.md               # This file
```

### What each file does in plain English:

| File | Think of it as... |
|------|------------------|
| `app.py` | The front door — what the user sees and interacts with |
| `agents.py` | The engine room — where all the AI work happens |
| `tools.py` | A toolbox — helper functions the agents pick up and use |
| `create_test_pdf.py` | A practice dummy — creates a fake PDF so you can test without your own PDF |
| `requirements.txt` | A shopping list — tells pip which libraries to install |
| `.env` | A secret locker — stores your API key safely outside the code |

---

## 5. Setup Instructions

### Step 1 — Make sure Python is installed
```bash
python --version
# Should show Python 3.8 or higher
```

### Step 2 — Create a new project folder and open it in VS Code
```bash
cd ..
mkdir VIDEO_PROMPT_GENERATOR_MULTI
code VIDEO_PROMPT_GENERATOR_MULTI
```

### Step 3 — Copy all project files into the folder
Copy these files into `VIDEO_PROMPT_GENERATOR_MULTI/`:
- `app.py`
- `agents.py`
- `tools.py`
- `create_test_pdf.py`
- `requirements.txt`

### Step 4 — Create a virtual environment
A virtual environment keeps this project's libraries separate from other projects.
```bash
python -m venv venv
```

### Step 5 — Activate the virtual environment
```bash
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```
You'll know it's activated when you see `(venv)` at the start of your terminal line.

### Step 6 — Install all required libraries
```bash
pip install -r requirements.txt
```

### Step 7 — Create the `.env` file
Create a new file called `.env` in the project folder and add this line:
```
GROQ_API_KEY=your_groq_api_key_here
```
Replace `your_groq_api_key_here` with your actual key from [https://console.groq.com](https://console.groq.com).

> ⚠️ **Important:** Never share your `.env` file or upload it to GitHub. It contains your secret API key.

---

## 6. How to Run

### Option A — Run the Streamlit web app (recommended)
```bash
streamlit run app.py
```
This opens the app in your browser at `http://localhost:8501`

### Option B — Generate a test PDF first (if you don't have your own PDF)
```bash
python create_test_pdf.py
```
This creates `test_scenes.pdf` in your folder with 10 sample beach scenes.

---

## 7. How to Use the App

1. **Open the app** in your browser after running `streamlit run app.py`
2. **Upload your PDF** by clicking the upload area or dragging your file in
3. **Adjust settings** in the left sidebar if needed (e.g. critic max iterations)
4. **Click "⚡ Generate Prompts"**
5. **Watch the agent log** — you'll see each agent's progress in real time
6. **View results:**
   - Theme chips (overall mood, style, palette)
   - Story flow analysis (expandable)
   - Individual prompt for each scene
   - Master prompt for the full video
7. **Copy or download** — use the copy buttons or click "⬇️ Download All Prompts"

---

## 8. Input Format

Your PDF should contain scene descriptions. Each scene should start with `Scene N:` or `Scene N.`

**Example format:**
```
Scene 1: A young woman stands alone on a vast golden beach at sunset.
The sky is painted in shades of orange and pink.

Scene 2: Ocean waves crash powerfully against dark rocky shores.
White foam spreads across the rocks.

Scene 3: A tall lighthouse stands on a cliff...
```

> 💡 The app works best with **5–10 scenes**. More scenes = more API calls = slower but richer output.

---

## 9. Output Format

### Individual Scene Prompts
One Runway-ready prompt per scene. Paste each into Runway to generate that specific shot.

**Example:**
```
Scene 1: A lone young woman silhouetted against a vast golden beach,
warm orange and pink sunset sky reflected on the shoreline, peaceful
and contemplative mood, golden hour lighting. cinematic, photorealistic,
smooth motion.
```

### Master Video Prompt
One combined prompt describing the full video from start to finish. Use this in Runway's Multi-Shot mode.

**Example:**
```
A solitary woman's journey along a dramatic coastal landscape from
golden sunset to starlit night — warm amber tones transitioning to
deep blues, the lighthouse as a guiding constant, nature's grandeur
evoking peace and quiet wonder. cinematic, photorealistic, smooth motion.
```

### Download
All prompts are downloadable as `video_prompts_output.txt`.

---

## 10. Design Patterns Used

This project demonstrates 3 key multi-agent design patterns:

| Pattern | Where it's used | Why |
|---------|----------------|-----|
| **Sequential** | Agents 1 → 3a → 3b → 3c → 4 | Each agent needs the previous agent's output before it can start |
| **Parallel** | Agent 2 (scene analysis) | All scenes are independent, so we analyze them simultaneously to save time |
| **Loop (Evaluator-Optimizer)** | Agent 5 (critic) | Quality control — keeps improving until the output meets the standard |

---

## 11. Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python** | Core programming language |
| **Groq API** | Fast AI inference provider |
| **Llama 3.3 70B** | The LLM used by all agents |
| **Streamlit** | Web UI framework |
| **pypdf** | PDF text extraction |
| **concurrent.futures** | Parallel processing for Agent 2 |
| **python-dotenv** | Loads API key from .env file |
| **fpdf2** | Creates the test PDF |

---

## 12. Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| `GROQ_API_KEY not found` | .env file missing or wrong key name | Check your `.env` file has `GROQ_API_KEY=...` with no spaces |
| `ModuleNotFoundError` | Libraries not installed | Run `pip install -r requirements.txt` again |
| `streamlit: command not found` | Virtual environment not activated | Run `venv\Scripts\activate` first |
| `File not found` error | Wrong PDF path | Make sure the PDF is in the project folder |
| App opens but nothing happens | Forgot to click Generate | Upload PDF first, then click ⚡ Generate Prompts |
| Scene prompts list is empty | PDF format not recognized | Make sure scenes start with `Scene 1:`, `Scene 2:`, etc. |
| API rate limit error | Too many requests | Wait 30 seconds and try again, or reduce scene count |

---

*Built as an internship project demonstrating multi-agent AI system design.*
*Single-agent → Multi-agent conversion with sequential, parallel, and loop patterns.*#   v i d e o - p r o m p t - g e n e r a t o r - m u l t i  
 