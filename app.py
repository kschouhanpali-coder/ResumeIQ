"""
app.py — AI Resume Analyzer & ATS Evaluator
Professional Streamlit dashboard powered by Groq/Gemini AI.
Modular version with separate components.
"""

import os
import json
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from resume_parser import extract_resume_text
from ats_analyzer import analyze_resume, _validate_result

# Modular imports
from history_manager import load_history, save_history, add_to_history
from report_generator import esc
from ui_components import (
    render_ats_evaluation_tab,
    render_optimization_tab,
    render_career_roadmap_tab,
    render_templates_tab,
    format_keyword
)

DEFAULT_MODEL_NAME = "Llama 3.3 70B"
DEFAULT_MODEL_ID = "llama-3.3-70b-versatile"

# Initialize session state for analysis results
if "active_candidate_id" not in st.session_state:
    st.session_state.active_candidate_id = None
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "sel_model" not in st.session_state:
    st.session_state.sel_model = DEFAULT_MODEL_NAME
if "last_file_name" not in st.session_state:
    st.session_state.last_file_name = None
if "last_jd" not in st.session_state:
    st.session_state.last_jd = None

# Page Config
st.set_page_config(
    page_title="ResumeIQ — AI Resume Analyzer",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load CSS Stylesheet
if os.path.exists("style.css"):
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">📋</div>
        <div class="brand-text">
            <h3><span style="text-transform: none !important; background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">Resume</span><span style="text-transform: none !important; background: linear-gradient(135deg, #f59e0b, #ef4444); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">IQ</span></h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key Persistence
    SAVED_KEY_FILE = ".api_key"
    saved_key = ""
    if os.path.exists(SAVED_KEY_FILE):
        try:
            with open(SAVED_KEY_FILE, "r") as f:
                saved_key = f.read().strip()
        except Exception:
            pass

    if not saved_key:
        saved_key = os.environ.get("GROQ_API_KEY", "")

    # API Credentials Card
    with st.container(border=True):
        st.markdown("""
        <div class="sidebar-header-pill" style="margin-top: 0; margin-bottom: 0.8rem;">
            <span class="icon">🔑</span>
            <span class="text">Groq API</span>
        </div>
        """, unsafe_allow_html=True)
        api_key = st.text_input("key", type="password", value=saved_key, placeholder="Enter your Groq API key",
                                label_visibility="collapsed", help="Get your Groq API Key from console.groq.com")
        
        if api_key:
            if api_key != saved_key:
                try:
                    with open(SAVED_KEY_FILE, "w") as f:
                        f.write(api_key.strip())
                except Exception:
                    pass
            status_html = '<div class="status-indicator active"><span class="pulse-green"></span>Groq Core Active</div>'
        else:
            # If the input was cleared, remove the file so it's not loaded next time
            if os.path.exists(SAVED_KEY_FILE):
                try:
                    os.remove(SAVED_KEY_FILE)
                except Exception:
                    pass
            status_html = '<div class="status-indicator offline"><span class="pulse-orange"></span>Groq Core Inactive</div>'
        
        st.markdown(status_html, unsafe_allow_html=True)

    # Resume Upload
    with st.container(border=True):
        st.markdown("""
        <div class="sidebar-header-pill" style="margin-top: 0; margin-bottom: 0.8rem;">
            <span class="icon">📤</span>
            <span class="text">Resume Upload Pool</span>
        </div>
        """, unsafe_allow_html=True)
        uploaded_files = st.file_uploader("file", type=["pdf","docx"], label_visibility="collapsed",
                                         accept_multiple_files=True,
                                         help="PDF or DOCX, max 200MB. Upload 10-100 resumes for ranking.")
        if uploaded_files:
            if len(uploaded_files) == 1:
                st.markdown(f"""
                <div class="file-ok">
                    <span class="dot"></span>
                    <span class="fname">{esc(uploaded_files[0].name)}</span>
                    <span class="fsize">{uploaded_files[0].size/1024:.0f} KB</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="file-ok">
                    <span class="dot"></span>
                    <span class="fname">{len(uploaded_files)} files selected</span>
                    <span class="fsize">{sum(f.size for f in uploaded_files)/1024:.0f} KB total</span>
                </div>
                """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Check if we should render a detailed candidate report or the history dashboard
# ─────────────────────────────────────────────────────────────
if st.session_state.analysis_data is None:
    # ─────────────────────────────────────────────────────────────
    # DASHBOARD / LANDING VIEW
    # ─────────────────────────────────────────────────────────────
    history = load_history()
    
    # Show Candidate Analytics Dashboard Header
    st.markdown("""
    <style>
    @keyframes headerGlow { 0%,100%{text-shadow:0 0 20px rgba(129,140,248,0.3)} 50%{text-shadow:0 0 40px rgba(167,139,250,0.5)} }
    @keyframes shimmer { 0%{background-position:200% center} 100%{background-position:-200% center} }
    </style>
    <div style="text-align: center; margin-bottom: 2rem; padding: 1.5rem 1rem;">
        <h1 style="font-size:3.2rem; font-weight:900; margin:0.5rem 0; line-height:1.15; animation:headerGlow 3s ease-in-out infinite;">
            <span style="background:linear-gradient(135deg,#818cf8 0%,#a78bfa 25%,#c084fc 50%,#818cf8 75%,#60a5fa 100%); background-size:200% auto; -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; animation:shimmer 4s linear infinite;">Resume</span><span style="background:linear-gradient(135deg,#f59e0b,#f97316,#ef4444); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">IQ</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)
    

        


    if history:
        # Spotlight Top Candidates Podium — Premium Design
        st.markdown("""
        <style>
        @keyframes spotlightShimmer {
            0% { background-position: -200% center; }
            100% { background-position: 200% center; }
        }
        @keyframes borderGlow {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }
        @keyframes floatBadge {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-3px); }
        }
        @keyframes scoreReveal {
            0% { opacity: 0; transform: scale(0.5); }
            100% { opacity: 1; transform: scale(1); }
        }
        .spotlight-title {
            display: flex; align-items: center; gap: 0.7rem; margin-top: 1rem; margin-bottom: 1.2rem; padding: 0.6rem 0;
        }
        .spotlight-title-icon {
            width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.15rem;
            background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(251,191,36,0.1)); border: 1px solid rgba(245,158,11,0.25);
            box-shadow: 0 0 15px rgba(245,158,11,0.15);
        }
        .spotlight-title-text {
            font-size: 1.08rem; font-weight: 800; letter-spacing: 0.5px;
            background: linear-gradient(135deg, #fbbf24, #f59e0b, #d97706); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        }
        .spotlight-card {
            position: relative; border-radius: 20px; padding: 1.5rem; height: 100%; overflow: hidden;
            backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .spotlight-card:hover {
            transform: translateY(-4px);
        }
        .spotlight-card::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; border-radius: 20px; padding: 1.5px; 
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0); mask-composite: exclude; -webkit-mask-composite: xor;
            pointer-events: none; animation: borderGlow 3s ease-in-out infinite;
        }
        .spotlight-card::after {
            content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; pointer-events: none; opacity: 0.03;
            background: conic-gradient(from 0deg, transparent, rgba(255,255,255,0.3), transparent 30%);
        }
        .spot-gold { background: linear-gradient(160deg, rgba(245,158,11,0.1) 0%, rgba(15,23,42,0.6) 40%, rgba(251,191,36,0.05) 100%); box-shadow: 0 8px 32px rgba(245,158,11,0.12), 0 0 60px rgba(245,158,11,0.04); }
        .spot-gold::before { background: linear-gradient(135deg, #f59e0b, #fbbf24, #f59e0b); }
        .spot-gold:hover { box-shadow: 0 12px 40px rgba(245,158,11,0.2), 0 0 80px rgba(245,158,11,0.06); }
        .spot-silver { background: linear-gradient(160deg, rgba(148,163,184,0.1) 0%, rgba(15,23,42,0.6) 40%, rgba(203,213,225,0.05) 100%); box-shadow: 0 8px 32px rgba(148,163,184,0.1), 0 0 60px rgba(148,163,184,0.03); }
        .spot-silver::before { background: linear-gradient(135deg, #94a3b8, #cbd5e1, #94a3b8); }
        .spot-silver:hover { box-shadow: 0 12px 40px rgba(148,163,184,0.18), 0 0 80px rgba(148,163,184,0.05); }
        .spot-bronze { background: linear-gradient(160deg, rgba(180,83,9,0.1) 0%, rgba(15,23,42,0.6) 40%, rgba(217,119,6,0.05) 100%); box-shadow: 0 8px 32px rgba(180,83,9,0.1), 0 0 60px rgba(180,83,9,0.03); }
        .spot-bronze::before { background: linear-gradient(135deg, #b45309, #d97706, #b45309); }
        .spot-bronze:hover { box-shadow: 0 12px 40px rgba(180,83,9,0.18), 0 0 80px rgba(180,83,9,0.05); }
        .spot-badge {
            display: inline-flex; align-items: center; gap: 0.35rem; font-size: 0.62rem; font-weight: 800; text-transform: uppercase;
            letter-spacing: 1.2px; padding: 0.25rem 0.7rem; border-radius: 20px; margin-bottom: 0.8rem;
            animation: floatBadge 3s ease-in-out infinite;
        }
        .spot-badge-gold { background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(251,191,36,0.1)); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); box-shadow: 0 2px 10px rgba(245,158,11,0.15); }
        .spot-badge-silver { background: linear-gradient(135deg, rgba(148,163,184,0.2), rgba(203,213,225,0.1)); color: #cbd5e1; border: 1px solid rgba(148,163,184,0.3); box-shadow: 0 2px 10px rgba(148,163,184,0.15); }
        .spot-badge-bronze { background: linear-gradient(135deg, rgba(180,83,9,0.2), rgba(217,119,6,0.1)); color: #d97706; border: 1px solid rgba(180,83,9,0.3); box-shadow: 0 2px 10px rgba(180,83,9,0.15); }
        .spot-avatar {
            width: 44px; height: 44px; border-radius: 14px; display: flex; align-items: center; justify-content: center;
            font-size: 0.85rem; font-weight: 900; color: #fff; letter-spacing: 1px; flex-shrink: 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .spot-avatar-gold { background: linear-gradient(135deg, #f59e0b, #d97706); }
        .spot-avatar-silver { background: linear-gradient(135deg, #94a3b8, #64748b); }
        .spot-avatar-bronze { background: linear-gradient(135deg, #b45309, #92400e); }
        .spot-name {
            font-size: 1rem; font-weight: 800; color: #f4f4f5; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
            letter-spacing: 0.3px;
        }
        .spot-file {
            font-size: 0.68rem; color: #71717a; margin-top: 0.15rem; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;
            display: flex; align-items: center; gap: 0.3rem;
        }
        .spot-score-ring {
            position: relative; width: 68px; height: 68px; margin: 0.8rem auto 0.5rem auto;
            animation: scoreReveal 0.6s ease-out;
        }
        .spot-score-text {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            font-size: 1.3rem; font-weight: 900; line-height: 1;
        }
        .spot-score-label {
            text-align: center; font-size: 0.58rem; color: #71717a; text-transform: uppercase; font-weight: 700; letter-spacing: 1px;
        }
        .spot-skill-tag {
            background: rgba(255,255,255,0.04); color: #a1a1aa; font-size: 0.6rem; font-weight: 600;
            padding: 0.18rem 0.5rem; display: inline-block; border: 1px solid rgba(255,255,255,0.07);
            border-radius: 20px; margin-right: 0.25rem; margin-bottom: 0.25rem; letter-spacing: 0.3px;
            transition: all 0.2s ease;
        }
        .spot-skill-tag:hover { background: rgba(255,255,255,0.08); color: #d4d4d8; }
        .spot-divider {
            height: 1px; margin: 0.7rem 0; 
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
        }
        </style>
        <div class="spotlight-title">
            <div class="spotlight-title-icon">🏆</div>
            <span class="spotlight-title-text">Top Performers Spotlight</span>
        </div>
        """, unsafe_allow_html=True)
        
        top_candidates = sorted(history, key=lambda x: x.get("ats_score", 0), reverse=True)[:3]
        spot_cols = st.columns(min(3, len(history)), gap="medium")
        
        podium_styles = [
            {"class": "gold", "color": "#fbbf24", "stroke": "#f59e0b", "badge": "🥇 #1 Gold"},
            {"class": "silver", "color": "#cbd5e1", "stroke": "#94a3b8", "badge": "🥈 #2 Silver"},
            {"class": "bronze", "color": "#d97706", "stroke": "#b45309", "badge": "🥉 #3 Bronze"}
        ]
        
        for idx, entry in enumerate(top_candidates):
            style_cfg = podium_styles[idx % len(podium_styles)]
            cand_name = entry["candidate_name"]
            ats_score = entry["ats_score"]
            filename = entry["filename"]
            skills = entry.get("analysis_data", {}).get("parsed_data", {}).get("skills", [])
            skills_html = "".join([f'<span class="spot-skill-tag">{esc(sk)}</span>' for sk in skills[:4]])
            
            # SVG ring arc calculation
            radius = 28
            circumference = 2 * 3.14159 * radius
            arc_length = (ats_score / 100) * circumference
            arc_gap = circumference - arc_length
            
            cls = style_cfg["class"]
            
            with spot_cols[idx]:
                st.markdown(f"""
                <div class="spotlight-card spot-{cls}">
                    <div class="spot-badge spot-badge-{cls}">{style_cfg['badge']}</div>
                    <div style="display:flex; align-items:center; gap:0.7rem; margin-bottom:0.3rem;">
                        <div class="spot-avatar spot-avatar-{cls}">{esc(cand_name[:2].upper())}</div>
                        <div style="min-width:0; flex:1;">
                            <div class="spot-name">{esc(cand_name)}</div>
                            <div class="spot-file">📄 {esc(filename)}</div>
                        </div>
                    </div>
                    <div class="spot-score-ring">
                        <svg viewBox="0 0 68 68" style="width:100%; height:100%; transform:rotate(-90deg);">
                            <circle cx="34" cy="34" r="{radius}" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="5"/>
                            <circle cx="34" cy="34" r="{radius}" fill="none" stroke="{style_cfg['stroke']}" stroke-width="5"
                                stroke-dasharray="{arc_length:.1f} {arc_gap:.1f}" stroke-linecap="round"
                                style="filter: drop-shadow(0 0 6px {style_cfg['stroke']}55); transition: stroke-dasharray 1s ease;"/>
                        </svg>
                        <div class="spot-score-text" style="color:{style_cfg['color']};">{ats_score}</div>
                    </div>
                    <div class="spot-score-label">ATS Score</div>
                    <div class="spot-divider"></div>
                    <div style="margin-top:0.3rem;">
                        {skills_html if skills_html else '<span style="font-size:0.65rem; color:#52525b; font-style:italic;">No skills parsed</span>'}
                    </div>
                </div>
                """, unsafe_allow_html=True)


        # Search & Filter controls
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        search_col, filter_col = st.columns([3, 2])
        with search_col:
            search_query = st.text_input("search_cand", placeholder="🔍 Search candidates by name, file, or skills...", label_visibility="collapsed")
        with filter_col:
            sort_by = st.selectbox(
                "Sort By",
                options=["ATS Score (Highest First)", "Date Analyzed (Latest First)"],
                index=0,
                key="candidate_sort_by",
                label_visibility="collapsed"
            )
            
        # Filter history by search query
        filtered_history = history
        if search_query:
            q = search_query.lower().strip()
            filtered_history = []
            for entry in history:
                name = entry.get("candidate_name", "").lower()
                fname = entry.get("filename", "").lower()
                skills = [s.lower() for s in entry.get("analysis_data", {}).get("parsed_data", {}).get("skills", [])]
                if q in name or q in fname or any(q in s for s in skills):
                    filtered_history.append(entry)

        # Sort filtered history
        if "ATS Score" in sort_by:
            history_sorted = sorted(filtered_history, key=lambda x: x.get("ats_score", 0), reverse=True)
        else:
            history_sorted = sorted(filtered_history, key=lambda x: x.get("timestamp", ""), reverse=True)

        # Category Tabs for Leaderboard
        tab_all, tab_pass, tab_review, tab_low = st.tabs([
            "👥 All Candidates", 
            "🟢 Shortlisted (75+)", 
            "🟡 Under Review (60-74)", 
            "🔴 Not Matching (<60)"
        ])

        def render_candidate_list(candidates_list, prefix):
            if not candidates_list:
                st.markdown("""
                <div style="border: 1px dashed rgba(255,255,255,0.06); border-radius: 12px; padding: 2.5rem; text-align: center; background: rgba(15,23,42,0.2); margin-top: 1rem;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📂</div>
                    <div style="color: #71717a; font-size: 0.88rem;">No candidates match this criteria.</div>
                </div>
                """, unsafe_allow_html=True)
                return
                
            for idx, entry in enumerate(candidates_list):
                score = entry['ats_score']
                score_color = "#4ade80" if score >= 80 else "#60a5fa" if score >= 60 else "#fbbf24" if score >= 40 else "#f87171"
                
                # Rank badge
                if "ATS Score" in sort_by:
                    if idx == 0:
                        rank_html = '<span style="background:linear-gradient(135deg,rgba(245,158,11,0.15),rgba(249,115,22,0.15)); color:#f59e0b; border:1px solid rgba(245,158,11,0.3); font-size:0.62rem; font-weight:700; padding:0.15rem 0.5rem; border-radius:12px; margin-left:0.6rem; vertical-align:middle; text-transform:uppercase; letter-spacing:0.5px;">🥇 #1</span>'
                    elif idx == 1:
                        rank_html = '<span style="background:linear-gradient(135deg,rgba(148,163,184,0.15),rgba(100,116,139,0.15)); color:#94a3b8; border:1px solid rgba(148,163,184,0.3); font-size:0.62rem; font-weight:700; padding:0.15rem 0.5rem; border-radius:12px; margin-left:0.6rem; vertical-align:middle; text-transform:uppercase; letter-spacing:0.5px;">🥈 #2</span>'
                    elif idx == 2:
                        rank_html = '<span style="background:linear-gradient(135deg,rgba(180,83,9,0.15),rgba(146,64,14,0.15)); color:#b45309; border:1px solid rgba(180,83,9,0.3); font-size:0.62rem; font-weight:700; padding:0.15rem 0.5rem; border-radius:12px; margin-left:0.6rem; vertical-align:middle; text-transform:uppercase; letter-spacing:0.5px;">🥉 #3</span>'
                    else:
                        rank_html = f'<span style="background:rgba(99,102,241,0.1); color:#818cf8; border:1px solid rgba(99,102,241,0.2); font-size:0.62rem; font-weight:700; padding:0.15rem 0.5rem; border-radius:12px; margin-left:0.6rem; vertical-align:middle; text-transform:uppercase; letter-spacing:0.5px;">#{idx+1}</span>'
                else:
                    rank_html = ""
    
                # Screening status
                if score >= 75:
                    screen_icon = "🟢"
                    screen_text = "Shortlisted"
                    screen_color = "#4ade80"
                elif score >= 60:
                    screen_icon = "🟡"
                    screen_text = "Under Review"
                    screen_color = "#fbbf24"
                else:
                    screen_icon = "🔴"
                    screen_text = "Not Matching"
                    screen_color = "#f87171"
                
                # Retrieve parsed key skills and format them
                skills = entry.get("analysis_data", {}).get("parsed_data", {}).get("skills", [])
                formatted_skills = []
                for sk in skills:
                    fmt = format_keyword(sk)
                    if fmt and fmt not in formatted_skills:
                        formatted_skills.append(fmt)
                if not formatted_skills and skills:
                    formatted_skills = [sk.title() for sk in skills]
                skills_chips = "".join([f'<span style="background:rgba(99,102,241,0.08); color:#a5b4fc; font-size:0.62rem; font-weight:600; padding:0.12rem 0.45rem; margin-right:0.25rem; margin-bottom:0.25rem; display:inline-block; border:1px solid rgba(99,102,241,0.18); border-radius:12px; letter-spacing:0.3px;">{esc(sk)}</span>' for sk in formatted_skills[:4]])
    
                with st.container(border=True):
                    rc1, rc2, rc3, rc4, rc5 = st.columns([3.6, 1.2, 1.2, 1.2, 0.5], vertical_alignment="center")
                    with rc1:
                        st.markdown(f"""
<div style="display:flex; align-items:center; gap:0.8rem; padding:0.1rem 0;">
<div style="width:40px; height:40px; border-radius:50%; background:linear-gradient(135deg,#6366f1 0%,#a855f7 100%); display:flex; align-items:center; justify-content:center; font-size:0.95rem; font-weight:800; color:#fff; box-shadow:0 4px 12px rgba(99,102,241,0.25); border: 2px solid rgba(255,255,255,0.1); flex-shrink:0;">
{esc(entry['candidate_name'][:2].upper())}
</div>
<div style="min-width:0;">
<div style="display:flex; align-items:center; flex-wrap:wrap;">
<span style="font-weight:700; color:#fafafa; font-size:0.95rem; letter-spacing: 0.3px;">{esc(entry['candidate_name'])}</span>
{rank_html}
</div>
<div style="font-size:0.72rem; color:#8e9196; margin-top:0.15rem; margin-bottom:0.35rem; display:flex; align-items:center; gap:0.25rem;">
<span>📄</span> <span style="text-overflow:ellipsis; overflow:hidden; white-space:nowrap; max-width:200px;">{esc(entry['filename'])}</span> <span style="color:#4b5563;">•</span> <span>{entry['timestamp'][:10]}</span>
</div>
<div class="tag-wrap" style="display:flex; flex-wrap:wrap; gap:0.1rem;">{skills_chips}</div>
</div>
</div>
""", unsafe_allow_html=True)
                    with rc2:
                        st.markdown(f"""
<div style="text-align:center;">
<div style="font-size:1.4rem; font-weight:900; color:{score_color}; line-height:1; text-shadow: 0 0 10px {score_color}22;">{score}</div>
<div style="font-size:0.58rem; color:#8e9196; text-transform:uppercase; font-weight:700; margin-top:0.2rem; letter-spacing:0.8px;">ATS Score</div>
</div>
""", unsafe_allow_html=True)
                    with rc3:
                        st.markdown(f"""
<div style="text-align:center;">
<span style="font-size:1rem; line-height:1.2;">{screen_icon}</span>
<div style="font-size:0.58rem; color:{screen_color}; font-weight:800; text-transform:uppercase; margin-top:0.15rem; letter-spacing:0.8px;">{screen_text}</div>
</div>
""", unsafe_allow_html=True)
                    with rc4:
                        if st.button("View", key=f"view_{prefix}_{entry['id']}", use_container_width=True, type="primary"):
                            st.session_state.active_candidate_id = entry['id']
                            st.session_state.analysis_data = entry['analysis_data']
                            st.session_state.resume_text = entry['resume_text']
                            st.session_state.sel_model = entry['sel_model']
                            st.rerun()
                    with rc5:
                        st.markdown('<div class="delete-btn-wrap">', unsafe_allow_html=True)
                        if st.button("🗑", key=f"delete_{prefix}_{entry['id']}", use_container_width=True):
                            updated_history = [h for h in history if h['id'] != entry['id']]
                            save_history(updated_history)
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

        with tab_all:
            render_candidate_list(history_sorted, "all")
        with tab_pass:
            render_candidate_list([c for c in history_sorted if c["ats_score"] >= 75], "pass")
        with tab_review:
            render_candidate_list([c for c in history_sorted if 60 <= c["ats_score"] < 75], "review")
        with tab_low:
            render_candidate_list([c for c in history_sorted if c["ats_score"] < 60], "low")
    else:
        # Empty state
        st.markdown("""
        <div style="border: 2px dashed #1e293b; border-radius: 12px; padding: 3rem; text-align: center; background: rgba(15,23,42,0.4); margin-bottom: 2rem;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">📂</div>
            <h4 style="color: #fafafa; font-size: 1.1rem; margin-bottom: 0.5rem; font-weight: 600;">No Candidate Records Yet</h4>
            <p style="color: #71717a; font-size: 0.88rem; max-width: 400px; margin: 0 auto;">Upload a candidate's resume in the sidebar, paste the job description below, and analyze to see results here.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Expander for analyzing a new resume, expanded dynamically based on history presence
    with st.expander("➕ Analyze New Resume", expanded=(not history)):
        st.markdown("""
        <div class="hero" style="padding: 1.5rem 1rem; margin-bottom: 1.5rem;">
            <h2>Analyze Candidate Resume</h2>
            <p>Upload a resume in the sidebar, paste a job description below, and click Analyze.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <div class="card-head">
                <div class="icon-box purple">💼</div>
                <h3>Job Description</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        job_description = st.text_area(
            "jd", height=200,
            placeholder="Paste the full job description here...\n\nExample: We are looking for a Software Engineer with 3+ years of experience in Python, React, AWS, Docker...",
            label_visibility="collapsed",
            key="dashboard_jd"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        _, bc, _ = st.columns([1, 2, 1])
        with bc:
            go_btn = st.button("Analyze Resume", use_container_width=True, type="primary", key="dashboard_analyze_btn")
            
        if go_btn:
            errs = []
            if not api_key: errs.append("Enter your **Groq API key** in the sidebar.")
            if not uploaded_files: errs.append("**Upload your resume(s)** in the sidebar.")
            if not job_description.strip(): errs.append("**Paste a job description** above.")
            if errs:
                for e in errs: st.error(e)
            else:
                if len(uploaded_files) == 1:
                    # Single file analysis
                    f = uploaded_files[0]
                    with st.status(f"Analyzing resume: {f.name}...", expanded=True) as status:
                        st.write("Extracting text from resume...")
                        f.seek(0)
                        resume_text = extract_resume_text(f)
                        if resume_text.startswith("[Error") or resume_text.startswith("[Unsupported"):
                            st.error(resume_text)
                            st.stop()
                        if len(resume_text.strip()) < 50:
                            st.error(f"⚠️ The uploaded file **{f.name}** does not contain enough extractable text. It might be a scanned image or empty. Please upload a standard text-based PDF or DOCX file.")
                            st.stop()
                        
                        st.write(f"Extracted **{len(resume_text):,}** characters from **{f.name}**")
                        model_display = DEFAULT_MODEL_NAME
                        st.write(f"Running ATS analysis with **{model_display}**...")
                        
                        result = analyze_resume(resume_text, job_description, api_key, DEFAULT_MODEL_ID)
                        if not result["success"]:
                            status.update(label="Analysis failed", state="error")
                            st.error(result["error"])
                            if result.get("raw"):
                                with st.expander("Raw response"): st.code(result["raw"])
                            st.stop()
                        
                        st.write("Done!")
                        status.update(label="Analysis complete", state="complete")
                    
                    add_to_history(
                        filename=f.name,
                        job_description=job_description,
                        analysis_data=result["data"],
                        resume_text=resume_text,
                        sel_model=model_display
                    )
                    
                    # Retrieve the generated candidate ID from history
                    hist = load_history()
                    cand_id = None
                    for h in hist:
                        if h.get("candidate_name") == result["data"].get("candidate_name") and h.get("filename") == f.name:
                            cand_id = h.get("id")
                            break
                    
                    st.session_state.active_candidate_id = cand_id
                    st.session_state.analysis_data = result["data"]
                    st.session_state.resume_text = resume_text
                    st.session_state.sel_model = model_display
                    st.rerun()
                else:
                    # Multiple files analysis
                    with st.status(f"Analyzing {len(uploaded_files)} resumes...", expanded=True) as status:
                        progress_bar = st.progress(0.0)
                        num_files = len(uploaded_files)
                        success_count = 0
                        
                        for idx, f in enumerate(uploaded_files):
                            st.write(f"Processing candidate {idx+1}/{num_files}: **{f.name}**...")
                            try:
                                f.seek(0)
                                resume_text = extract_resume_text(f)
                                if resume_text.startswith("[Error") or resume_text.startswith("[Unsupported"):
                                    st.error(f"Failed to extract text from {f.name}: {resume_text}")
                                    continue
                                if len(resume_text.strip()) < 50:
                                    st.error(f"⚠️ Failed to extract text from **{f.name}**: The file does not contain enough extractable text (might be a scanned image or empty).")
                                    continue
                                
                                result = analyze_resume(resume_text, job_description, api_key, DEFAULT_MODEL_ID)
                                if not result["success"]:
                                    st.error(f"Analysis failed for {f.name}: {result['error']}")
                                    continue
                                
                                add_to_history(
                                    filename=f.name,
                                    job_description=job_description,
                                    analysis_data=result["data"],
                                    resume_text=resume_text,
                                    sel_model=DEFAULT_MODEL_NAME
                                )
                                success_count += 1
                            except Exception as ex:
                                st.error(f"Unexpected error analyzing {f.name}: {ex}")
                            
                            progress_bar.progress(float(idx + 1) / num_files)
                        
                        if success_count > 0:
                            status.update(label=f"Analysis complete: successfully parsed and ranked {success_count}/{num_files} resumes!", state="complete")
                            st.success(f"Successfully processed and ranked {success_count} candidate resumes! Check the Analytics Dashboard below to view rankings.")
                            st.session_state.analysis_data = None
                            st.session_state.resume_text = None
                            st.session_state.sel_model = DEFAULT_MODEL_NAME
                            st.rerun()
                        else:
                            status.update(label="Analysis failed", state="error")
                            st.error("Could not parse or analyze any of the uploaded resumes.")
                
    st.stop()
else:
    # Detailed report view
    if st.button("← Back to History Dashboard", key="back_to_dashboard", type="secondary"):
        st.session_state.active_candidate_id = None
        st.session_state.analysis_data = None
        st.session_state.resume_text = None
        st.rerun()

    resume_text = st.session_state.resume_text
    data = _validate_result(st.session_state.analysis_data, resume_text=resume_text)
    sel_model = st.session_state.sel_model
    candidate_id = st.session_state.active_candidate_id

    with st.expander("🔍 View Extracted Resume Text", expanded=False):
        st.markdown(f"""
        <div class="extracted-text-container">
            <div class="extracted-text-box">
{esc(resume_text)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "📊 ATS Evaluation Dashboard", 
        "✍️ Optimization & Editor", 
        "🚀 Career Roadmap & Prep"
    ])
    
    with tab1:
        render_ats_evaluation_tab(data, sel_model, resume_text)
        
    with tab2:
        render_optimization_tab(data, candidate_id)
        
    with tab3:
        render_career_roadmap_tab(data, resume_text, candidate_id)

# Force reload trigger - removed contrib grid
