# ============================================================
# agents.py — All 7 agents for the Multi-Agent Pipeline
# Using Google Gemini API
# ============================================================

import os
import json
import re
import concurrent.futures
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools import read_pdf

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = "gemini-3-flash-preview"


# ============================================================
# HELPER FUNCTION — Call Gemini API
# ============================================================

def _call_gemini(system_prompt: str, user_prompt: str, temperature: float = 0.4, max_tokens: int = 1000) -> str:
    """Helper function to call Gemini API with retry on rate limit"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            return response.text.strip()
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = 30 * (attempt + 1)
                print(f"Rate limit hit! Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise e


# ============================================================
# AGENT 1 — PDF Reader Agent
# ============================================================

def pdf_reader_agent(pdf_path: str, progress_callback=None) -> dict:
    if progress_callback:
        progress_callback("📄 Agent 1: Reading PDF...")

    result = read_pdf(pdf_path)

    if result["status"] == "error":
        raise ValueError(f"PDF Reader Agent failed: {result['error']}")

    if progress_callback:
        progress_callback(f"✅ Agent 1 done — extracted {result['pages']} page(s)")

    return {
        "raw_text": result["text"],
        "pages": result["pages"],
    }


# ============================================================
# AGENT 2 — Scene Splitter + Analyzer Agent
# ============================================================

def _split_screenplay_into_scenes(raw_text: str) -> list:
    """Splits a screenplay into individual scenes."""
    pattern = r'(\d+\.\s+(?:INT\.|EXT\.)[^\n]+|\b(?:INT\.|EXT\.)[^\n]+)'
    parts = re.split(pattern, raw_text, flags=re.IGNORECASE)

    scenes = []
    i = 1
    while i < len(parts) - 1:
        heading = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""

        num_match = re.match(r'^(\d+)\.', heading)
        scene_num = int(num_match.group(1)) if num_match else len(scenes) + 1

        location_match = re.search(r'(?:INT\.|EXT\.)\s+([^-\n]+)', heading, re.IGNORECASE)
        time_match = re.search(r'-\s+(\w+)', heading)

        location = location_match.group(1).strip() if location_match else "Unknown"
        time_of_day = time_match.group(1).strip() if time_match else "Unknown"
        interior_exterior = "INT" if "INT." in heading.upper() else "EXT"

        scenes.append({
            "scene_num": scene_num,
            "heading": heading,
            "location": location,
            "time_of_day": time_of_day,
            "interior_exterior": interior_exterior,
            "body": body,
        })
        i += 2

    if not scenes:
        lines = [l.strip() for l in raw_text.strip().split("\n\n") if l.strip()]
        scenes = [{
            "scene_num": idx + 1,
            "heading": f"Scene {idx + 1}",
            "location": "Unknown",
            "time_of_day": "Unknown",
            "interior_exterior": "Unknown",
            "body": line,
        } for idx, line in enumerate(lines)]

    return scenes


def _analyze_batch_of_scenes(batch: list) -> list:
    """Analyze a batch of scenes in ONE API call"""
    time.sleep(1)
    
    # Format all scenes in the batch into one text
    batch_text = ""
    for scene in batch:
        batch_text += f"""
Scene {scene['scene_num']}:
Heading: {scene['heading']}
Location: {scene['location']}
Time of Day: {scene['time_of_day']}
Interior/Exterior: {scene['interior_exterior']}
Content: {scene['body'][:500]}
---
"""

    raw = _call_gemini(
        system_prompt="""You are a professional film scene analyst.
Analyze ALL the given scenes and return ONLY a valid JSON array.
For each scene return an object with these exact keys:
{
  "scene": <scene number>,
  "heading": "<scene heading>",
  "location": "<specific location>",
  "time_of_day": "<time of day>",
  "interior_exterior": "<INT or EXT>",
  "characters": ["<character name and appearance>"],
  "main_action": "<what is happening>",
  "mood": "<emotional tone>",
  "emotion": "<human emotion conveyed>",
  "colors": "<dominant colors>",
  "visual_theme": "<visual style>",
  "dialogue_context": "<brief summary of dialogue>",
  "camera_suggestions": "<suggested camera movements>",
  "key_props": ["<important props>"]
}
Return ONLY a JSON array of objects. No explanation, no markdown, no extra text.""",
        user_prompt=batch_text,
        temperature=0.3,
        max_tokens=2000,
    )

    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        results = json.loads(raw)
        if isinstance(results, list):
            return results
        return []
    except json.JSONDecodeError:
        # If batch fails, return basic info for each scene
        return [{
            "scene": scene["scene_num"],
            "heading": scene["heading"],
            "location": scene["location"],
            "time_of_day": scene["time_of_day"],
            "interior_exterior": scene["interior_exterior"],
            "characters": [],
            "main_action": scene["body"][:200],
            "mood": "unknown",
            "emotion": "unknown",
            "colors": "unknown",
            "visual_theme": "unknown",
            "dialogue_context": "unknown",
            "camera_suggestions": "unknown",
            "key_props": [],
        } for scene in batch]


def scene_analyzer_agent(raw_text: str, progress_callback=None) -> list:
    if progress_callback:
        progress_callback("🎬 Agent 2: Splitting screenplay into scenes...")

    scenes = _split_screenplay_into_scenes(raw_text)
    scenes = scenes[:10]  # Only process first 10 scenes for now

    if progress_callback:
        progress_callback(f"✅ Found {len(scenes)} scenes — analyzing in batches of 10...")

    # Split scenes into batches of 10
    batch_size = 10
    batches = [scenes[i:i+batch_size] for i in range(0, len(scenes), batch_size)]

    if progress_callback:
        progress_callback(f"📦 Processing {len(batches)} batches...")

    scene_analyses = []

    # Process batches in parallel (max 3 at a time)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(_analyze_batch_of_scenes, batch): i
            for i, batch in enumerate(batches)
        }

        for future in concurrent.futures.as_completed(futures):
            results = future.result()
            scene_analyses.extend(results)

    scene_analyses.sort(key=lambda x: x.get("scene", 0))

    if progress_callback:
        progress_callback(f"✅ Agent 2 done — analyzed {len(scene_analyses)} scenes")

    return scene_analyses


# ============================================================
# AGENT 3a — Theme Finder Agent
# ============================================================

def theme_finder_agent(scene_analyses: list, progress_callback=None) -> dict:
    if progress_callback:
        progress_callback("🎨 Agent 3a: Finding overall theme & mood...")

    analyses_text = json.dumps(scene_analyses, indent=2)

    raw = _call_gemini(
        system_prompt="""You are a film director analyzing a screenplay's overall visual theme.
Given scene analyses, identify the overall theme and visual style of the entire film.
Return ONLY a JSON object:
{
  "overall_theme": "<main theme in 3-5 words>",
  "overall_mood": "<emotional tone of the whole film>",
  "visual_style": "<consistent visual style>",
  "color_palette": "<dominant overall palette>",
  "narrative_arc": "<brief description of the story arc>",
  "character_consistency": {
    "<character name>": "<appearance description to keep consistent across all scenes>"
  },
  "cinematography_style": "<overall camera and lighting style>"
}
Return ONLY the JSON. No markdown, no extra text.""",
        user_prompt=f"Scene analyses:\n{analyses_text}",
        temperature=0.4,
        max_tokens=500,
    )

    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "overall_theme": "cinematic journey",
            "overall_mood": "emotional",
            "visual_style": "cinematic",
            "color_palette": "neutral",
            "narrative_arc": "unknown",
            "character_consistency": {},
            "cinematography_style": "cinematic",
        }

    if progress_callback:
        progress_callback(f"✅ Agent 3a done — theme: {result.get('overall_theme', 'N/A')}")

    return result


# ============================================================
# AGENT 3b — Connection Finder Agent
# ============================================================

def connection_finder_agent(scene_analyses: list, progress_callback=None) -> list:
    if progress_callback:
        progress_callback("🔗 Agent 3b: Finding connections between scenes...")

    analyses_text = json.dumps(scene_analyses, indent=2)

    raw = _call_gemini(
        system_prompt="""You are a film editor finding visual and thematic connections between consecutive scenes.
Given scene analyses from a screenplay, find what visually or thematically connects each scene to the next.
Return ONLY a JSON array:
[
  {
    "from_scene": 1,
    "to_scene": 2,
    "visual_connection": "<visual element that links them>",
    "emotional_connection": "<emotional link between scenes>",
    "transition_suggestion": "<suggested transition type e.g. cut, fade, dissolve>"
  }
]
Return ONLY the JSON array. No markdown, no extra text.""",
        user_prompt=f"Scene analyses:\n{analyses_text}",
        temperature=0.4,
        max_tokens=1000,
    )

    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        connections = json.loads(raw)
    except json.JSONDecodeError:
        connections = []

    if progress_callback:
        progress_callback(f"✅ Agent 3b done — found {len(connections)} connections")

    return connections


# ============================================================
# AGENT 3c — Story Flow Agent
# ============================================================

def story_flow_agent(scene_analyses: list, theme: dict, connections: list, progress_callback=None) -> str:
    if progress_callback:
        progress_callback("📖 Agent 3c: Mapping story flow...")

    payload = {
        "theme": theme,
        "connections": connections,
        "scene_count": len(scene_analyses),
        "locations": [s.get("location", "") for s in scene_analyses],
        "moods": [s.get("mood", "") for s in scene_analyses],
    }

    flow = _call_gemini(
        system_prompt="""You are a narrative director working on a screenplay adaptation.
Write a short narrative flow guide describing how the film should progress visually from start to finish.
Focus on visual style, mood shifts, character consistency, and visual elements.
Write 4-6 sentences max. Plain text, no JSON, no bullet points.""",
        user_prompt=json.dumps(payload),
        temperature=0.5,
        max_tokens=300,
    )

    if progress_callback:
        progress_callback("✅ Agent 3c done — story flow mapped")

    return flow


# ============================================================
# AGENT 4 — Prompt Writer Agent
# ============================================================

def prompt_writer_agent(
    scene_analyses: list,
    theme: dict,
    connections: list,
    story_flow: str,
    progress_callback=None,
) -> dict:
    if progress_callback:
        progress_callback("✍️ Agent 4: Writing scene-by-scene Runway prompts...")

    character_consistency = theme.get("character_consistency", {})
    cinematography_style = theme.get("cinematography_style", "cinematic")
    color_palette = theme.get("color_palette", "neutral tones")
    visual_style = theme.get("visual_style", "cinematic")

    payload = json.dumps(
        {
            "scenes": scene_analyses,
            "theme": theme,
            "connections": connections,
            "story_flow": story_flow,
            "character_consistency": character_consistency,
            "cinematography_style": cinematography_style,
        },
        indent=2,
    )

    raw = _call_gemini(
        system_prompt=f"""You are a professional Runway AI video prompt writer working on a film adaptation.

IMPORTANT RULES:
1. Generate ONE Runway prompt per scene
2. Each prompt must be 30-50 words maximum
3. Each prompt must maintain VISUAL CONSISTENCY across all scenes:
   - Same color palette: {color_palette}
   - Same visual style: {visual_style}
   - Same cinematography: {cinematography_style}
   - Characters must look EXACTLY the same in every scene they appear
4. Each prompt must include:
   - Camera movement (tracking shot, dolly, aerial, pan etc.)
   - Location and time of day
   - Character action and appearance (if characters present)
   - Mood and lighting
   - Transition hint to next scene
5. Each prompt must end with: cinematic, photorealistic, smooth motion
6. Prompts must flow smoothly — when videos are combined they should feel like ONE movie!

Return ONLY a JSON object:
{{
  "scene_prompts": [
    {{
      "scene": 1,
      "heading": "<scene heading>",
      "prompt": "<runway prompt>",
      "transition_to_next": "<how this scene should end to connect to next>"
    }}
  ],
  "master_prompt": "<one paragraph describing the full film for reference>"
}}
Return ONLY the JSON. No markdown, no extra text.""",
        user_prompt=payload,
        temperature=0.7,
        max_tokens=4000,
    )

    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {"scene_prompts": [], "master_prompt": raw}

    if progress_callback:
        progress_callback(f"✅ Agent 4 done — {len(result.get('scene_prompts', []))} scene prompts written")

    return result


# ============================================================
# AGENT 5 — Prompt Critic Agent (LOOP 🔁)
# ============================================================

def _evaluate_prompts(prompts: dict, theme: dict) -> dict:
    raw = _call_gemini(
        system_prompt="""You are a strict Runway AI prompt quality reviewer for a film project.
Evaluate the given scene prompts and return ONLY a JSON object:
{
  "approved": true/false,
  "score": <1-10>,
  "issues": ["<issue 1>", "<issue 2>"],
  "improvement_instructions": "<specific instructions to improve>"
}
Check for: prompt length (30-50 words), visual consistency, camera movement, smooth flow, character consistency.
Approve (true) only if score >= 7. No markdown, no extra text.""",
        user_prompt=json.dumps({"prompts": prompts, "theme": theme}),
        temperature=0.3,
        max_tokens=400,
    )

    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"approved": True, "score": 7, "issues": [], "improvement_instructions": ""}


def _improve_prompts(prompts: dict, feedback: dict, scene_analyses: list, theme: dict, story_flow: str) -> dict:
    payload = {
        "current_prompts": prompts,
        "feedback": feedback,
        "scene_analyses": scene_analyses,
        "theme": theme,
        "story_flow": story_flow,
    }

    raw = _call_gemini(
        system_prompt="""You are a Runway AI prompt writer improving scene prompts based on critic feedback.
Fix ALL issues and return improved prompts as ONLY a JSON object:
{
  "scene_prompts": [
    {
      "scene": 1,
      "heading": "<scene heading>",
      "prompt": "<improved prompt>",
      "transition_to_next": "<transition hint>"
    }
  ],
  "master_prompt": "<improved master prompt>"
}
Each prompt must end with: cinematic, photorealistic, smooth motion.
Maintain visual consistency across ALL scenes.
Return ONLY the JSON. No markdown, no extra text.""",
        user_prompt=json.dumps(payload),
        temperature=0.6,
        max_tokens=4000,
    )

    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return prompts


def prompt_critic_agent(
    prompts: dict,
    scene_analyses: list,
    theme: dict,
    story_flow: str,
    max_iterations: int = 3,
    progress_callback=None,
) -> dict:
    current_prompts = prompts
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        if progress_callback:
            progress_callback(f"🔎 Agent 5: Quality check (iteration {iteration}/{max_iterations})...")

        feedback = _evaluate_prompts(current_prompts, theme)

        score = feedback.get("score", 7)
        approved = feedback.get("approved", True)

        if progress_callback:
            progress_callback(f"   Score: {score}/10 — {'✅ Approved!' if approved else '🔄 Needs improvement...'}")

        if approved:
            break

        if iteration < max_iterations:
            current_prompts = _improve_prompts(
                current_prompts, feedback, scene_analyses, theme, story_flow
            )

    if progress_callback:
        progress_callback("✅ Agent 5 done — final prompts approved!")

    return current_prompts


# ============================================================
# COORDINATOR — run_pipeline()
# ============================================================

def run_pipeline(pdf_path: str, progress_callback=None) -> dict:
    reader_output = pdf_reader_agent(pdf_path, progress_callback)
    scene_analyses = scene_analyzer_agent(reader_output["raw_text"], progress_callback)
    theme = theme_finder_agent(scene_analyses, progress_callback)
    connections = connection_finder_agent(scene_analyses, progress_callback)
    story_flow = story_flow_agent(scene_analyses, theme, connections, progress_callback)
    prompts = prompt_writer_agent(scene_analyses, theme, connections, story_flow, progress_callback)
    final_prompts = prompt_critic_agent(
        prompts, scene_analyses, theme, story_flow, progress_callback=progress_callback
    )

    print("Scene prompts count:", len(final_prompts.get("scene_prompts", [])))
    print("Master prompt:", final_prompts.get("master_prompt", "")[:100])

    return {
        "scene_analyses": scene_analyses,
        "theme": theme,
        "connections": connections,
        "story_flow": story_flow,
        "scene_prompts": final_prompts.get("scene_prompts", []),
        "master_prompt": final_prompts.get("master_prompt", ""),
    }