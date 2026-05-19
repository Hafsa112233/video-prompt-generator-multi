import streamlit as st
import tempfile
import os
from agents import run_pipeline

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Video Prompt Generator",
    page_icon="🎬",
    layout="wide",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #0a0a0f;
    color: #e8e6f0;
}

.stApp {
    background: #0a0a0f;
}

/* Header */
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #ff6b6b 0%, #ffd93d 40%, #6bcb77 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.2rem;
}

.hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
    color: #6b6880;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 2.5rem;
}

/* Agent status log */
.log-box {
    background: #13121a;
    border: 1px solid #2a2840;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    color: #a09cb8;
    line-height: 2;
    max-height: 260px;
    overflow-y: auto;
}

/* Scene prompt cards */
.scene-card {
    background: #13121a;
    border: 1px solid #2a2840;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}

.scene-card:hover {
    border-color: #ff6b6b55;
}

.scene-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #ffd93d;
    margin-bottom: 0.5rem;
}

.scene-text {
    font-family: 'DM Mono', monospace;
    font-size: 0.88rem;
    color: #d4d0e8;
    line-height: 1.7;
}

/* Master prompt box */
.master-box {
    background: linear-gradient(135deg, #1a1225 0%, #120f1f 100%);
    border: 1.5px solid #ff6b6b55;
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-top: 1.5rem;
}

.master-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #ff6b6b;
    margin-bottom: 0.8rem;
}

.master-text {
    font-family: 'DM Mono', monospace;
    font-size: 0.95rem;
    color: #f0eeff;
    line-height: 1.8;
}

/* Upload zone */
.upload-hint {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #4a4760;
    text-align: center;
    margin-top: 0.5rem;
    letter-spacing: 0.05em;
}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid #2a2840;
    margin: 2rem 0;
}

/* Theme chip */
.chip {
    display: inline-block;
    background: #1e1b2e;
    border: 1px solid #3a3560;
    border-radius: 100px;
    padding: 0.25rem 0.9rem;
    font-size: 0.78rem;
    color: #9b96c0;
    margin: 0.2rem;
    font-family: 'DM Mono', monospace;
}

/* Streamlit overrides */
.stButton > button {
    background: linear-gradient(135deg, #ff6b6b, #ffd93d) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 2.2rem !important;
    transition: opacity 0.2s !important;
}

.stButton > button:hover {
    opacity: 0.85 !important;
}

div[data-testid="stFileUploader"] {
    background: #13121a !important;
    border: 1.5px dashed #2a2840 !important;
    border-radius: 12px !important;
}

/* Progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg, #ff6b6b, #ffd93d) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d0c14 !important;
    border-right: 1px solid #1e1b2e !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="hero-title">🎬 Video Prompt Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Multi-Agent AI · Runway-Ready Prompts · Scene-by-Scene</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR — Agent Info
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 Agent Pipeline")
    st.markdown("""
<div style='font-family: DM Mono, monospace; font-size: 0.8rem; color: #7a76a0; line-height: 2.2;'>
① PDF Reader<br>
② Scene Analyzer <span style='color:#ffd93d'>(parallel)</span><br>
③a Theme Finder<br>
③b Connection Finder<br>
③c Story Flow<br>
④ Prompt Writer<br>
⑤ Prompt Critic <span style='color:#6bcb77'>(loop)</span>
</div>
""", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#2a2840; margin:1.2rem 0'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Settings")
    max_iter = st.slider("Critic max iterations", 1, 5, 3)
    st.markdown("<hr style='border-color:#2a2840; margin:1.2rem 0'>", unsafe_allow_html=True)
    st.markdown("""
<div style='font-size:0.75rem; color:#4a4760; font-family: DM Mono, monospace;'>
Model: Gemini 3 Flash Preview<br>
Provider: Google
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN — Upload + Generate
# ─────────────────────────────────────────────
col1, col2 = st.columns([1.2, 1], gap="large")

with col1:
    st.markdown("#### Upload your scenes PDF")
    uploaded_file = st.file_uploader(
        label="Drop PDF here",
        type=["pdf"],
        label_visibility="collapsed",
    )
    st.markdown('<div class="upload-hint">PDF with scene descriptions · max 10 scenes recommended</div>', unsafe_allow_html=True)

    if uploaded_file:
        st.markdown(f"""
<div style='margin-top:1rem; padding:0.8rem 1.2rem; background:#13121a; border-radius:10px;
border:1px solid #2a2840; font-size:0.82rem; color:#9b96c0; font-family: DM Mono, monospace;'>
📎 <b style='color:#d4d0e8'>{uploaded_file.name}</b> &nbsp;·&nbsp; {round(uploaded_file.size/1024, 1)} KB
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown("#### Ready to generate?")
    st.markdown("""
<div style='font-size:0.82rem; color:#6b6880; font-family: DM Mono, monospace; line-height:1.9; margin-bottom:1.2rem;'>
7 specialized agents will work together<br>
to craft Runway-ready prompts for<br>
each scene + a master video prompt.
</div>
""", unsafe_allow_html=True)
    generate_btn = st.button("⚡ Generate Prompts", use_container_width=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PIPELINE EXECUTION
# ─────────────────────────────────────────────
if generate_btn:
    if not uploaded_file:
        st.error("Please upload a PDF file first!")
    else:
        log_lines = []
        log_placeholder = st.empty()
        progress_bar = st.progress(0)

        # Agent step weights for progress bar
        AGENT_STEPS = [
            "Agent 1",
            "Agent 2",
            "Agent 3a",
            "Agent 3b",
            "Agent 3c",
            "Agent 4",
            "Agent 5",
        ]
        step_map = {name: int((i + 1) / len(AGENT_STEPS) * 100) for i, name in enumerate(AGENT_STEPS)}
        current_progress = [0]

        def update_progress(msg: str):
            log_lines.append(msg)
            log_html = "<br>".join(log_lines[-12:])  # show last 12 lines
            log_placeholder.markdown(
                f'<div class="log-box">{log_html}</div>',
                unsafe_allow_html=True,
            )
            # Update progress bar based on agent
            for agent_name, pct in step_map.items():
                if agent_name.lower() in msg.lower():
                    if pct > current_progress[0]:
                        current_progress[0] = pct
                        progress_bar.progress(current_progress[0])
                    break

        # Save PDF to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            result = run_pipeline(tmp_path, progress_callback=update_progress)
            progress_bar.progress(100)
            update_progress("🎉 Pipeline complete!")

            # ── RESULTS ──────────────────────────────
            st.markdown("## 🎬 Generated Prompts")

            # Theme chips
            theme = result.get("theme", {})
            if theme:
                chips_html = " ".join([
                    f'<span class="chip">🎨 {theme.get("overall_theme","")}</span>',
                    f'<span class="chip">💭 {theme.get("overall_mood","")}</span>',
                    f'<span class="chip">🎥 {theme.get("visual_style","")}</span>',
                    f'<span class="chip">🌈 {theme.get("color_palette","")}</span>',
                ])
                st.markdown(chips_html, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

            # Story flow
            if result.get("story_flow"):
                with st.expander("📖 Story Flow Analysis", expanded=False):
                    st.markdown(f"""
<div style='font-family: DM Mono, monospace; font-size:0.85rem; color:#a09cb8; line-height:1.8;'>
{result['story_flow']}
</div>""", unsafe_allow_html=True)

            # Scene prompts
            st.markdown("### 🎞️ Individual Scene Prompts")
            scene_prompts = result.get("scene_prompts", [])

            if scene_prompts:
                for sp in scene_prompts:
                    scene_num = sp.get("scene", "?")
                    heading = sp.get("heading", "")
                    prompt_text = sp.get("prompt", "")
                    transition = sp.get("transition_to_next", "")

                    st.markdown(f"""
<div class="scene-card">
  <div class="scene-label">Scene {scene_num} — {heading}</div>
  <div class="scene-text">{prompt_text}</div>
  <div style='font-size:0.75rem; color:#6b6880; margin-top:0.5rem;'>
    🔗 Transition: {transition}
  </div>
</div>""", unsafe_allow_html=True)

                    st.code(prompt_text, language=None)

            else:
                st.warning("No scene prompts were generated.")

            # Master prompt
            master = result.get("master_prompt", "")
            if master:
                st.markdown(f"""
<div class="master-box">
  <div class="master-label">🎬 Master Video Prompt</div>
  <div class="master-text">{master}</div>
</div>""", unsafe_allow_html=True)
                st.code(master, language=None)

            # Save to file
            output_text = "=== INDIVIDUAL SCENE PROMPTS ===\n\n"
            for sp in scene_prompts:
                output_text += f"Scene {sp.get('scene', '?')}:\n{sp.get('prompt', '')}\n\n"
            output_text += "=== MASTER VIDEO PROMPT ===\n\n" + master

            st.download_button(
                label="⬇️ Download All Prompts (.txt)",
                data=output_text,
                file_name="video_prompts_output.txt",
                mime="text/plain",
            )

        except Exception as e:
            st.error(f"Pipeline error: {str(e)}")

        finally:
            os.unlink(tmp_path)