# 🎬 Video Prompt Generator — Multi-Agent AI System

> A multi-agent AI pipeline that reads a movie script PDF and automatically generates **individual Runway-ready prompts per scene** plus one **master video prompt** for the full video.

---

## 📌 Table of Contents

1. [Project Overview](#1-project-overview)
2. [How It Works](#2-how-it-works)
3. [Agent Architecture](#3-agent-architecture)
4. [Project Structure](#4-project-structure)
5. [Setup Instructions](#5-setup-instructions)
6. [How to Run](#6-how-to-run)
7. [Input Format](#7-input-format)
8. [Output Format](#8-output-format)
9. [Design Patterns Used](#9-design-patterns-used)
10. [Tech Stack](#10-tech-stack)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Project Overview

### What does this project do?
This project takes a **movie script PDF** and uses **multiple AI agents** working together to generate professional **Runway AI video prompts** — one prompt per scene.

### Why multiple agents instead of one?
- Each agent is a **specialist** with one clear job
- Agents pass output to the next like an **assembly line**
- A **critic agent** checks quality and loops until good enough
- Scene analysis runs **in parallel** — faster ⚡

---

## 2. How It Works
Upload a movie script PDF
↓
① PDF Reader Agent — extracts text
↓
② Scene Analyzer Agent — analyzes ALL scenes (parallel ⚡)
↓
③a Theme Finder Agent — finds overall theme and mood
③b Connection Finder Agent — finds links between scenes
③c Story Flow Agent — maps the narrative arc
↓
④ Prompt Writer Agent — writes 1 prompt per scene + master prompt
↓
⑤ Prompt Critic Agent — reviews quality, loops back if needed 🔁
↓
Output: Individual scene prompts + master video prompt

---

## 3. Agent Architecture

### Agent 1 — PDF Reader Agent
| Property | Details |
|----------|---------|
| **Pattern** | Sequential |
| **Job** | Opens the PDF and extracts all text |
| **Input** | File path to the PDF |
| **Output** | `{ "raw_text": "...", "pages": 10 }` |

### Agent 2 — Scene Analyzer Agent
| Property | Details |
|----------|---------|
| **Pattern** | Parallel ⚡ |
| **Job** | Splits screenplay into scenes and analyzes all simultaneously |
| **Input** | Raw text from Agent 1 |
| **Output** | List of JSON objects, one per scene |

### Agent 3a — Theme Finder Agent
| Property | Details |
|----------|---------|
| **Pattern** | Sequential |
| **Job** | Identifies overall theme, mood, visual style and character consistency |
| **Input** | Scene analyses from Agent 2 |
| **Output** | `{ "overall_theme": "...", "overall_mood": "...", "character_consistency": {...} }` |

### Agent 3b — Connection Finder Agent
| Property | Details |
|----------|---------|
| **Pattern** | Sequential |
| **Job** | Finds visual and thematic links between consecutive scenes |
| **Input** | Scene analyses from Agent 2 |
| **Output** | List of connections between scenes |

### Agent 3c — Story Flow Agent
| Property | Details |
|----------|---------|
| **Pattern** | Sequential |
| **Job** | Maps how the story should progress visually from start to finish |
| **Input** | Theme + connections + scene count |
| **Output** | Short narrative flow paragraph |

### Agent 4 — Prompt Writer Agent
| Property | Details |
|----------|---------|
| **Pattern** | Sequential |
| **Job** | Writes one Runway prompt per scene + one master prompt |
| **Input** | Scene analyses + theme + connections + story flow |
| **Output** | `{ "scene_prompts": [...], "master_prompt": "..." }` |

### Agent 5 — Prompt Critic Agent
| Property | Details |
|----------|---------|
| **Pattern** | Loop 🔁 |
| **Job** | Reviews prompts, sends back for improvement if score < 7 |
| **Input** | Prompts from Agent 4 |
| **Output** | Final approved prompts |
| **Max iterations** | 3 (adjustable in sidebar) |

---

## 4. Project Structure
VIDEO_PROMPT_GENERATOR_MULTI/
│
├── app.py              # Streamlit web UI
├── agents.py           # All 7 agents + coordinator
├── tools.py            # PDF reading utility
├── requirements.txt    # Required libraries
├── .gitignore          # Files to ignore in GitHub
├── .env                # Your API key (never commit this!)
└── README.md           # This file

---

## 5. Setup Instructions

### Step 1 — Clone the repository
```bash
git clone https://github.com/Hafsa112233/video-prompt-generator-multi.git
cd video-prompt-generator-multi
```

### Step 2 — Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Create `.env` file
GOOGLE_API_KEY=your_gemini_api_key_here
Get your free API key from [https://aistudio.google.com/](https://aistudio.google.com/)

---

## 6. How to Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## 7. Input Format

Your PDF should be a screenplay with scene headings like:

INT. ADAM'S APARTMENT - DUSK 1
A view of London stretches south...
EXT. STREET - NIGHT 2
Adam walks quickly through...


---

## 8. Output Format

### Individual Scene Prompts
One Runway-ready prompt per scene:
Scene 1: Slow drone push-in toward a high-rise window overlooking
London at dusk. Neutral gray sky meets Victorian rooftops. Muted
lighting. cinematic, photorealistic, smooth motion.

### Master Video Prompt
One combined prompt for the full film reference.

### Download
All prompts downloadable as `video_prompts_output.txt`

---

## 9. Design Patterns Used

| Pattern | Where | Why |
|---------|-------|-----|
| **Sequential** | Agents 1 → 3a → 3b → 3c → 4 | Each agent needs previous output |
| **Parallel** | Agent 2 | Scenes are independent, analyze simultaneously |
| **Loop** | Agent 5 | Quality control until standard is met |

---

## 10. Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python** | Core language |
| **Google Gemini 3 Flash** | AI model for all agents |
| **Google GenAI SDK** | Gemini API client |
| **Streamlit** | Web UI |
| **pypdf** | PDF text extraction |
| **concurrent.futures** | Parallel processing |
| **python-dotenv** | Load API key from .env |

---

## 11. Troubleshooting

| Problem | Fix |
|---------|-----|
| `GOOGLE_API_KEY not found` | Check `.env` file has `GOOGLE_API_KEY=...` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `streamlit not found` | Activate venv first |
| `Rate limit error` | Wait 30 seconds and try again |
| `Scene prompts empty` | Make sure PDF has `INT.` or `EXT.` scene headings |

---

*Built as an internship project demonstrating multi-agent AI system design.*
*Patterns used: Sequential, Parallel, and Loop.*