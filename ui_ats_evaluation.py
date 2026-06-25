import json
import re
import streamlit as st
from charts import make_radar
from report_generator import esc, v_cls, s_label, p_badge, generate_html_report

def format_keyword(kw):
    if not kw:
        return None
    kw_lower = kw.strip().lower()
    
    # Remove leading/trailing non-alphanumeric (except + or # for C++, C#)
    kw_lower = re.sub(r'^[^a-zA-Z0-9+#]+|[^a-zA-Z0-9+#]+$', '', kw_lower)
    if not kw_lower:
        return None
        
    # Ignore if it contains any digit (like salary 12, 12LPA, etc.)
    if re.search(r'\d', kw_lower):
        return None
        
    # Ignore if it starts with currency or is a common currency/salary keyword
    if any(kw_lower.startswith(c) for c in ['₹', '$', '£', '€', '¥']):
        return None
        
    # Noise words to ignore (including locations, work modes, and metadata)
    noise = {
        "must", "year", "years", "required", "preferred", "advantageous", 
        "experience", "work", "need", "needs", "using", "good", "strong", 
        "understanding", "knowledge", "skill", "skills", "ability", 
        "candidate", "role", "position", "etc", "and", "the", "for", "with", 
        "from", "that", "this", "these", "those", "have", "has", "had",
        "should", "would", "could", "about", "after", "again", "against",
        # Locations & regions
        "hyderabad", "bangalore", "bengaluru", "pune", "mumbai", "delhi", 
        "noida", "gurgaon", "gurugram", "chennai", "kolkata", "india", 
        "usa", "london", "singapore", "location", "locations", "country",
        # Workplace / job metadata
        "remote", "hybrid", "onsite", "office", "techai", "innovations", 
        "company", "job", "description", "contract", "salary", "fulltime", 
        "parttime", "internship", "employment", "immediate", "joiner", 
        "join", "joining", "client", "team", "members", "member", "opportunity",
        "opportunities", "candidate", "candidates", "applicant", "applicants",
        "process", "requirements", "responsibilities", "qualification", 
        "qualifications", "education", "degree", "diploma", "certification",
        "certifications", "day", "days", "week", "weeks", "month", "months",
        # Salary & compensation junk
        "lpa", "ctc", "lakh", "lakhs", "lac", "lacs", "pa", "pm", "inr", "usd", "compensation", "package", "annual",
        # Generic verbs, soft skills, and nouns
        "develop", "developing", "developer", "development", "lead", "leading", "leadership", 
        "mentor", "mentoring", "thinking", "think", "vision", "analytical", "analyze", "analyzing", 
        "analyst", "analysis", "build", "building", "builder", "create", "creating", "creator", 
        "design", "designing", "designer", "implement", "implementing", "implementation", 
        "manage", "managing", "management", "manager", "support", "supporting", "write", "writing", 
        "learn", "learning", "work", "working", "team", "teams", "people", "project", "projects", 
        "program", "programs", "system", "systems", "software", "application", "applications", 
        "technology", "technologies", "problem", "problems", "solving", "solved", "solution", 
        "solutions", "process", "processes", "master's degree", "masters degree", "bachelors degree", 
        "bachelor's degree", "degree", "education", "organization", "organizations", "expert", 
        "expertise", "excellent", "highly", "focused", "focus", "success", "successful", "deliver", 
        "delivering", "delivered", "collaborate", "collaborating", "collaboration", "drive", 
        "driving", "driven", "effective", "effectively", "goal", "goals", "result", "results", 
        "key", "value", "values", "growth", "grow", "growing"
    }
    
    if kw_lower in noise:
        return None
        
    # Standard acronyms / special casings
    custom_casings = {
        "sql": "SQL",
        "nlp": "NLP",
        "gcp": "GCP",
        "aws": "AWS",
        "api": "API",
        "ml": "ML",
        "ai": "AI",
        "cv": "CV",
        "c++": "C++",
        "c#": "C#",
        "js": "JavaScript",
        "css": "CSS",
        "html": "HTML",
        "json": "JSON",
        "rest": "REST",
        "xml": "XML",
        "db": "Database",
        "nosql": "NoSQL",
        "mongodb": "MongoDB",
        "tensorflow": "TensorFlow",
        "pytorch": "PyTorch",
        "scikit-learn": "Scikit-Learn",
        "numpy": "NumPy",
        "pandas": "Pandas",
        "matplotlib": "Matplotlib",
        "seaborn": "Seaborn",
        "github": "GitHub",
        "gitlab": "GitLab",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "ci/cd": "CI/CD",
        "cicd": "CI/CD",
        "llm": "LLM",
        "llms": "LLMs",
        "rag": "RAG",
        "tfidf": "TF-IDF",
        "tf-idf": "TF-IDF",
        "spacy": "spaCy",
        "nltk": "NLTK",
        "bert": "BERT",
        "gpt": "GPT",
        "cnn": "CNN",
        "rnn": "RNN",
        "lstm": "LSTM",
        "clouddata": "Cloud Data",
        "cloud data": "Cloud Data",
        "master's degree": "Master's Degree",
        "masters degree": "Master's Degree",
        "bachelor's degree": "Bachelor's Degree",
        "bachelors degree": "Bachelor's Degree"
    }
    
    if kw_lower in custom_casings:
        return custom_casings[kw_lower]
        
    return kw.title()

def get_metric_context(txt, metric):
    if not txt or not metric:
        return metric
    
    escaped_metric = re.escape(metric)
    match = re.search(escaped_metric, txt, re.IGNORECASE)
    if not match:
        return metric
        
    start, end = match.start(), match.end()
    
    before = txt[max(0, start - 30):start]
    after = txt[end:min(len(txt), end + 25)]
    
    before_segment = re.split(r'[\r\n•\-\*|:;]', before)[-1].strip()
    after_segment = re.split(r'[\r\n•\-\*|:;]', after)[0].strip()
    
    before_words = before_segment.split()
    before_context = " ".join(before_words[-2:]) if len(before_words) > 2 else " ".join(before_words)
    
    after_words = after_segment.split()
    after_context = " ".join(after_words[:2]) if len(after_words) > 2 else " ".join(after_words)
    
    full_context = f"{before_context} {metric} {after_context}".strip()
    
    # Clean up spaces around parentheses and commas
    full_context = re.sub(r'\(\s+', '(', full_context)
    full_context = re.sub(r'\s+\)', ')', full_context)
    full_context = re.sub(r'\s+,\s*', ', ', full_context)
    full_context = re.sub(r'\s+\.\s*', '. ', full_context)
    
    full_context = re.sub(r'\s+', ' ', full_context)
    full_context = re.sub(r'^[\s,.\-:\;\(\)]+|[\s,.\-:\;\(\)]+$', '', full_context)
    
    if len(full_context) > 48:
        full_context = full_context[:45] + "..."
    return full_context

def render_ats_evaluation_tab(data, sel_model, resume_text=None):
    cname = esc(data.get("candidate_name", "Candidate"))
    ats = data.get("ats_score", 0)
    rq_score = data.get("resume_quality_score", 0)
    ir_score = data.get("interview_readiness_score", 0)
    
    hp = data.get("hiring_probability", {})
    hp_ats = hp.get("ats_pass", "Low")

    st.markdown('<div class="line"></div>', unsafe_allow_html=True)
    
    # ─── HEADER ───────────────────────────────────────────────
    st.markdown(f"""<div class="res-header" style="margin-bottom:1.5rem;">
<div class="over">Resume Intelligence</div>
<div class="name">ATS Evaluation Dashboard</div>
</div>""", unsafe_allow_html=True)

    # ─── HIGH-LEVEL KPI METRICS GRID ─────────────────────────
    st.markdown(f"""<div class="metrics-row" style="margin-bottom: 2rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.2rem;">
<div class="m-card" style="border-left: 4px solid #818cf8; background: linear-gradient(135deg, rgba(129, 140, 248, 0.08) 0%, rgba(15, 23, 42, 0.3) 100%); padding: 1.3rem; border-radius: 14px; border: 1px solid rgba(129, 140, 248, 0.2); border-left-width: 4px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 8px 32px 0 rgba(129, 140, 248, 0.06); backdrop-filter: blur(8px);">
<div class="m-label" style="font-size: 0.72rem; color: #a1a1aa; text-transform: uppercase; font-weight: 700; letter-spacing: 0.8px;">ATS Compatibility</div>
<div class="m-num" style="font-size: 1.8rem; font-weight: 900; color: #818cf8; margin: 0.4rem 0;">{ats}%</div>
<div style="height: 4px; background: rgba(255, 255, 255, 0.06); border-radius: 2px; overflow: hidden; margin-bottom: 0.4rem;">
<div style="width: {ats}%; height: 100%; background: #818cf8; border-radius: 2px;"></div>
</div>
<div class="m-sub" style="font-size: 0.68rem; color: #71717a;">Score Match Index</div>
</div>
<div class="m-card" style="border-left: 4px solid #a78bfa; background: linear-gradient(135deg, rgba(167, 139, 250, 0.08) 0%, rgba(15, 23, 42, 0.3) 100%); padding: 1.3rem; border-radius: 14px; border: 1px solid rgba(167, 139, 250, 0.2); border-left-width: 4px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 8px 32px 0 rgba(167, 139, 250, 0.06); backdrop-filter: blur(8px);">
<div class="m-label" style="font-size: 0.72rem; color: #a1a1aa; text-transform: uppercase; font-weight: 700; letter-spacing: 0.8px;">Resume Quality</div>
<div class="m-num" style="font-size: 1.8rem; font-weight: 900; color: #a78bfa; margin: 0.4rem 0;">{rq_score}%</div>
<div style="height: 4px; background: rgba(255, 255, 255, 0.06); border-radius: 2px; overflow: hidden; margin-bottom: 0.4rem;">
<div style="width: {rq_score}%; height: 100%; background: #a78bfa; border-radius: 2px;"></div>
</div>
<div class="m-sub" style="font-size: 0.68rem; color: #71717a;">Content Quality</div>
</div>
<div class="m-card" style="border-left: 4px solid #60a5fa; background: linear-gradient(135deg, rgba(96, 165, 250, 0.08) 0%, rgba(15, 23, 42, 0.3) 100%); padding: 1.3rem; border-radius: 14px; border: 1px solid rgba(96, 165, 250, 0.2); border-left-width: 4px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 8px 32px 0 rgba(96, 165, 250, 0.06); backdrop-filter: blur(8px);">
<div class="m-label" style="font-size: 0.72rem; color: #a1a1aa; text-transform: uppercase; font-weight: 700; letter-spacing: 0.8px;">Interview Readiness</div>
<div class="m-num" style="font-size: 1.8rem; font-weight: 900; color: #60a5fa; margin: 0.4rem 0;">{ir_score}%</div>
<div style="height: 4px; background: rgba(255, 255, 255, 0.06); border-radius: 2px; overflow: hidden; margin-bottom: 0.4rem;">
<div style="width: {ir_score}%; height: 100%; background: #60a5fa; border-radius: 2px;"></div>
</div>
<div class="m-sub" style="font-size: 0.68rem; color: #71717a;">{s_label(ir_score)}</div>
</div>
<div class="m-card" style="border-left: 4px solid #34d399; background: linear-gradient(135deg, rgba(52, 211, 153, 0.08) 0%, rgba(15, 23, 42, 0.3) 100%); padding: 1.3rem; border-radius: 14px; border: 1px solid rgba(52, 211, 153, 0.2); border-left-width: 4px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 8px 32px 0 rgba(52, 211, 153, 0.06); backdrop-filter: blur(8px);">
<div class="m-label" style="font-size: 0.72rem; color: #a1a1aa; text-transform: uppercase; font-weight: 700; letter-spacing: 0.8px;">ATS Pass Rate</div>
<div class="m-num" style="font-size: 1.8rem; font-weight: 900; color: #34d399; margin: 0.4rem 0;">{hp_ats}</div>
<div style="height: 4px; background: rgba(255, 255, 255, 0.06); border-radius: 2px; overflow: hidden; margin-bottom: 0.4rem;">
<div style="width: {'90%' if hp_ats == 'High' else '60%' if hp_ats == 'Medium' else '30%'}; height: 100%; background: #34d399; border-radius: 2px;"></div>
</div>
<div class="m-sub" style="font-size: 0.68rem; color: #71717a;">Estimated Likelihood</div>
</div>
</div>""", unsafe_allow_html=True)

    # ─── ATS SCREENING SIMULATION BANNER ──────────────────────
    bd = data.get("score_breakdown", {})
    if ats >= 75:
        pass_reasons = []
        if bd.get("skills", 0) >= 70:
            pass_reasons.append("<strong>Strong Keyword Alignment:</strong> High semantic overlap with critical technical stack requirements.")
        if bd.get("experience", 0) >= 70:
            pass_reasons.append("<strong>Sufficient Experience Depth:</strong> Experience history matches core duties and seniority needs.")
        if bd.get("projects", 0) >= 70:
            pass_reasons.append("<strong>Relevant Project Portfolio:</strong> Project description depth shows practical hands-on capability.")
        if bd.get("formatting", 0) >= 70:
            pass_reasons.append("<strong>ATS Friendly Formatting:</strong> Parser layout check passed without structural layout warnings.")
        
        if not pass_reasons:
            pass_reasons.append("<strong>Composite Quality:</strong> Total evaluation score meets the minimum qualification filter.")
            
        pass_bullets = "".join([f"<li style='margin-bottom:0.4rem;'>{r}</li>" for r in pass_reasons])
        st.markdown(f"""<div style="background:rgba(16,185,129,0.04); border:1px solid rgba(16,185,129,0.18); border-radius:12px; padding:1.4rem; margin-bottom:2rem; box-shadow: 0 4px 20px rgba(16,185,129,0.05);">
<div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.8rem;">
<div style="width:32px; height:32px; border-radius:8px; background:rgba(52,211,153,0.12); display:flex; align-items:center; justify-content:center; font-size:1rem; border:1px solid rgba(52,211,153,0.2);">✅</div>
<div>
<div style="font-weight:700; color:#34d399; font-size:1rem; letter-spacing:0.3px;">Passed Screening — Shortlisted for Interview</div>
<div style="font-size:0.65rem; color:#71717a; text-transform:uppercase; font-weight:600; letter-spacing:0.5px;">ATS Simulation Engine v2.0</div>
</div>
</div>
<p style="font-size: 0.86rem; color: #a1a1aa; margin: 0 0 0.6rem 0;">This candidate has cleared the automated ATS company screening filters. Key qualifying factors:</p>
<ul style="font-size: 0.84rem; color: #d4d4d8; margin: 0; padding-left: 1.2rem; line-height: 1.6;">
{pass_bullets}
</ul>
</div>""", unsafe_allow_html=True)
    else:
        fail_reasons = []
        if bd.get("skills", 0) < 70:
            fail_reasons.append("<strong>Low Keyword Match:</strong> Missing critical technical keywords required by the job description.")
        if bd.get("experience", 0) < 70:
            fail_reasons.append("<strong>Weak Experience Depth:</strong> Resume experience shows insufficient depth or alignment with job requirements.")
        if bd.get("projects", 0) < 70:
            fail_reasons.append("<strong>Portfolio Gap:</strong> Project list lacks relevant tech stack or detailed project impact.")
        if bd.get("formatting", 0) < 70:
            fail_reasons.append("<strong>Formatting Weaknesses:</strong> Formatting structure, design complexity, or readability checks are weak.")
            
        if not fail_reasons:
            fail_reasons.append("<strong>Low Keyword Match:</strong> Combined keyword density fails to meet job threshold parameters.")
            
        fail_bullets = "".join([f"<li style='margin-bottom:0.4rem;'>{r}</li>" for r in fail_reasons])
        st.markdown(f"""<div style="background:rgba(239,68,68,0.04); border:1px solid rgba(239,68,68,0.18); border-radius:12px; padding:1.4rem; margin-bottom:2rem; box-shadow: 0 4px 20px rgba(239,68,68,0.05);">
<div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.8rem;">
<div style="width:32px; height:32px; border-radius:8px; background:rgba(248,113,113,0.12); display:flex; align-items:center; justify-content:center; font-size:1rem; border:1px solid rgba(248,113,113,0.2);">🚫</div>
<div>
<div style="font-weight:700; color:#f87171; font-size:1rem; letter-spacing:0.3px;">Rejected at Screening Stage</div>
<div style="font-size:0.65rem; color:#71717a; text-transform:uppercase; font-weight:600; letter-spacing:0.5px;">ATS Simulation Engine v2.0</div>
</div>
</div>
<p style="font-size: 0.86rem; color: #a1a1aa; margin: 0 0 0.6rem 0;">The candidate did not clear the initial automated ATS company filters. Key reasons for rejection:</p>
<ul style="font-size: 0.84rem; color: #d4d4d8; margin: 0; padding-left: 1.2rem; line-height: 1.6;">
{fail_bullets}
</ul>
</div>""", unsafe_allow_html=True)

    # ─── VISUAL SCORES & STANDING GRID ────────────────────────
    score_color_b = "#4ade80" if ats >= 80 else "#60a5fa" if ats >= 60 else "#fbbf24" if ats >= 40 else "#f87171"
    score_grade = "Excellent" if ats >= 85 else "Strong" if ats >= 75 else "Good" if ats >= 60 else "Needs Work" if ats >= 40 else "Critical"
    
    benchmark = data.get("ats_benchmark", {})
    c_score = ats
    avg_score = benchmark.get("average_score", 65)
    top_score = benchmark.get("top_score", 92)
    ranking = benchmark.get("candidate_ranking", "Top 25%")

    col_visual_l, col_visual_r = st.columns([1, 1], gap="medium")
    
    with col_visual_l:
        # Standing & Benchmark (Combined circular gauge and Pool benchmark)
        st.markdown(f"""<div class="card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between; padding: 1.5rem; margin: 0; box-shadow:0 4px 15px rgba(0,0,0,0.15);">
<div style="display: flex; align-items: center; gap: 1.2rem; margin-bottom: 1.6rem;">
<div style="position: relative; width: 90px; height: 90px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
<svg width="90" height="90" viewBox="0 0 90 90" style="position: absolute; transform: rotate(-90deg); filter: drop-shadow(0 0 6px {score_color_b}33);">
<circle cx="45" cy="45" r="38" stroke="rgba(255,255,255,0.04)" stroke-width="6" fill="transparent" />
<circle cx="45" cy="45" r="38" stroke="{score_color_b}" stroke-width="6" fill="transparent" 
stroke-dasharray="238.7" stroke-dashoffset="{238.7 - (238.7 * ats / 100)}" stroke-linecap="round" />
</svg>
<div style="text-align: center; z-index: 10;">
<span style="font-size: 1.6rem; font-weight: 900; color: {score_color_b}; line-height: 1;">{ats}</span>
<div style="font-size: 0.45rem; color: #71717a; font-weight: 700; text-transform: uppercase; margin-top: 0.05rem; letter-spacing: 0.5px;">out of 100</div>
</div>
</div>
<div>
<div style="font-size: 0.62rem; font-weight: 700; color: #8e9196; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 0.15rem;">Compatibility Rating</div>
<div style="font-size: 1.15rem; font-weight: 800; color: #fafafa; margin-bottom: 0.30rem; letter-spacing:0.2px;">AI Screening Verdict</div>
<span style="display: inline-block; background: {score_color_b}22; color: {score_color_b}; font-size: 0.68rem; font-weight: 800; padding: 0.2rem 0.5rem; border-radius: 4px; border: 1px solid {score_color_b}33; text-transform: uppercase; letter-spacing: 0.5px;">{score_grade}</span>
</div>
</div>

<div style="border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 1.2rem;">
<div class="pc-label" style="font-weight: 700; color: #fafafa; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 1.2rem; display: flex; justify-content: space-between; align-items: center;">
<span>ATS Pool Benchmark</span>
<span style="color: #fbbf24; font-weight: 800; font-size:0.75rem;">{esc(ranking)} Ranking</span>
</div>
<div style="position: relative; height: 6px; background: rgba(255,255,255,0.08); border-radius: 3px; margin: 1.5rem 0 1rem 0;">
<!-- Average Notch -->
<div style="position: absolute; left: {avg_score}%; top: 50%; transform: translate(-50%, -50%); width: 2px; height: 12px; background: rgba(255,255,255,0.4); border-radius: 1px; z-index: 2;"></div>
<!-- Top Notch -->
<div style="position: absolute; left: {top_score}%; top: 50%; transform: translate(-50%, -50%); width: 2px; height: 12px; background: #10b981; border-radius: 1px; z-index: 2;"></div>
<!-- Candidate Fill & Glow Pin -->
<div style="position: absolute; left: 0; width: {c_score}%; height: 100%; background: linear-gradient(90deg, #6366f1, #fbbf24); border-radius: 3px;"></div>
<div style="position: absolute; left: {c_score}%; top: 50%; transform: translate(-50%, -50%); width: 14px; height: 14px; background: #fbbf24; border: 3px solid #0f172a; border-radius: 50%; box-shadow: 0 0 10px #fbbf24; z-index: 3;"></div>
</div>
<!-- Legend Row Below Slider -->
<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1.1rem; padding: 0 0.2rem;">
<div style="display: flex; align-items: center; gap: 0.35rem; font-size: 0.72rem; color: #a1a1aa;">
<span style="width: 8px; height: 8px; background: rgba(255,255,255,0.4); border-radius: 50%;"></span>
<span>Avg Score: <strong>{avg_score}</strong></span>
</div>
<div style="display: flex; align-items: center; gap: 0.35rem; font-size: 0.72rem; color: #fbbf24;">
<span style="width: 8px; height: 8px; background: #fbbf24; border-radius: 50%; box-shadow: 0 0 6px #fbbf24;"></span>
<span>You: <strong>{c_score}</strong></span>
</div>
<div style="display: flex; align-items: center; gap: 0.35rem; font-size: 0.72rem; color: #34d399;">
<span style="width: 8px; height: 8px; background: #10b981; border-radius: 50%;"></span>
<span>Top: <strong>{top_score}</strong></span>
</div>
</div>
</div>""", unsafe_allow_html=True)
        
    with col_visual_r:
        # Radar Chart
        with st.container(border=True):
            st.markdown("""<div class="card-head" style="margin-bottom: 0.6rem; border-bottom:none;">
<div class="icon-box blue">🎯</div><h3 style="margin:0;">Score Breakdown Radar</h3></div>""", unsafe_allow_html=True)
            st.plotly_chart(make_radar(data.get("dimensions", data.get("score_breakdown", {}))), use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # ─── ATS DIMENSION BREAKDOWN & RATIONALE ──────────────────
    dims = data.get("dimensions", {})
    expl = data.get("score_explanation", "")
    if not expl or expl.strip() == "No explanation available.":
        verdict_conclusion = data.get("final_recruiter_verdict", {}).get("conclusion", "")
        if verdict_conclusion and verdict_conclusion != "Not available":
            expl = verdict_conclusion
        else:
            expl = f"The candidate has been evaluated with an overall compatibility score of {ats}/100 based on standard ATS parameters."

    items_html = ""
    if dims and "technical_skills" in dims:
        for icon, label_name, weight, key, color in [
            ("🛠️", "Technical Skills Match", "25%", "technical_skills", "#818cf8"),
            ("💼", "Experience Relevance", "25%", "experience_relevance", "#60a5fa"),
            ("📈", "Leadership & Growth", "15%", "leadership_growth", "#a78bfa"),
            ("🤝", "Cultural Fit", "10%", "cultural_fit", "#34d399"),
            ("📄", "Presentation Quality", "10%", "presentation_quality", "#fb923c"),
            ("🌱", "Sustainability", "10%", "sustainability", "#38bdf8"),
            ("💡", "Innovation & Impact", "5%", "innovation_impact", "#c084fc")
        ]:
            d_val = dims.get(key, {})
            d_score = d_val.get("score", 0)
            d_expl = esc(d_val.get("explanation", "Not available"))
            
            # Highlight positive/negative professional keywords dynamically
            d_expl_formatted = d_expl
            for term in ["lacks", "lacking", "no visible", "does not directly", "does not demonstrate", "weak", "insufficient", "lacks experience", "not in"]:
                d_expl_formatted = re.sub(rf"\b({term})\b", r"<span style='color:#f87171; font-weight:600;'>\1</span>", d_expl_formatted, flags=re.IGNORECASE)
            for term in ["strong", "excellent", "well-structured", "easy to read", "suggest a fit", "skills in", "experience in", "good match", "fits well"]:
                d_expl_formatted = re.sub(rf"\b({term})\b", r"<span style='color:#34d399; font-weight:600;'>\1</span>", d_expl_formatted, flags=re.IGNORECASE)
                
            items_html += f"""<div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.02) 0%, rgba(255, 255, 255, 0.005) 100%); border: 1px solid rgba(255, 255, 255, 0.04); border-left: 4px solid {color}; border-radius: 12px; padding: 1.1rem; margin-bottom: 0.8rem; box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.12); backdrop-filter: blur(4px);">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem; flex-wrap:wrap; gap:0.5rem;">
<div style="display:flex; align-items:center; gap:0.5rem;">
<span style="font-size:1.05rem;">{icon}</span>
<strong style="color:#fafafa; font-size:0.92rem; letter-spacing:0.3px;">{label_name}</strong>
<span style="font-size:0.65rem; color:#a1a1aa; text-transform:uppercase; font-weight:700; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); padding:0.1rem 0.35rem; border-radius:4px; margin-left:0.25rem;">Weight: {weight}</span>
</div>
<span style="font-size:0.76rem; font-weight:800; color:{color}; background:{color}15; border:1px solid {color}25; padding:0.2rem 0.6rem; border-radius:6px; letter-spacing:0.5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">{d_score} / 100</span>
</div>
<div style="height: 6px; background: rgba(255, 255, 255, 0.04); border-radius: 3px; overflow: hidden; margin-bottom: 0.75rem; border: 1px solid rgba(255,255,255,0.02);">
<div style="width: {d_score}%; height: 100%; background: {color}; border-radius: 3px; box-shadow: 0 0 8px {color}aa;"></div>
</div>
<div style="font-size:0.84rem; color:#d4d4d8; line-height:1.6; letter-spacing:0.1px;">{d_expl_formatted}</div>
</div>"""

    st.markdown(f"""<div class="card" style="box-shadow:0 4px 15px rgba(0,0,0,0.1);">
<div class="card-head" style="border-bottom: 1px solid rgba(255, 255, 255, 0.06); padding-bottom: 0.6rem; margin-bottom: 1rem;">
<div class="icon-box purple">🧠</div>
<h3 style="margin:0;">ATS Dimension Breakdown & Rationale</h3>
</div>
{items_html}
</div>""", unsafe_allow_html=True)


    # Profile & Compliance Audit Intelligence variables are defined.
    # They will be rendered in a unified tab block at the bottom after profile HTML is built.

    # ─── SKILLS & KEYWORDS INTELLIGENCE ──────────────────────
    matched = data.get("matched_skills", [])
    critical_miss = data.get("critical_missing_skills", [])
    miss = data.get("missing_skills", [])
    rec_skills = data.get("recommended_skills", [])
    gap_analysis = data.get("skill_gap_analysis", "")
    
    # Missing keywords TF-IDF merging
    missing_kws = data.get("missing_keywords", [])
    
    # Deduplicate lists sequentially:
    # 1. Clean matched skills
    cleaned_matched = []
    for s in matched:
        fmt = format_keyword(s)
        if fmt and fmt not in cleaned_matched:
            cleaned_matched.append(fmt)

    # 2. Clean critical gaps (ensuring they are not in matched)
    cleaned_critical_miss = []
    for s in critical_miss:
        fmt = format_keyword(s)
        if fmt and fmt not in cleaned_critical_miss and fmt not in cleaned_matched:
            cleaned_critical_miss.append(fmt)

    # 3. Clean recommended additions (ensuring they are not in matched or critical gaps)
    cleaned_rec_skills = []
    for s in rec_skills:
        fmt = format_keyword(s)
        if fmt and fmt not in cleaned_rec_skills and fmt not in cleaned_matched and fmt not in cleaned_critical_miss:
            cleaned_rec_skills.append(fmt)

    # 4. Clean general missing keywords (ensuring they are not in matched, critical gaps, or recommended additions)
    cleaned_general_miss = []
    for s in (miss + missing_kws):
        fmt = format_keyword(s)
        if fmt and fmt not in cleaned_general_miss and fmt not in cleaned_matched and fmt not in cleaned_critical_miss and fmt not in cleaned_rec_skills:
            cleaned_general_miss.append(fmt)

    # Matched skills tags categorized systematically
    matched_html = ""
    if cleaned_matched:
        categories = {
            "Programming Languages": [],
            "Frameworks & Libraries": [],
            "Databases & Storage": [],
            "Cloud, DevOps & Tools": [],
            "Other Competencies": []
        }
        
        langs = {"python", "sql", "scala", "r", "java", "c++", "c#", "c", "javascript", "typescript", "html", "css", "go", "golang", "rust", "ruby", "php", "bash", "shell", "js", "ts"}
        frameworks = {"tensorflow", "keras", "pytorch", "scikit-learn", "xgboost", "numpy", "pandas", "spark", "hadoop", "apache hadoop", "pyspark", "flask", "django", "fastapi", "react", "vue", "angular", "node.js", "nodejs", "opencv", "nltk", "spacy", "scipy", "spring", "spring boot", "hibernate"}
        dbs = {"mysql", "postgresql", "mongodb", "cassandra", "redis", "sqlite", "oracle", "mariadb", "dynamodb", "elasticsearch", "neo4j", "db2", "database", "databases", "nosql"}
        cloud_devops = {"aws", "amazon web services", "gcp", "google cloud", "google cloud platform", "azure", "docker", "kubernetes", "git", "github", "gitlab", "jenkins", "ansible", "terraform", "ci/cd", "cicd", "jupyter", "jupyter notebook", "conda", "linux", "unix", "jira", "confluence"}
        
        for s in cleaned_matched:
            s_lower = s.lower().strip()
            if s_lower in langs or any(x == s_lower for x in ["c++", "c#", "js", "ts"]):
                categories["Programming Languages"].append(s)
            elif s_lower in dbs or "database" in s_lower:
                categories["Databases & Storage"].append(s)
            elif s_lower in frameworks or "spark" in s_lower or "hadoop" in s_lower or "react" in s_lower:
                categories["Frameworks & Libraries"].append(s)
            elif s_lower in cloud_devops or "cloud" in s_lower or "docker" in s_lower or "kubernetes" in s_lower or "aws" in s_lower or "gcp" in s_lower or "azure" in s_lower or "git" in s_lower:
                categories["Cloud, DevOps & Tools"].append(s)
            else:
                categories["Other Competencies"].append(s)
                
        cat_blocks = []
        for cat_name, cat_skills in categories.items():
            if cat_skills:
                chips_str = "".join([f'<span class="t t-green" style="margin-right:0.3rem; margin-bottom:0.35rem; display:inline-block; font-size:0.75rem;">{esc(s)}</span>' for s in cat_skills])
                # Constructed as a single line to prevent Markdown parsing as an indented code block
                cat_blocks.append(f'<div style="margin-bottom:0.6rem;"><div style="font-size:0.68rem; color:#71717a; text-transform:uppercase; font-weight:700; margin-bottom:0.2rem; letter-spacing:0.5px;">{cat_name}</div><div class="tag-wrap">{chips_str}</div></div>')
        matched_html = "".join(cat_blocks)
    else:
        matched_html = '<div style="color:#52525b;font-size:0.8rem;margin-top: 0.4rem;">No matched skills identified.</div>'

    # Critical gaps tags
    crit_html = ""
    if cleaned_critical_miss:
        chips_str = "".join([f'<span class="t t-red" style="background:rgba(239,68,68,0.15); font-weight:700; margin-right:0.3rem; margin-bottom:0.35rem; display:inline-block; font-size:0.75rem;">{esc(s)}</span>' for s in cleaned_critical_miss])
        crit_html = f'<div class="tag-wrap" style="margin-top: 0.2rem;">{chips_str}</div>'
    else:
        crit_html = '<div style="color:#34d399; font-size:0.84rem; font-weight:600; padding: 0.2rem 0; display:flex; align-items:center; gap:0.4rem;">🎉 Perfect Match! No critical missing requirements.</div>'

    # General missing skills + TF-IDF keywords tags
    miss_html = ""
    if cleaned_general_miss:
        chips_str = "".join([f'<span class="t t-orange" style="margin-right:0.3rem; margin-bottom:0.35rem; display:inline-block; font-size:0.75rem;">{esc(s)}</span>' for s in cleaned_general_miss])
        miss_html = f'<div class="tag-wrap" style="margin-top: 0.2rem;">{chips_str}</div>'
    else:
        miss_html = '<div style="color:#a1a1aa; font-size:0.82rem; padding: 0.2rem 0; font-style:italic;">✨ All parsed general keywords are matched.</div>'

    # Recommended skills tags
    rec_html = ""
    if cleaned_rec_skills:
        chips_str = "".join([f'<span class="t t-purple" style="margin-right:0.3rem; margin-bottom:0.35rem; display:inline-block; font-size:0.75rem;">{esc(s)}</span>' for s in cleaned_rec_skills])
        rec_html = f'<div class="tag-wrap" style="margin-top: 0.2rem;">{chips_str}</div>'
    else:
        rec_html = '<div style="color:#a1a1aa; font-size:0.82rem; padding: 0.2rem 0; font-style:italic;">👍 Profile covers all recommended upskilling keywords.</div>'

    st.markdown(f"""<div class="card">
<div class="card-head" style="border-bottom: 1px solid rgba(255, 255, 255, 0.06); padding-bottom: 0.6rem; margin-bottom: 1.2rem;">
<div class="icon-box blue">🔍</div>
<h3 style="margin:0;">Skills & Keywords Intelligence</h3>
</div>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.2rem; margin-bottom: 1rem;">
<!-- Left Column: Matched & Upskilling -->
<div style="display: flex; flex-direction: column; gap: 1rem;">
<div style="background: rgba(255,255,255,0.015); border: 1px solid rgba(255, 255, 255, 0.06); border-left: 4px solid #10b981; border-radius: 12px; padding: 1.2rem; flex-grow: 1;">
<div style="display: flex; align-items: center; gap: 0.4rem; font-size: 0.88rem; font-weight: 800; color: #10b981; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.8rem; border-bottom: 1px solid rgba(16, 185, 129, 0.1); padding-bottom: 0.4rem;">
✅ Matched Skills
</div>
{matched_html}
</div>
<div style="background: rgba(255,255,255,0.015); border: 1px solid rgba(255, 255, 255, 0.06); border-left: 4px solid #a78bfa; border-radius: 12px; padding: 1.2rem; flex-grow: 1;">
<div style="display: flex; align-items: center; gap: 0.4rem; font-size: 0.88rem; font-weight: 800; color: #a78bfa; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.8rem; border-bottom: 1px solid rgba(167, 139, 250, 0.1); padding-bottom: 0.4rem;">
💡 Recommended Upskilling Additions
</div>
{rec_html}
</div>
</div>

<!-- Right Column: Critical & General Missing -->
<div style="display: flex; flex-direction: column; gap: 1rem;">
<div style="background: rgba(255,255,255,0.015); border: 1px solid rgba(255, 255, 255, 0.06); border-left: 4px solid #f87171; border-radius: 12px; padding: 1.2rem; flex-grow: 1;">
<div style="display: flex; align-items: center; gap: 0.4rem; font-size: 0.88rem; font-weight: 800; color: #f87171; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.8rem; border-bottom: 1px solid rgba(248, 113, 113, 0.1); padding-bottom: 0.4rem;">
⚠️ Critical Missing Requirements
</div>
{crit_html}
</div>
<div style="background: rgba(255,255,255,0.015); border: 1px solid rgba(255, 255, 255, 0.06); border-left: 4px solid #fb923c; border-radius: 12px; padding: 1.2rem; flex-grow: 1;">
<div style="display: flex; align-items: center; gap: 0.4rem; font-size: 0.88rem; font-weight: 800; color: #fb923c; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.8rem; border-bottom: 1px solid rgba(251, 146, 60, 0.1); padding-bottom: 0.4rem;">
❌ Missing General Keywords (TF-IDF)
</div>
{miss_html}
</div>
</div>
</div>
<div class="profile-cell" style="background: rgba(255, 255, 255, 0.015); border: 1px solid rgba(255, 255, 255, 0.05); margin-top: 0.8rem;">
<div class="pc-label" style="color:#fb923c; font-weight:700;">Skill Gap Impact Critique</div>
<div class="pc-text" style="color:#e4e4e7; font-size:0.86rem; line-height:1.6;">{esc(gap_analysis) if gap_analysis else "The candidate's score indicates a moderate match. Key gaps should be bridged through targeted upskilling projects."}</div>
</div>
</div>""", unsafe_allow_html=True)

    # ─── PARSED CANDIDATE PROFILE (Consolidated Summary) ──────
    prof = data.get("profile_summary", {})
    parsed_d = data.get("parsed_data", {})
    edu_list = parsed_d.get("education", [])
    proj_list = parsed_d.get("projects", [])
    exp_list = parsed_d.get("experience", [])

    exp_summary_val = esc(prof.get("experience_summary", "Not available"))
    edu_summary_val = esc(prof.get("education_summary", "Not available"))
    proj_summary_val = esc(prof.get("projects_summary", "Not available"))

    # Structured Experience
    exp_html = ""
    if exp_list:
        for i, exp in enumerate(exp_list):
            comp = esc(exp.get("company", ""))
            role = esc(exp.get("role", ""))
            dur = esc(exp.get("duration", ""))
            summary = esc(exp.get("summary", ""))
            
            summary_html = ""
            if summary:
                bullets = [b.strip() for b in re.split(r'[\r\n•\-\*|]+', summary) if b.strip()]
                if len(bullets) > 1:
                    li_items = "".join([f"<li style='margin-bottom:0.25rem; font-size:0.8rem; color:#d4d4d8;'>{b}</li>" for b in bullets])
                    summary_html = f"<ul style='margin: 0.3rem 0 0 0; padding-left: 1.1rem; line-height: 1.45; list-style-type: disc;'>{li_items}</ul>"
                else:
                    summary_html = f"<div style='font-size:0.8rem; color:#d4d4d8; line-height: 1.45; margin-top:0.2rem;'>{summary}</div>"
            
            border_style = "border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.8rem; margin-bottom: 0.8rem;" if i < len(exp_list) - 1 else ""
            exp_html += f"""<div style="{border_style}">
<div style="display:flex; justify-content:space-between; align-items:baseline; gap: 0.5rem; margin-bottom:0.2rem;">
<span style="font-weight:700; color:#fafafa; font-size:0.88rem;">{role}</span>
<span style="font-size:0.72rem; color:#a1a1aa; white-space:nowrap; font-weight:500;">{dur}</span>
</div>
<div style="font-size:0.8rem; color:#818cf8; font-weight:600; margin-bottom:0.3rem;">{comp}</div>
{summary_html}
</div>"""
    else:
        exp_html = f"<div style='font-size:0.82rem; color:#d4d4d8; line-height:1.5;'>{exp_summary_val}</div>"

    # Structured Education
    edu_html = ""
    if edu_list:
        for i, edu in enumerate(edu_list):
            inst = esc(edu.get("institution", ""))
            deg = esc(edu.get("degree", ""))
            gpa = esc(edu.get("gpa", ""))
            yrs = esc(edu.get("years", ""))
            
            border_style = "border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.8rem; margin-bottom: 0.8rem;" if i < len(edu_list) - 1 else ""
            gpa_html = f"<span style='background:rgba(52,211,153,0.1); color:#34d399; font-size:0.7rem; font-weight:700; padding:0.1rem 0.45rem; border-radius:4px; margin-left:0.5rem;'>GPA: {gpa}</span>" if gpa else ""
            
            edu_html += f"""<div style="{border_style}">
<div style="display:flex; justify-content:space-between; align-items:baseline; gap: 0.5rem; margin-bottom:0.2rem;">
<span style="font-weight:700; color:#fafafa; font-size:0.88rem;">{deg}</span>
<span style="font-size:0.72rem; color:#a1a1aa; white-space:nowrap; font-weight:500;">{yrs}</span>
</div>
<div style="font-size:0.8rem; color:#60a5fa; font-weight:600; margin-bottom:0.3rem;">{inst} {gpa_html}</div>
</div>"""
    else:
        edu_html = f"<div style='font-size:0.82rem; color:#d4d4d8; line-height:1.5;'>{edu_summary_val}</div>"

    # Structured Projects
    proj_html = ""
    if proj_list:
        for i, proj in enumerate(proj_list):
            title = esc(proj.get("title", ""))
            desc = esc(proj.get("description", ""))
            techs = proj.get("technologies", [])
            
            techs_chips = "".join([f'<span class="t t-blue" style="font-size:0.65rem; padding:0.1rem 0.35rem; margin-right:0.25rem; margin-top:0.25rem; display:inline-block;">{esc(t)}</span>' for t in techs])
            border_style = "border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.8rem; margin-bottom: 0.8rem;" if i < len(proj_list) - 1 else ""
            
            proj_html += f"""<div style="{border_style}">
<div style="font-weight:700; color:#fafafa; font-size:0.88rem; margin-bottom:0.2rem;">{title}</div>
<div style="font-size:0.8rem; color:#d4d4d8; line-height:1.45; margin-bottom:0.3rem;">{desc}</div>
<div class="tag-wrap" style="margin-top:0.2rem;">{techs_chips}</div>
</div>"""
    else:
        proj_html = f"<div style='font-size:0.82rem; color:#d4d4d8; line-height:1.5;'>{proj_summary_val}</div>"

    # ─── DYNAMIC AUDIT CALCULATIONS (Contact, Sections, Metrics, Readability, Certifications) ───
    txt = resume_text or ""
    
    # 1. Contact Information Audit Extractor
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', txt)
    email_val = email_match.group(0) if email_match else ""
    
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s\(\)]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}', txt)
    phone_val = phone_match.group(0) if phone_match else ""
    
    linkedin_match = re.search(r'(?:linkedin\.com/in/|linkedin\.com/pub/)[a-zA-Z0-9%_-]+', txt, re.IGNORECASE)
    linkedin_val = linkedin_match.group(0) if linkedin_match else ""
    
    github_match = re.search(r'github\.com/[a-zA-Z0-9%_-]+', txt, re.IGNORECASE)
    github_val = github_match.group(0) if github_match else ""
    
    def make_contact_row(label, val, is_url=False):
        if val:
            display_val = val
            if is_url:
                val_url = val if val.lower().startswith("http") else "https://" + val
                display_html = f'<a href="{val_url}" target="_blank" style="color:#60a5fa; text-decoration:none; font-size:0.75rem; word-break:break-all; font-weight:600;">{esc(display_val)}</a>'
            else:
                display_html = f'<span style="color:#e4e4e7; font-size:0.75rem; font-weight:600;">{esc(display_val)}</span>'
                
            return f"""<div style="padding:0.45rem 0; border-bottom:1px solid rgba(255,255,255,0.03);">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.15rem;">
<span style="font-size:0.8rem; color:#a1a1aa; font-weight:500;">{label}</span>
<span style="background:rgba(52,211,153,0.1); color:#34d399; font-size:0.65rem; font-weight:700; padding:0.1rem 0.40rem; border-radius:4px;">✓ Found</span>
</div>
<div style="margin-top: 0.1rem;">{display_html}</div>
</div>"""
        else:
            return f"""<div style="padding:0.45rem 0; border-bottom:1px solid rgba(255,255,255,0.03); display:flex; justify-content:space-between; align-items:center;">
<span style="font-size:0.8rem; color:#a1a1aa; font-weight:500;">{label}</span>
<span style="background:rgba(244,63,94,0.1); color:#f43f5e; font-size:0.65rem; font-weight:700; padding:0.1rem 0.40rem; border-radius:4px;">✗ Missing</span>
</div>"""

    contact_html = f"""<div style="display:flex; flex-direction:column; gap:0.4rem;">
{make_contact_row("Email Address", email_val)}
{make_contact_row("Phone Number", phone_val)}
{make_contact_row("LinkedIn URL", linkedin_val, is_url=True)}
{make_contact_row("GitHub URL", github_val, is_url=True)}
</div>"""

    # 2. Standard Resume Sections Audit Check
    def make_section_row(label, has_section, count_info):
        if has_section:
            return f"""<div style="padding:0.45rem 0; border-bottom:1px solid rgba(255,255,255,0.03); display:flex; justify-content:space-between; align-items:center;">
<span style="font-size:0.8rem; color:#a1a1aa; font-weight:500;">{label}</span>
<span style="background:rgba(52,211,153,0.1); color:#34d399; font-size:0.65rem; font-weight:700; padding:0.1rem 0.40rem; border-radius:4px;">✓ Found ({count_info})</span>
</div>"""
        else:
            return f"""<div style="padding:0.45rem 0; border-bottom:1px solid rgba(255,255,255,0.03); display:flex; justify-content:space-between; align-items:center;">
<span style="font-size:0.8rem; color:#a1a1aa; font-weight:500;">{label}</span>
<span style="background:rgba(244,63,94,0.1); color:#f43f5e; font-size:0.65rem; font-weight:700; padding:0.1rem 0.40rem; border-radius:4px;">✗ Missing</span>
</div>"""

    sections_html = f"""<div style="display:flex; flex-direction:column; gap:0.4rem;">
{make_section_row("Experience Section", bool(exp_list), f"{len(exp_list)} entries")}
{make_section_row("Education Section", bool(edu_list), f"{len(edu_list)} entries")}
{make_section_row("Skills Section", bool(cleaned_matched), f"{len(cleaned_matched)} keywords")}
{make_section_row("Projects Section", bool(proj_list), f"{len(proj_list)} entries")}
</div>"""

    # 3. Performance Metrics Density Counter
    metrics_found = []
    if txt:
        # Match percentages, currencies, multipliers, counts with plus (e.g. 10M+, 5+), scale numbers (e.g. 10k, 5M), or scale words
        patterns = [
            r'\b\d+(?:\.\d+)?%',  # 23%
            r'[$\u20B9\u00A3\u20AC\u00A5]\d+(?:\.\d+)?[KkMmBb]?(?:\b|\s)',  # $10k
            r'\b\d+(?:\.\d+)?x\b',  # 2x
            r'\b\d+(?:\.\d+)?[KkMmBb]?\++',  # 5+, 10M+
            r'\b\d+[KkMmBb]\b',  # 10k, 5M
            r'\b\d+(?:\.\d+)?\s*(?:million|billion|lakh|lakhs|crore|crores|percent|users|clients|employees|fold)\b'  # 10 million
        ]
        
        for pat in patterns:
            matches = re.findall(pat, txt, re.IGNORECASE)
            for m in matches:
                m_clean = m.strip()
                # Clean up punctuation around the metric match
                m_clean = re.sub(r'^[^\w$%₹+]+|[^\w$%₹+]+$', '', m_clean)
                
                # Filter out standard calendar years (1990-2030)
                if m_clean.isdigit() and 1990 <= int(m_clean) <= 2030:
                    continue
                    
                # Skip if it is a phone number (e.g. 7 digits or more without prefixes/suffixes)
                digits_only = re.sub(r'\D', '', m_clean)
                if len(digits_only) >= 7:
                    continue
                    
                if m_clean and m_clean not in metrics_found:
                    metrics_found.append(m_clean)
                
    m_count = len(metrics_found)
    
    # 3.1 Classify Metrics into Categories
    def classify_metric(context, metric):
        ctx_lower = context.lower()
        m_lower = metric.lower()
        if any(w in ctx_lower for w in ["increase", "growth", "grow", "boost", "revenue", "sale", "profit", "uplift", "improve", "optimize", "better", "faster", "higher", "more"]):
            if "%" in m_lower or "percent" in ctx_lower:
                return "Growth & Impact", "📈", "#34d399", "rgba(52,211,153,0.06)", "rgba(52,211,153,0.18)"
        if any(w in ctx_lower for w in ["reduce", "decrease", "churn", "cost", "time", "latency", "error", "saving", "save", "cut", "drop", "minimize", "less"]):
            return "Efficiency & Optimization", "⚡", "#a78bfa", "rgba(167,139,250,0.06)", "rgba(167,139,250,0.18)"
        if any(w in ctx_lower for w in ["accuracy", "precision", "f1", "recall", "auc", "error rate", "model", "test", "coverage", "score", "metric"]):
            return "Accuracy & Quality", "🎯", "#60a5fa", "rgba(96,165,250,0.06)", "rgba(96,165,250,0.18)"
        if any(sym in m_lower for sym in ["$", "₹", "£", "€", "¥"]) or any(w in ctx_lower for w in ["budget", "dollar", "rupee", "cost", "value"]):
            return "Financial & Scale", "💼", "#fb923c", "rgba(251,146,60,0.06)", "rgba(251,146,60,0.18)"
        if any(w in ctx_lower for w in ["user", "client", "customer", "member", "visitor", "download", "database", "record", "request", "server", "node", "document", "file", "transaction"]):
            return "Scale & Scope", "🌐", "#fb7171", "rgba(248,113,113,0.06)", "rgba(248,113,113,0.18)"
        if "%" in m_lower:
            return "Growth & Impact", "📈", "#34d399", "rgba(52,211,153,0.06)", "rgba(52,211,153,0.18)"
        return "Scale & Scope", "🌐", "#fb7171", "rgba(248,113,113,0.06)", "rgba(248,113,113,0.18)"

    categorized_metrics = {}
    for m in metrics_found[:6]:
        context = get_metric_context(txt, m)
        cat_name, cat_emoji, cat_color, cat_bg, cat_border = classify_metric(context, m)
        if cat_name not in categorized_metrics:
            categorized_metrics[cat_name] = []
        categorized_metrics[cat_name].append((m, context, cat_emoji, cat_color, cat_bg, cat_border))

    metrics_chips = ""
    if categorized_metrics:
        group_html = []
        for cat, items in categorized_metrics.items():
            _, cat_emoji, cat_color, cat_bg, cat_border = items[0][2], items[0][2], items[0][3], items[0][4], items[0][5]
            chips = "".join([
                f'<span style="background:{bg}; color:{color}; font-size:0.68rem; font-weight:600; padding:0.2rem 0.5rem; border-radius:5px; border:1px solid {border}; display:inline-block; margin-bottom:0.3rem; margin-right:0.3rem; line-height:1.4;" title="{esc(m)}">{esc(ctx)}</span>'
                for m, ctx, emoji, color, bg, border in items
            ])
            group_html.append(f"""
<div style="margin-top: 0.6rem; border-top: 1px solid rgba(255,255,255,0.04); padding-top: 0.5rem;">
<div style="font-size:0.7rem; font-weight:800; color:{cat_color}; margin-bottom:0.3rem; display:flex; align-items:center; gap:0.25rem; text-transform:uppercase; letter-spacing:0.5px;">
<span>{cat_emoji}</span><span>{cat}</span>
</div>
<div style="display:flex; flex-wrap:wrap; gap:0.1rem;">{chips}</div>
</div>
""")
        metrics_chips = "".join(group_html)
    else:
        metrics_chips = '<div style="color:#71717a; font-size:0.75rem; font-style:italic; margin-top:0.6rem;">No explicit quantifiable metrics detected.</div>'
        
    if m_count >= 10:
        m_rating = "Excellent"
        m_color = "#34d399"
        metrics_density_desc = "Excellent metrics density. Highly data-driven achievements help stand out to hiring managers."
    elif m_count >= 6:
        m_rating = "Strong"
        m_color = "#60a5fa"
        metrics_density_desc = "Strong metrics density. Good use of quantifiable metrics to validate your work impact."
    elif m_count >= 3:
        m_rating = "Good"
        m_color = "#fb923c"
        metrics_density_desc = "Good metrics density, but could be improved. Try adding more metrics to your projects & experiences."
    else:
        m_rating = "Weak"
        m_color = "#f43f5e"
        metrics_density_desc = "Few or no quantifiable metrics detected. We recommend adding numbers, percentages, or scale metrics."

    # 4. Word Count & Readability Average Sentence Length (ASL)
    w_count = len(txt.split())
    sentences = [s.strip() for s in re.split(r'[.!?\n]+', txt) if len(s.strip()) > 5]
    total_sentences = len(sentences)
    asl = w_count / max(1, total_sentences)
    
    if asl < 12:
        asl_desc = f"Avg Sentence: {asl:.1f} words. Sentences are concise and easy to read, highlighting direct achievements."
    elif asl <= 18:
        asl_desc = f"Avg Sentence: {asl:.1f} words. Sentences are professionally balanced with good structure."
    elif asl <= 24:
        asl_desc = f"Avg Sentence: {asl:.1f} words. Some sentences are long and could be split to improve readability."
    else:
        asl_desc = f"Avg Sentence: {asl:.1f} words. Sentences are too long or nested, making parsing difficult."

    if w_count < 150:
        w_status = "Too Short"
        w_color = "#f43f5e"
        word_count_desc = f"Too short for a comprehensive review. {asl_desc}"
    elif w_count > 1000:
        w_status = "Too Verbose"
        w_color = "#fb923c"
        word_count_desc = f"Very long. Consider condensing content to keep under 2 pages. {asl_desc}"
    else:
        w_status = "Optimal"
        w_color = "#34d399"
        word_count_desc = f"Optimal word density for a 1-2 page professional resume. {asl_desc}"

    # 5. Certifications & Credentials Parser
    certifications = []
    if txt:
        lines = [line.strip() for line in txt.split('\n') if line.strip()]
        cert_keywords = ["certified", "certification", "credential", "certificate", "udemy", "coursera", "nptel", "diploma", "nanodegree", "hackerrank", "oracle", "cisco", "redhat", "aws", "salesforce", "pmi", "pmp", "scrum", "agile", "mit", "harvard", "meta", "linkedin", "nvidia", "linux foundation", "togaf", "comptia", "kubernetes"]
        noise_headers = {
            "certifications", "certification", "credentials", "credential", 
            "certificates", "courses", "licenses", "licenses & certifications", 
            "education & certifications", "awards & certifications", 
            "key certifications", "professional certifications", "additional certifications",
            "online certifications", "other certifications", "academic certifications", "my certifications",
            "certification training"
        }
        for line in lines:
            cleaned_line = re.sub(r'^[^a-zA-Z0-9(]+', '', line).strip()
            cleaned_line = re.sub(r':+$', '', cleaned_line).strip()
            cleaned_lower = cleaned_line.lower()
            
            if not cleaned_line or len(cleaned_line) < 4:
                continue
                
            if cleaned_lower in noise_headers:
                continue
                
            if any(word in cleaned_lower for word in ["tools &", "skills", "technologies", "platforms", "languages", "technical stack", "frameworks", "core competencies"]):
                continue
                
            if any(kw in cleaned_lower for kw in cert_keywords):
                if cleaned_lower in ["certifications:", "certification:", "credentials:", "licenses:", "courses:", "other achievements:", "certifications & credentials"]:
                    continue
                if len(cleaned_line.split()) < 2:
                    continue
                if cleaned_line not in certifications:
                    certifications.append(cleaned_line)
                    
    cert_items_html = []
    if certifications:
        for cert in certifications[:4]:
            platform = "Independent"
            c_lower = cert.lower()
            for p in ["aws", "google", "microsoft", "azure", "gcp", "ibm", "cisco", "oracle", "coursera", "udemy", "nptel", "hackerrank", "freecodecamp", "stanford", "red hat", "salesforce", "pmi", "scrum alliance", "comptia", "meta", "nvidia"]:
                if p in c_lower:
                    platform = p.upper() if p in ["aws", "gcp", "ibm", "nptel", "pmi"] else p.title()
                    break
                    
            skill = "Technical"
            for s in ["python", "sql", "machine learning", "deep learning", "data science", "cloud", "devops", "kubernetes", "docker", "security", "cybersecurity", "web development", "javascript", "react", "java", "artificial intelligence", "ai", "project management", "agile", "scrum", "cloud practitioner", "solutions architect"]:
                if s in c_lower:
                    skill = s.title()
                    break
            if skill == "Technical":
                if "developer" in c_lower:
                    skill = "Developer"
                elif "architect" in c_lower:
                    skill = "Architecture"
                elif "analyst" in c_lower:
                    skill = "Analysis"
                    
            year = ""
            year_match = re.search(r'\b(20\d{2})\b', cert)
            if year_match:
                year = year_match.group(1)
                
            title = cert
            if year:
                title = re.sub(rf'\b{year}\b', '', title)
            title = re.sub(r'[\(\)\|\[\]\-\:]', ' ', title)
            title = re.sub(r'\s+', ' ', title).strip()
            
            if len(title) > 55:
                title = title[:52] + "..."
                
            badges = []
            badges.append(f'<span style="font-size:0.65rem; font-weight:700; color:#818cf8; background:rgba(129,140,248,0.12); padding:0.12rem 0.45rem; border-radius:4px; border:1px solid rgba(129,140,248,0.2);">🏢 Issuer: {esc(platform)}</span>')
            badges.append(f'<span style="font-size:0.65rem; font-weight:700; color:#34d399; background:rgba(52,211,153,0.12); padding:0.12rem 0.45rem; border-radius:4px; border:1px solid rgba(52,211,153,0.2);">🎯 Skill: {esc(skill)}</span>')
            if year:
                badges.append(f'<span style="font-size:0.65rem; font-weight:700; color:#fb923c; background:rgba(251,146,60,0.1); padding:0.12rem 0.45rem; border-radius:4px; border:1px solid rgba(251,146,60,0.15);">📅 Year: {esc(year)}</span>')
                
            badges_html = f'<div style="display:flex; gap:0.35rem; margin-top:0.45rem; flex-wrap:wrap;">{"".join(badges)}</div>'
            
            cert_items_html.append(f"""<div style="margin-bottom:0.6rem; padding:0.7rem 0.9rem; background:linear-gradient(135deg, rgba(167, 139, 250, 0.05) 0%, rgba(15, 23, 42, 0.25) 100%); border:1px solid rgba(167,139,250,0.15); border-left:3.5px solid #a78bfa; border-radius:8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
<div style="font-weight:700; font-size:0.82rem; color:#fafafa; line-height:1.4;">{esc(title)}</div>
{badges_html}
</div>""")

    cert_html = ""
    if cert_items_html:
        cert_html = "".join(cert_items_html)
    else:
        cert_html = f"""<div style="padding:0.6rem 0.8rem; background:rgba(255,255,255,0.01); border:1px solid rgba(255,255,255,0.03); border-radius:8px; font-size:0.82rem; color:#a1a1aa; line-height:1.5;">
❌ No certifications detected.<br/>
<span style="font-size:0.75rem; color:#71717a; display:inline-block; margin-top:0.4rem;">Consider acquiring and adding cloud, tech, or professional certificates (e.g. AWS, GCP, NPTEL) to boost credibility.</span>
</div>"""

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    st.markdown("""<div class="card-head" style="margin-bottom: 0.8rem;">
        <div class="icon-box purple">🔍</div>
        <h3 style="margin:0;">Profile & Compliance Audit Intelligence</h3>
    </div>""", unsafe_allow_html=True)
    
    audit_tab1, audit_tab2 = st.tabs([
        "🔍 ATS Structural & Compliance Audit",
        "👤 Parsed Candidate Profile Details"
    ])
    
    with audit_tab1:
        st.markdown(f"""<div class="card" style="box-shadow:0 4px 15px rgba(0,0,0,0.15); margin-top: 0.5rem; border: none; padding: 0; background: transparent;">
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1.2rem; align-items: stretch;">
<div class="profile-cell" style="margin:0; background: linear-gradient(180deg, rgba(129, 140, 248, 0.04) 0%, rgba(15, 23, 42, 0.3) 100%); border: 1px solid rgba(129, 140, 248, 0.15); border-left: 4px solid #818cf8; border-radius: 12px; padding: 1.2rem; height: 100%; box-sizing: border-box; display: flex; flex-direction: column; justify-content: flex-start;">
<div class="pc-label" style="color:#818cf8; font-weight:800; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.5px;">📇 Contact Information Audit</div>
<div style="margin-top:0.6rem; flex-grow: 1;">{contact_html}</div>
</div>
<div class="profile-cell" style="margin:0; background: linear-gradient(180deg, rgba(167, 139, 250, 0.04) 0%, rgba(15, 23, 42, 0.3) 100%); border: 1px solid rgba(167, 139, 250, 0.15); border-left: 4px solid #a78bfa; border-radius: 12px; padding: 1.2rem; height: 100%; box-sizing: border-box; display: flex; flex-direction: column; justify-content: flex-start;">
<div class="pc-label" style="color:#a78bfa; font-weight:800; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.5px;">🗂️ Standard Resume Sections</div>
<div style="margin-top:0.6rem; flex-grow: 1;">{sections_html}</div>
</div>
<div class="profile-cell" style="margin:0; background: linear-gradient(180deg, rgba(251, 146, 60, 0.04) 0%, rgba(15, 23, 42, 0.3) 100%); border: 1px solid rgba(251, 146, 60, 0.15); border-left: 4px solid #fb923c; border-radius: 12px; padding: 1.2rem; height: 100%; box-sizing: border-box; display: flex; flex-direction: column; justify-content: flex-start;">
<div>
<div class="pc-label" style="color:#fb923c; font-weight:800; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.5px;">📊 Performance Metrics Density</div>
<div style="display:flex; align-items:baseline; gap:0.4rem; margin:0.6rem 0 0.2rem 0;">
<span style="font-size:2.2rem; font-weight:900; color:{m_color}; text-shadow: 0 0 10px rgba(251,146,60,0.15); line-height:1;">{m_count}</span>
<span style="font-size:0.78rem; color:#a1a1aa; font-weight:600;">Metrics Found</span>
</div>
<div style="margin-bottom:0.6rem; display:inline-block;">
<span style="background:rgba(251,146,60,0.1); color:{m_color}; font-size:0.68rem; font-weight:800; padding:0.15rem 0.5rem; border-radius:4px; border:1px solid rgba(251,146,60,0.15); text-transform:uppercase; letter-spacing:0.5px;">Rating: {m_rating}</span>
</div>
<p style="font-size:0.8rem; color:#a1a1aa; margin:0; line-height:1.5;">{metrics_density_desc}</p>
{metrics_chips}
</div>
</div>
<div class="profile-cell" style="margin:0; background: linear-gradient(180deg, rgba(52, 211, 153, 0.04) 0%, rgba(15, 23, 42, 0.3) 100%); border: 1px solid rgba(52, 211, 153, 0.15); border-left: 4px solid #34d399; border-radius: 12px; padding: 1.2rem; height: 100%; box-sizing: border-box; display: flex; flex-direction: column; justify-content: flex-start;">
<div>
<div class="pc-label" style="color:#34d399; font-weight:800; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.5px;">📝 Resume Length & Word Count</div>
<div style="display:flex; align-items:baseline; gap:0.4rem; margin:0.6rem 0 0.2rem 0;">
<span style="font-size:2.2rem; font-weight:900; color:{w_color}; text-shadow: 0 0 10px rgba(52,211,153,0.15); line-height:1;">{w_count}</span>
<span style="font-size:0.78rem; color:#a1a1aa; font-weight:600;">Words</span>
</div>
<div style="margin-bottom:0.6rem; display:inline-block;">
<span style="background:rgba(52,211,153,0.1); color:{w_color}; font-size:0.68rem; font-weight:800; padding:0.15rem 0.5rem; border-radius:4px; border:1px solid rgba(52,211,153,0.15); text-transform:uppercase; letter-spacing:0.5px;">Status: {w_status}</span>
</div>
<p style="font-size:0.8rem; color:#a1a1aa; margin:0; line-height:1.5;">{word_count_desc}</p>
</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

    with audit_tab2:
        st.markdown(f"""<div class="card" style="box-shadow:0 4px 15px rgba(0,0,0,0.15); margin-top: 0.5rem; border: none; padding: 0; background: transparent;">
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1.2rem; align-items: stretch; margin-bottom: 1rem;">
<div class="profile-cell" style="margin:0; background: linear-gradient(180deg, rgba(59, 130, 246, 0.04) 0%, rgba(15, 23, 42, 0.3) 100%); border: 1px solid rgba(59, 130, 246, 0.15); border-left: 4px solid #3b82f6; border-radius: 12px; padding: 1.2rem; height: 100%; box-sizing: border-box; display: flex; flex-direction: column; justify-content: flex-start;">
<div class="pc-label" style="color:#3b82f6; font-weight:800; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.5px;">💼 Experience Summary</div>
<div class="pc-text" style="display:block; margin-top:0.6rem; flex-grow: 1;">{exp_html}</div>
</div>
<div class="profile-cell" style="margin:0; background: linear-gradient(180deg, rgba(16, 185, 129, 0.04) 0%, rgba(15, 23, 42, 0.3) 100%); border: 1px solid rgba(16, 185, 129, 0.15); border-left: 4px solid #10b981; border-radius: 12px; padding: 1.2rem; height: 100%; box-sizing: border-box; display: flex; flex-direction: column; justify-content: flex-start;">
<div class="pc-label" style="color:#10b981; font-weight:800; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.5px;">🎓 Education Summary</div>
<div class="pc-text" style="display:block; margin-top:0.6rem; flex-grow: 1;">{edu_html}</div>
</div>
<div class="profile-cell" style="margin:0; background: linear-gradient(180deg, rgba(251, 191, 36, 0.04) 0%, rgba(15, 23, 42, 0.3) 100%); border: 1px solid rgba(251, 191, 36, 0.15); border-left: 4px solid #fbbf24; border-radius: 12px; padding: 1.2rem; height: 100%; box-sizing: border-box; display: flex; flex-direction: column; justify-content: flex-start;">
<div class="pc-label" style="color:#fbbf24; font-weight:800; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.5px;">🚀 Projects Portfolio Details</div>
<div class="pc-text" style="display:block; margin-top:0.6rem; flex-grow: 1;">{proj_html}</div>
</div>
<div class="profile-cell" style="margin:0; background: linear-gradient(180deg, rgba(167, 139, 250, 0.04) 0%, rgba(15, 23, 42, 0.3) 100%); border: 1px solid rgba(167, 139, 250, 0.15); border-left: 4px solid #a78bfa; border-radius: 12px; padding: 1.2rem; height: 100%; box-sizing: border-box; display: flex; flex-direction: column; justify-content: flex-start;">
<div class="pc-label" style="color:#a78bfa; font-weight:800; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.5px;">🏆 Certifications & Credentials</div>
<div class="pc-text" style="display:block; margin-top:0.6rem; flex-grow: 1;">{cert_html}</div>
</div>
</div>
</div>""", unsafe_allow_html=True)



    # ─── FINAL RECRUITER VERDICT & JOB SUGGESTIONS ─────────────
    verdict_data = data.get("final_recruiter_verdict", {})
    vd = verdict_data.get("verdict", "Weak Match")
    v_emoji = verdict_data.get("verdict_emoji", "🔴")
    conclusion = verdict_data.get("conclusion", "")

    vd_lower = vd.lower()
    if "strong" in vd_lower or "exceptional" in vd_lower:
        verdict_badge_html = f'<span style="background:rgba(16, 185, 129, 0.15); color:#34d399; border:1px solid rgba(16, 185, 129, 0.3); font-size:1rem; font-weight:800; padding:0.4rem 1.2rem; border-radius:30px; letter-spacing:0.5px; box-shadow: 0 0 20px rgba(16, 185, 129, 0.12); display: inline-flex; align-items: center; gap: 0.4rem;">{v_emoji} {esc(vd)}</span>'
    elif "weak" in vd_lower or "below" in vd_lower or "critical" in vd_lower:
        verdict_badge_html = f'<span style="background:rgba(239, 68, 68, 0.15); color:#f87171; border:1px solid rgba(239, 68, 68, 0.3); font-size:1rem; font-weight:800; padding:0.4rem 1.2rem; border-radius:30px; letter-spacing:0.5px; box-shadow: 0 0 20px rgba(239, 68, 68, 0.12); display: inline-flex; align-items: center; gap: 0.4rem;">{v_emoji} {esc(vd)}</span>'
    else:
        verdict_badge_html = f'<span style="background:rgba(59, 130, 246, 0.15); color:#60a5fa; border:1px solid rgba(59, 130, 246, 0.3); font-size:1rem; font-weight:800; padding:0.4rem 1.2rem; border-radius:30px; letter-spacing:0.5px; box-shadow: 0 0 20px rgba(59, 130, 246, 0.12); display: inline-flex; align-items: center; gap: 0.4rem;">{v_emoji} {esc(vd)}</span>'

    roles = data.get("job_role_recommendations", [])
    rec_roles_html = ""
    if roles:
        rec_roles_html = "".join([
            f'<div style="background:rgba(129,140,248,0.06); border:1px solid rgba(129,140,248,0.15); border-radius:30px; padding:0.35rem 0.9rem; display:inline-flex; align-items:center; gap:0.4rem; margin-right:0.4rem; margin-bottom:0.4rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">'
            f'<span style="font-weight:700; color:#818cf8; font-size:0.78rem;">{esc(r.get("title", ""))}</span>'
            f'<span style="background:rgba(129,140,248,0.15); color:#a78bfa; font-size:0.65rem; font-weight:800; padding:0.08rem 0.4rem; border-radius:10px;">{r.get("match_percentage", 0)}% Match</span>'
            f'</div>' for r in roles
        ])
    else:
        rec_roles_html = '<div style="color:#71717a; font-size:0.8rem; font-style:italic;">No job role recommendations available.</div>'

    st.markdown(f"""<div class="verdict-box" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.06) 0%, rgba(167, 139, 250, 0.03) 50%, rgba(15, 23, 42, 0.4) 100%); border: 1px solid rgba(99, 102, 241, 0.18); border-left: 5px solid #818cf8; border-radius: 16px; padding: 2.2rem; text-align: center; margin-top: 1rem; box-shadow: 0 8px 32px rgba(99, 102, 241, 0.08);">
<div class="v-over" style="color: #a1a1aa; font-size: 0.72rem; text-transform: uppercase; font-weight: 800; letter-spacing: 2px; margin-bottom: 0.6rem;">🏆 Final Recruiter Verdict</div>
<div style="margin: 0.8rem 0;">{verdict_badge_html}</div>
<div class="v-desc" style="color: #f4f4f5; font-size: 0.95rem; font-style: italic; max-width: 720px; line-height: 1.8; margin: 1.4rem auto 1.8rem auto; padding: 0 1rem;">
“{esc(conclusion)}”
</div>
<div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 1.5rem; text-align: left; max-width: 720px; margin: 0 auto;">
<div style="font-size: 0.68rem; color: #71717a; text-transform: uppercase; font-weight: 800; margin-bottom: 0.8rem; letter-spacing: 1px;">Recommended Roles Based on Competencies</div>
<div class="tag-wrap" style="display:flex; flex-wrap:wrap; gap:0.3rem;">{rec_roles_html}</div>
</div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="line"></div>', unsafe_allow_html=True)
    
    # Download report
    dc1, dc2 = st.columns(2)
    with dc1:
        st.download_button("Download Report (JSON)", json.dumps(data, indent=2, ensure_ascii=False),
                           f"ats_report_{cname.replace(' ','_').lower()}.json", "application/json",
                           use_container_width=True)
    with dc2:
        html_report = generate_html_report(data)
        st.download_button("Download PDF Report (HTML)", html_report,
                           f"ats_report_{cname.replace(' ','_').lower()}.html", "text/html",
                           use_container_width=True)

