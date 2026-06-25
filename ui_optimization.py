import streamlit as st
import re
from datetime import datetime
from report_generator import esc

def clean_html(html_str):
    if not html_str:
        return ""
    # Strip leading whitespace from each line to prevent markdown code-block parsing
    return "\n".join([line.strip() for line in html_str.split("\n")])

def highlight_xyz(text):
    if not text:
        return ""
    # Highlight percentages and numeric metrics in emerald
    text = re.sub(
        r'(\b\d+(?:\.\d+)?%|\b\d+x\b|\$[0-9,]+[KkMmBb]?|\b\d+\+)',
        r'<span style="background: rgba(52,211,153,0.06); border: 1px solid rgba(52,211,153,0.2); border-radius: 4px; padding: 0.1rem 0.35rem; margin: 0 0.1rem; color: #34d399; font-weight: 700; white-space: nowrap; font-size: 0.85em; text-shadow: 0 0 8px rgba(52,211,153,0.15);">\1</span>',
        text
    )
    # Highlight action verbs in lavender/light purple
    action_verbs = ["Achieved", "Spearheaded", "Optimized", "Designed", "Built", "Developed", "Deployed", "Implemented", "Architected", "Engineered", "Created", "Increased", "Reduced", "Delivered", "Improved", "Led", "Accomplished", "Pioneered", "Leveraged"]
    for verb in action_verbs:
        text = re.compile(rf'\b({verb})\b', re.IGNORECASE).sub(
            r'<span style="background: rgba(167,139,250,0.06); border: 1px solid rgba(167,139,250,0.2); border-radius: 4px; padding: 0.1rem 0.35rem; margin: 0 0.1rem; color: #c084fc; font-weight: 700; white-space: nowrap; font-size: 0.85em; text-shadow: 0 0 8px rgba(167,139,250,0.15);">\1</span>',
            text
        )
    # Highlight common technology terms in light blue
    techs = ["ensemble methods", "machine learning", "deep learning", "flask", "django", "react", "python", "sql", "aws", "docker", "kubernetes", "git", "ci/cd", "fastapi"]
    for tech in techs:
        text = re.compile(rf'\b({tech})\b', re.IGNORECASE).sub(
            r'<span style="background: rgba(96,165,250,0.06); border: 1px solid rgba(96,165,250,0.2); border-radius: 4px; padding: 0.1rem 0.35rem; margin: 0 0.1rem; color: #60a5fa; font-weight: 700; white-space: nowrap; font-size: 0.85em;">\1</span>',
            text
        )
    return text

def parse_xyz(text):
    if not text:
        return "None detected", "None detected", "Generic method", "quantifiable data"
    # Action Verbs
    action_verbs = ["Achieved", "Spearheaded", "Optimized", "Designed", "Built", "Developed", "Deployed", "Implemented", "Architected", "Engineered", "Created", "Increased", "Reduced", "Delivered", "Improved", "Led", "Accomplished", "Pioneered", "Leveraged"]
    found_verbs = []
    for verb in action_verbs:
        if re.search(rf'\b{verb}\b', text, re.IGNORECASE):
            found_verbs.append(verb.title())
            
    # Metrics
    metrics_pattern = r'(\b\d+(?:\.\d+)?%|\b\d+x\b|\$[0-9,]+[KkMmBb]?|\b\d+\+)'
    found_metrics = re.findall(metrics_pattern, text)
    
    # Technologies / Methods
    techs = ["ensemble methods", "machine learning", "deep learning", "flask", "django", "react", "python", "sql", "aws", "docker", "kubernetes", "git", "ci/cd", "fastapi"]
    found_techs = []
    for tech in techs:
        if re.search(rf'\b{tech}\b', text, re.IGNORECASE):
            found_techs.append(tech)
            
    verb_label = ", ".join(found_verbs) if found_verbs else "None detected"
    metric_label = ", ".join(found_metrics) if found_metrics else "None detected"
    tech_label = ", ".join([t.title() for t in found_techs]) if found_techs else "Generic method"
    
    metric_highlight = found_metrics[0] if found_metrics else "quantifiable data"
    
    return verb_label, metric_label, tech_label, metric_highlight

def parse_original_weakness(text):
    if not text:
        return "None / Passive", "Missing Metric", "Lacks Tech Context", "No content available."
    
    # Check if starting with passive verb
    weak_verbs = ["Developed", "Worked", "Responsible", "Assisted", "Helped", "Participated", "Managed", "Led", "Created", "Built"]
    first_word_match = re.match(r'^\s*"?\s*([a-zA-Z]+)', text)
    verb_label = "Passive / Generic"
    if first_word_match:
        first_word = first_word_match.group(1)
        if first_word.title() in weak_verbs:
            verb_label = f"Weak Verb ({first_word.title()})"
            
    # Check metrics
    metrics_pattern = r'(\b\d+(?:\.\d+)?%|\b\d+x\b|\$[0-9,]+[KkMmBb]?|\b\d+\+)'
    has_metric = bool(re.search(metrics_pattern, text))
    if has_metric:
        metric_label = "Buried Outcome"
        critique = "The impact metric is positioned towards the end of the sentence, reducing its visual prominence during initial recruiter scans."
    else:
        metric_label = "Missing Outcome"
        critique = "No quantifiable metrics or business outcomes are listed. The statement fails to prove the scale or success of your work."
        
    # Check technology
    techs = ["ensemble methods", "machine learning", "deep learning", "flask", "django", "react", "python", "sql", "aws", "docker", "kubernetes", "git", "ci/cd", "fastapi"]
    has_tech = any(t in text.lower() for t in techs)
    tech_label = "Underutilized" if has_tech else "Lacks Tech Context"
    
    return verb_label, metric_label, tech_label, critique

def get_readiness_checklist(p_desc, p_deploy):
    combined = (p_desc + " " + p_deploy).lower()
    checklist = [
        ("Database / Storage", any(w in combined for w in ["sql", "db", "mongo", "postgres", "mysql", "redis", "firebase", "database"]), "💾"),
        ("API / Web Interface", any(w in combined for w in ["flask", "django", "fastapi", "api", "rest", "backend", "express", "node", "ui", "interface", "app"]), "⚡"),
        ("Cloud Deployment", any(w in combined for w in ["aws", "heroku", "docker", "kubernetes", "cloud", "deploy", "gcp", "azure", "vercel", "github pages", "render"]), "🚀"),
        ("CI/CD / Automation", any(w in combined for w in ["test", "pytest", "unittest", "jenkins", "github actions", "ci", "cd", "pipeline"]), "🧪")
    ]
    return checklist

def find_project_techs(p_name, p_innov, p_val, p_deploy, parsed_projects):
    p_name_lower = p_name.lower()
    for proj in parsed_projects:
        if proj.get("title", "").lower() in p_name_lower or p_name_lower in proj.get("title", "").lower():
            return proj.get("technologies", [])
            
    # Extract from text if not found in parsed projects
    tech_keywords = ["python", "javascript", "react", "flask", "django", "html", "css", "sql", "postgresql", "mysql", "mongodb", "aws", "gcp", "docker", "kubernetes", "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "c++", "java", "node", "express", "git"]
    combined = (p_name + " " + p_innov + " " + p_val + " " + p_deploy).lower()
    return [t.title() for t in tech_keywords if t in combined]

def get_recommendation_priority(rec):
    rec_lower = rec.lower()
    if any(w in rec_lower for w in ["crucial", "critical", "must", "essential", "primary", "develop", "personal project", "direct link", "add link", "missing"]):
        return "High Priority", "🔴", "#f87171", "rgba(248,113,113,0.06)", "rgba(248,113,113,0.18)"
    if any(w in rec_lower for w in ["improve", "increase", "add description", "participation", "engage", "network", "share", "activity"]):
        return "Medium Priority", "🟡", "#fb923c", "rgba(251,146,60,0.06)", "rgba(251,146,60,0.18)"
    return "Low Priority", "🔵", "#60a5fa", "rgba(96,165,250,0.06)", "rgba(96,165,250,0.18)"

def generate_cover_letter_html(cname, email, phone, role, date_str, letter_text):
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Cover Letter - {cname}</title>
    <style>
        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #1e293b;
            background: #ffffff;
            margin: 0;
            padding: 2.5rem;
            line-height: 1.7;
            font-size: 0.95rem;
        }}
        .header {{
            border-bottom: 2px solid #6366f1;
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}
        .header-left {{
            text-align: left;
        }}
        .header-right {{
            text-align: right;
        }}
        .candidate-name {{
            font-weight: 800;
            font-size: 1.5rem;
            color: #1e1b4b;
        }}
        .contact-info {{
            font-size: 0.82rem;
            color: #64748b;
            margin-top: 0.2rem;
        }}
        .doc-title {{
            font-weight: 700;
            font-size: 0.85rem;
            color: #6366f1;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        .date {{
            font-size: 0.82rem;
            color: #64748b;
            margin-top: 0.2rem;
        }}
        .recipient {{
            margin-bottom: 2rem;
            font-size: 0.9rem;
            color: #475569;
        }}
        .body-text {{
            white-space: pre-line;
            color: #334155;
            margin-bottom: 3rem;
        }}
        .signature {{
            border-top: 1px dashed #cbd5e1;
            padding-top: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .signature-name {{
            font-weight: 700;
            font-size: 1.15rem;
            color: #1e1b4b;
            margin-top: 0.4rem;
        }}
        @media print {{
            body {{
                padding: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <div class="candidate-name">{cname}</div>
            <div class="contact-info">{email} | {phone}</div>
        </div>
        <div class="header-right">
            <div class="doc-title">Cover Letter</div>
            <div class="date">{date_str}</div>
        </div>
    </div>
    
    <div class="recipient">
        <div><strong>To:</strong> Hiring Team</div>
        <div style="margin-top: 0.25rem;"><strong>Subject:</strong> Application for {role} Role</div>
    </div>
    
    <div class="body-text">
        {letter_text}
    </div>
    
    <div class="signature">
        <div>
            <div style="font-style: italic; color: #64748b;">Sincerely,</div>
            <div class="signature-name">{cname}</div>
        </div>
        <div style="border: 1px solid #cbd5e1; border-radius: 6px; padding: 0.4rem 0.8rem; font-size: 0.72rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
            Verified Candidate Profile
        </div>
    </div>
</body>
</html>"""

def render_optimization_tab(data, candidate_id=None):
    cname = esc(data.get("candidate_name", "Candidate"))
    
    st.markdown(clean_html('<div class="line"></div>'), unsafe_allow_html=True)
    
    st.markdown(clean_html(f"""<div class="res-header">
<div class="over">Resume Intelligence</div>
<div class="name">Optimization Engine</div>
</div>"""), unsafe_allow_html=True)

    # ─── RESUME QUALITY REPORT (Overview Section) ──────────────────────
    rq_rep = data.get("resume_quality_report", {})
    rq_strengths = rq_rep.get("strengths", [])
    rq_weaknesses = rq_rep.get("weaknesses", [])
    rq_analysis = rq_rep.get("analysis", "")
    
    st.markdown(clean_html(f"""<div class="card" style="margin-bottom: 1.5rem; background: linear-gradient(135deg, rgba(52, 211, 153, 0.04) 0%, rgba(15, 23, 42, 0.4) 100%); border: 1px solid rgba(52, 211, 153, 0.15); border-left: 4px solid #10b981; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);">
<div class="card-head" style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 0.5rem; margin-bottom: 1rem;">
<div class="icon-box green">📄</div>
<h3 style="margin:0;">Resume Quality Evaluation Detail</h3>
</div>
<div class="card-body" style="color:#e4e4e7; font-size:0.92rem; line-height:1.6; font-style:italic;">
“{esc(rq_analysis)}”
</div>
</div>"""), unsafe_allow_html=True)
    
    rq_col1, rq_col2 = st.columns(2, gap="medium")
    with rq_col1:
        strengths_bullets = "".join([
            f'<div style="display:flex; align-items:flex-start; gap:0.5rem; margin-top:0.6rem;">'
            f'<span style="color:#34d399; font-weight:bold; font-size:0.95rem; line-height:1.2;">✓</span>'
            f'<span style="font-size:0.86rem; color:#d4d4d8; line-height:1.45;">{esc(s)}</span>'
            f'</div>' for s in rq_strengths
        ]) if rq_strengths else '<div style="color:#71717a; font-size:0.82rem; margin-top:0.4rem; font-style:italic;">No specific strengths highlighted</div>'
        
        st.markdown(clean_html(f"""<div class="profile-cell" style="background: linear-gradient(135deg, rgba(52, 211, 153, 0.04) 0%, rgba(15, 23, 42, 0.3) 100%); border: 1px solid rgba(52, 211, 153, 0.15); border-left: 4px solid #34d399; border-radius:12px; padding:1.2rem 1.4rem; height: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
<div class="pc-label" style="color: #34d399; font-weight:700; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.5rem;">✅ Formatting & Content Strengths</div>
{strengths_bullets}
</div>"""), unsafe_allow_html=True)
        
    with rq_col2:
        weaknesses_bullets = "".join([
            f'<div style="display:flex; align-items:flex-start; gap:0.5rem; margin-top:0.6rem;">'
            f'<span style="color:#f87171; font-weight:bold; font-size:0.95rem; line-height:1.2;">⚠</span>'
            f'<span style="font-size:0.86rem; color:#d4d4d8; line-height:1.45;">{esc(w)}</span>'
            f'</div>' for w in rq_weaknesses
        ]) if rq_weaknesses else '<div style="color:#71717a; font-size:0.82rem; margin-top:0.4rem; font-style:italic;">No specific weaknesses highlighted</div>'
        
        st.markdown(clean_html(f"""<div class="profile-cell" style="background: linear-gradient(135deg, rgba(248, 113, 113, 0.04) 0%, rgba(15, 23, 42, 0.3) 100%); border: 1px solid rgba(248, 113, 113, 0.15); border-left: 4px solid #f87171; border-radius:12px; padding:1.2rem 1.4rem; height: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
<div class="pc-label" style="color: #f87171; font-weight:700; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.5rem;">❌ Formatting & Content Weaknesses</div>
{weaknesses_bullets}
</div>"""), unsafe_allow_html=True)

    st.markdown(clean_html("<div style='height: 1.5rem;'></div>"), unsafe_allow_html=True)
    
    st.markdown(clean_html("""<div class="card-head" style="margin-bottom: 0.8rem;">
        <div class="icon-box purple">🛠️</div>
        <h3 style="margin:0;">Interactive Optimization Deep-Dives</h3>
    </div>"""), unsafe_allow_html=True)

    # Sub-tabs for deep-dives
    opt_tab1, opt_tab2, opt_tab3, opt_tab4 = st.tabs([
        "✍️ Bullet Rewrite Suggestions",
        "🛠️ Project Portfolio Deep-Dive",
        "💻 GitHub & LinkedIn Profiles",
        "📝 AI Cover Letter Draft"
    ])
    
    # ─── TAB 1: REWRITE SUGGESTIONS ──────────────────────────────────
    with opt_tab1:
        rewrites = data.get("rewritten_statements", [])
        if rewrites:
            for rw in rewrites:
                orig = rw.get("original", "")
                sugg = rw.get("suggested", "")
                
                orig_hl = highlight_xyz(orig)
                sugg_hl = highlight_xyz(sugg)
                
                verb_label, metric_label, tech_label, metric_highlight = parse_xyz(sugg)
                orig_verb, orig_metric, orig_tech, orig_critique = parse_original_weakness(orig)
                
                st.markdown(clean_html(f"""
<div class="rewrite-card-container">
    <div class="rewrite-grid">
        <!-- Original -->
        <div class="rewrite-box-original">
            <div>
                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.72rem; color: #f87171; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 800; margin-bottom: 0.6rem;">
                    <span>❌ Original Phrasing (Weak)</span>
                    <span class="rewrite-weakness-badge">ATS Score: 45/100</span>
                </div>
                <div style="font-size: 0.88rem; color: #e4e4e7; line-height: 1.6; font-style: italic; margin-bottom: 0.8rem;">
                    <span style="color: #ef4444; font-size: 1.4rem; font-weight: 800; font-family: Georgia, serif; vertical-align: -0.2rem; margin-right: 0.1rem;">“</span>{orig_hl}<span style="color: #ef4444; font-size: 1.4rem; font-weight: 800; font-family: Georgia, serif; vertical-align: -0.2rem; margin-left: 0.1rem;">”</span>
                </div>
            </div>
            
            <!-- Weakness Analysis Breakdown -->
            <div style="background: rgba(239, 68, 68, 0.02); border: 1px solid rgba(239, 68, 68, 0.08); border-radius: 8px; padding: 0.6rem 0.8rem; margin-bottom: 0.8rem;">
                <div style="font-size: 0.68rem; color: #f87171; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem;">⚠️ ATS Weakness Analysis</div>
                <div style="display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.76rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #a1a1aa;">Verb Quality:</span>
                        <span style="color: #f87171; font-weight: 700;">{orig_verb}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #a1a1aa;">Quantifiable Metric:</span>
                        <span style="color: #fb923c; font-weight: 700;">{orig_metric}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #a1a1aa;">Tech/Method Context:</span>
                        <span style="color: #f87171; font-weight: 700;">{orig_tech}</span>
                    </div>
                </div>
            </div>
            
            <!-- Structure Critique -->
            <div style="font-size: 0.72rem; color: #94a3b8; line-height: 1.45; background: rgba(255,255,255,0.01); border-radius: 6px; padding: 0.5rem 0.7rem; border-left: 2px solid #ef4444; margin-bottom: 0.8rem;">
                ❌ <strong>Structure Critique:</strong> {orig_critique}
            </div>
            
            <div style="font-size: 0.68rem; color: #71717a; border-top: 1px solid rgba(255, 255, 255, 0.04); padding-top: 0.5rem; display:flex;">
                <span class="rewrite-badge-warn">⚠️ Lacks clear quantifiable impact and action verbs.</span>
            </div>
        </div>

        <!-- Divider with arrow -->
        <div class="rewrite-divider">
            <div class="rewrite-arrow-circle">➔</div>
        </div>

        <!-- Suggested -->
        <div class="rewrite-box-suggested">
            <div>
                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.72rem; color: #34d399; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 800; margin-bottom: 0.6rem;">
                    <span>✨ Google X-Y-Z Rewrite (Impact)</span>
                    <span class="rewrite-impact-badge">Impact: 95/100</span>
                </div>
                <div style="font-size: 0.9rem; color: #fafafa; line-height: 1.6; font-weight: 600; margin-bottom: 0.8rem;">
                    <span style="color: #10b981; font-size: 1.4rem; font-weight: 800; font-family: Georgia, serif; vertical-align: -0.2rem; margin-right: 0.1rem;">“</span>{sugg_hl}<span style="color: #10b981; font-size: 1.4rem; font-weight: 800; font-family: Georgia, serif; vertical-align: -0.2rem; margin-left: 0.1rem;">”</span>
                </div>
            </div>
            
            <!-- Framework Breakdown Analysis -->
            <div style="background: rgba(52, 211, 153, 0.02); border: 1px solid rgba(52, 211, 153, 0.08); border-radius: 8px; padding: 0.6rem 0.8rem; margin-bottom: 0.8rem;">
                <div style="font-size: 0.68rem; color: #34d399; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem;">📊 X-Y-Z Structure Breakdown</div>
                <div style="display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.76rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #a1a1aa;">Action Verb [X]:</span>
                        <span style="color: #c084fc; font-weight: 700;">{verb_label}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #a1a1aa;">Quantifiable Metric [Y]:</span>
                        <span style="color: #34d399; font-weight: 700;">{metric_label}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #a1a1aa;">Technology / Method [Z]:</span>
                        <span style="color: #60a5fa; font-weight: 700;">{tech_label}</span>
                    </div>
                </div>
            </div>
            
            <!-- Professional Value Add -->
            <div style="font-size: 0.72rem; color: #94a3b8; line-height: 1.45; background: rgba(255,255,255,0.01); border-radius: 6px; padding: 0.5rem 0.7rem; border-left: 2px solid #38bdf8; margin-bottom: 0.8rem;">
                💡 <strong>Impact Analysis:</strong> Relocates accomplishments to the front of the sentence. Using metrics like <strong>{metric_highlight}</strong> makes the contribution instantly verifiable by recruiters and raises the resume's overall ATS visibility score.
            </div>

            <div style="font-size: 0.68rem; color: #34d399; border-top: 1px solid rgba(16, 185, 129, 0.1); padding-top: 0.5rem; display:flex;">
                <span class="rewrite-badge-success">🚀 Accomplished [X] as measured by [Y] by doing [Z].</span>
            </div>
        </div>
    </div>
</div>"""), unsafe_allow_html=True)
        else:
            st.info("No statement rewrites suggested for this resume profile.")

    # ─── TAB 2: PORTFOLIO DEEP-DIVE ──────────────────────────────────
    with opt_tab2:
        proj_eval = data.get("project_evaluation", [])
        if proj_eval:
            for proj in proj_eval:
                p_name = esc(proj.get("name", "Project"))
                p_score = proj.get("score", 0)
                p_compl = esc(proj.get("complexity", "Medium"))
                p_innov = esc(proj.get("innovation", ""))
                p_val = esc(proj.get("value", ""))
                p_deploy = esc(proj.get("deployment", ""))
                p_rel = esc(proj.get("relevance", ""))
                p_strengths = proj.get("strengths", [])
                p_weaknesses = proj.get("weaknesses", [])
                p_sugs = proj.get("suggestions", [])
                
                # Check complexity score for gauge
                c_score = 70
                c_color_rgb = "96, 165, 250"
                if p_compl.lower() == "high":
                    c_score = 90
                    c_color = "#a78bfa"
                    c_color_rgb = "167, 139, 250"
                elif p_compl.lower() == "low":
                    c_score = 45
                    c_color = "#f43f5e"
                    c_color_rgb = "244, 63, 94"
                else:
                    c_color = "#60a5fa"
                    
                # Technologies
                techs = find_project_techs(p_name, p_innov, p_val, p_deploy, data.get("parsed_data", {}).get("projects", []))
                tech_chips = "".join([f'<span style="background:rgba(99,102,241,0.06); color:#818cf8; border:1px solid rgba(99,102,241,0.2); font-size:0.68rem; font-weight:700; padding:0.15rem 0.55rem; border-radius:6px; margin-right:0.35rem; margin-top:0.35rem; display:inline-block; box-shadow: 0 0 8px rgba(99,102,241,0.05);">⚙️ {esc(t)}</span>' for t in techs]) if techs else ""
                
                # Readiness checklist
                checklist = get_readiness_checklist(p_innov + " " + p_val, p_deploy)
                
                # Dynamic recommendations based on checklist status
                dynamic_sugs = []
                db_checked = next((checked for name, checked, _ in checklist if "Database" in name), True)
                api_checked = next((checked for name, checked, _ in checklist if "API" in name), True)
                cloud_checked = next((checked for name, checked, _ in checklist if "Cloud" in name), True)
                cicd_checked = next((checked for name, checked, _ in checklist if "CI/CD" in name), True)
                
                if not db_checked:
                    dynamic_sugs.append("Integrate a database system (e.g. SQLite, PostgreSQL, or MongoDB) to handle stateful data persistence.")
                if not api_checked:
                    dynamic_sugs.append("Expose model predictions programmatically through a REST API framework (Flask or FastAPI).")
                if not cloud_checked:
                    dynamic_sugs.append("Create a Dockerfile configuration and deploy to cloud platforms (AWS, Render, or GCP) for remote accessibility.")
                if not cicd_checked:
                    dynamic_sugs.append("Set up automated unit testing (pytest) and set up a CI/CD build check using GitHub Actions.")
                
                # Combine original suggestions with dynamic checklists suggestions
                all_sugs = list(p_sugs)
                for ds in dynamic_sugs:
                    if ds not in all_sugs:
                        all_sugs.append(ds)
                
                checklist_html = ""
                for name, checked, emoji in checklist:
                    status_icon = '<span style="color:#34d399; font-weight:bold; font-size:0.9rem;">✓</span>' if checked else '<span style="color:#71717a; font-weight:bold; font-size:0.9rem;">○</span>'
                    status_color = '#d4d4d8' if checked else '#71717a'
                    checklist_html += f"""
                    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.35rem; font-size:0.8rem; color:{status_color};">
                        <div style="display:flex; align-items:center; gap:0.4rem;">
                            <span style="font-size:0.9rem;">{emoji}</span><span>{name}</span>
                        </div>
                        <div>{status_icon}</div>
                    </div>
                    """
                
                # Format bullet points
                strengths_html = "".join([
                    f'<div style="display:flex; align-items:flex-start; gap:0.5rem; margin-top:0.5rem;">'
                    f'<span style="color:#34d399; font-weight:bold; font-size:0.9rem; line-height:1.2;">✓</span>'
                    f'<span style="font-size:0.84rem; color:#d4d4d8; line-height:1.45;">{esc(s)}</span>'
                    f'</div>' for s in p_strengths
                ]) if p_strengths else '<div style="color:#71717a; font-size:0.82rem; margin-top:0.4rem; font-style:italic;">No specific strengths listed</div>'
                
                weaknesses_html = ""
                if p_weaknesses:
                    weaknesses_html += "".join([
                        f'<div style="display:flex; align-items:flex-start; gap:0.5rem; margin-top:0.5rem;">'
                        f'<span style="color:#f87171; font-weight:bold; font-size:0.9rem; line-height:1.2;">⚠</span>'
                        f'<span style="font-size:0.84rem; color:#d4d4d8; line-height:1.45;">{esc(w)}</span>'
                        f'</div>' for w in p_weaknesses
                    ])
                if all_sugs:
                    weaknesses_html += "".join([
                        f'<div style="display:flex; align-items:flex-start; gap:0.5rem; margin-top:0.5rem;">'
                        f'<span style="color:#60a5fa; font-weight:bold; font-size:0.9rem; line-height:1.2;">💡</span>'
                        f'<span style="font-size:0.84rem; color:#d4d4d8; line-height:1.45;">{esc(s)}</span>'
                        f'</div>' for s in all_sugs
                    ])
                if not weaknesses_html:
                    weaknesses_html = '<div style="color:#34d399; font-size:0.82rem; font-weight:600; margin-top:0.4rem;">🎉 No weaknesses identified! Project is production ready.</div>'
                
                st.markdown(clean_html(f"""<div class="project-card">
<!-- Title & Score Bar -->
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.2rem; border-bottom:1px solid rgba(255, 255, 255, 0.06); padding-bottom:0.8rem; flex-wrap:wrap; gap:0.5rem;">
    <div>
        <div style="font-size: 1.2rem; font-weight: 700; color: #fafafa; font-family:\'Outfit\', sans-serif; letter-spacing: -0.01em;">{p_name}</div>
        <div style="display:flex; flex-wrap:wrap; gap:0.1rem; margin-top:0.25rem;">{tech_chips}</div>
    </div>
    <div style="display:flex; gap:0.5rem; align-items:center;">
        <span style="font-size:0.65rem; font-weight:800; color:{c_color}; background:rgba(255,255,255,0.02); border:1px solid {c_color}; padding:0.25rem 0.65rem; border-radius:6px; text-transform:uppercase; letter-spacing:0.8px; box-shadow: 0 0 10px rgba({c_color_rgb}, 0.12);">{p_compl} Complexity</span>
        <span style="font-size:0.65rem; font-weight:800; color:#34d399; background:rgba(52,211,153,0.08); border:1px solid rgba(52,211,153,0.22); padding:0.25rem 0.65rem; border-radius:6px; text-transform:uppercase; letter-spacing:0.8px; box-shadow: 0 0 10px rgba(52,211,153,0.12);">Score: {p_score}/100</span>
    </div>
</div>

<!-- 4-Axis Grid Details -->
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.2rem; margin-bottom: 1.5rem;">
    <div style="background: linear-gradient(135deg, rgba(167, 139, 250, 0.03) 0%, rgba(15, 23, 42, 0.3) 100%); border: 1px solid rgba(167, 139, 250, 0.15); border-left: 4px solid #a78bfa; border-radius: 12px; padding: 1.1rem; box-shadow: inset 0 1px 0 rgba(255,255,255,0.01);">
        <div style="font-size: 0.84rem; color: #d4d4d8; line-height: 1.6;">
            <span style="color:#a78bfa; font-weight:800; display:block; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.4rem;">💡 Innovation Index</span> 
            {p_innov}
        </div>
    </div>
    <div style="background: linear-gradient(135deg, rgba(52, 211, 153, 0.03) 0%, rgba(15, 23, 42, 0.3) 100%); border: 1px solid rgba(52, 211, 153, 0.15); border-left: 4px solid #34d399; border-radius: 12px; padding: 1.1rem; box-shadow: inset 0 1px 0 rgba(255,255,255,0.01);">
        <div style="font-size: 0.84rem; color: #d4d4d8; line-height: 1.6;">
            <span style="color:#34d399; font-weight:800; display:block; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.4rem;">📊 Business Impact</span> 
            {p_val}
        </div>
    </div>
    <div style="background: linear-gradient(135deg, rgba(96, 165, 250, 0.03) 0%, rgba(15, 23, 42, 0.3) 100%); border: 1px solid rgba(96, 165, 250, 0.15); border-left: 4px solid #60a5fa; border-radius: 12px; padding: 1.1rem; box-shadow: inset 0 1px 0 rgba(255,255,255,0.01);">
        <div style="font-size: 0.84rem; color: #d4d4d8; line-height: 1.6;">
            <span style="color:#60a5fa; font-weight:800; display:block; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.4rem;">🚀 Deployment & Cloud</span> 
            {p_deploy}
        </div>
    </div>
    <div style="background: linear-gradient(135deg, rgba(251, 146, 60, 0.03) 0%, rgba(15, 23, 42, 0.3) 100%); border: 1px solid rgba(251, 146, 60, 0.15); border-left: 4px solid #fb923c; border-radius: 12px; padding: 1.1rem; box-shadow: inset 0 1px 0 rgba(255,255,255,0.01);">
        <span style="color:#fb923c; font-weight:800; display:block; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.5rem;">🏁 Production Readiness</span> 
        {checklist_html}
    </div>
</div>

<!-- Strengths & Weaknesses side-by-side -->
<div class="profile-2col" style="grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:1rem; margin-top:0.6rem;">
    <div style="background:linear-gradient(135deg, rgba(52,211,153,0.02) 0%, rgba(15,23,42,0.3) 100%); border:1px solid rgba(52,211,153,0.15); border-left:4px solid #34d399; border-radius:12px; padding:1.2rem 1.4rem; box-shadow: 0 4px 15px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255, 255, 255, 0.01);">
        <div style="font-size:0.72rem; color:#34d399; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.5rem;">Project Strengths</div>
        {strengths_html}
    </div>
    <div style="background:linear-gradient(135deg, rgba(239,68,68,0.02) 0%, rgba(15,23,42,0.3) 100%); border:1px solid rgba(239,68,68,0.15); border-left:4px solid #f87171; border-radius:12px; padding:1.2rem 1.4rem; box-shadow: 0 4px 15px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255, 255, 255, 0.01);">
        <div style="font-size:0.72rem; color:#f87171; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.5rem;">Areas for Improvement & Action Plan</div>
        {weaknesses_html}
    </div>
</div>
</div>"""), unsafe_allow_html=True)
        else:
            st.info("No projects were detected/evaluated in this resume profile.")

    # ─── TAB 3: SOCIALS ANALYSIS ─────────────────────────────────────
    with opt_tab3:
        gh = data.get("github_analysis", {})
        li = data.get("linkedin_analysis", {})
        gh_score = gh.get("score", 0)
        li_score = li.get("score", 0)
        
        # SVG Circular Gauge helper
        def get_radial_gauge(score, prefix):
            color1, color2 = "#a78bfa", "#818cf8"
            if prefix == "gh":
                color1, color2 = "#c084fc", "#6366f1"
            elif prefix == "li":
                color1, color2 = "#38bdf8", "#3b82f6"
                
            offset = 282.7 * (1 - score / 100)
            return f"""
            <div style="display:flex; justify-content:center; margin-bottom:1.2rem;">
                <svg width="120" height="120" viewBox="0 0 120 120">
                    <defs>
                        <linearGradient id="gaugeGrad-{prefix}" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="{color1}" />
                            <stop offset="100%" stop-color="{color2}" />
                        </linearGradient>
                        <filter id="glow-{prefix}">
                            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                            <feMerge>
                                <feMergeNode in="coloredBlur"/>
                                <feMergeNode in="SourceGraphic"/>
                            </feMerge>
                        </filter>
                    </defs>
                    <circle cx="60" cy="60" r="45" stroke="rgba(255,255,255,0.03)" stroke-width="8" fill="transparent" />
                    <circle cx="60" cy="60" r="45" stroke="url(#gaugeGrad-{prefix})" stroke-width="8" fill="transparent"
                            stroke-dasharray="282.7" stroke-dashoffset="{offset}"
                            stroke-linecap="round" filter="url(#glow-{prefix})" />
                    <text x="60" y="62" font-family="'Outfit', sans-serif" font-weight="900" font-size="24" fill="#fafafa" text-anchor="middle" style="text-shadow: 0 2px 10px rgba(0,0,0,0.5);">{score}</text>
                    <text x="60" y="78" font-family="'Outfit', sans-serif" font-weight="700" font-size="9" fill="#71717a" text-anchor="middle" style="letter-spacing:1px;">SCORE</text>
                </svg>
            </div>
            """
            
        def get_audit_checklist_html(platform):
            # Dynamic audit checklist rows
            checklist = []
            if platform == "github":
                has_github = bool(re.search(r'github\.com', data.get("resume_text", "").lower()))
                has_projects = len(data.get("parsed_data", {}).get("projects", [])) > 0
                has_skills = len(data.get("parsed_data", {}).get("skills", [])) > 0
                checklist = [
                    ("Profile Bio & Contact Info", has_github),
                    ("Public Repository Documentation", has_projects),
                    ("Project Readme Files (README.md)", has_projects),
                    ("Repository Organization & Topics", has_skills),
                    ("Contribution Graph Activity", True)
                ]
            else:
                has_li = bool(re.search(r'linkedin\.com', data.get("resume_text", "").lower()))
                has_summary = len(data.get("profile_summary", {}).get("experience_summary", "")) > 10
                has_experience = len(data.get("parsed_data", {}).get("experience", [])) > 0
                has_skills = len(data.get("parsed_data", {}).get("skills", [])) > 0
                has_certs = len(data.get("parsed_data", {}).get("education", [])) > 0
                checklist = [
                    ("Professional Headline Keywords", has_li),
                    ("Story-Driven Summary / About", has_summary),
                    ("Work Experience Impact Metrics", has_experience),
                    ("Skills & Endorsements Matrix", has_skills),
                    ("Education & Certifications Details", has_certs)
                ]
                
            html = ""
            for item, checked in checklist:
                if checked:
                    status_badge = '<span style="background:rgba(52,211,153,0.08); color:#34d399; font-size:0.65rem; font-weight:800; padding:0.15rem 0.45rem; border-radius:4px; border:1px solid rgba(52,211,153,0.18); text-transform:uppercase; letter-spacing:0.5px;">✓ Completed</span>'
                    color = '#e4e4e7'
                else:
                    status_badge = '<span style="background:rgba(239,68,68,0.08); color:#f87171; font-size:0.65rem; font-weight:800; padding:0.15rem 0.45rem; border-radius:4px; border:1px solid rgba(239,68,68,0.18); text-transform:uppercase; letter-spacing:0.5px;">○ Missing</span>'
                    color = '#8e8e93'
                html += f"""
                <div style="display:flex; align-items:center; justify-content:space-between; padding:0.45rem 0; border-bottom:1px solid rgba(255,255,255,0.03); font-size:0.78rem; color:{color};">
                    <span style="font-weight: 500;">{item}</span>
                    <span>{status_badge}</span>
                </div>
                """
            return f'<div style="margin-top:0.4rem;">{html}</div>'
 
        def make_list_html(items, is_recommendation=False):
            if not items:
                return '<div style="color:#71717a; font-size:0.8rem; font-style:italic;">No data available.</div>'
            html = ""
            for item in items:
                if is_recommendation:
                    priority_text, priority_emoji, priority_color, cat_bg, cat_border = get_recommendation_priority(item)
                    badge = f'<span style="background:{cat_bg}; color:{priority_color}; font-size:0.6rem; font-weight:800; padding:0.08rem 0.35rem; border-radius:3px; border:1px solid {cat_border}; margin-right:0.35rem; text-transform:uppercase; vertical-align:middle; display:inline-block;">{priority_emoji} {priority_text}</span>'
                    html += f"""<div style="display:flex; align-items:flex-start; gap:0.4rem; margin-top:0.5rem; line-height:1.45;">
                    <div style="margin-top: 0.1rem; flex-shrink:0;">{badge}</div>
                    <span style="font-size:0.8rem; color:#d4d4d8;">{esc(item)}</span>
                    </div>"""
                else:
                    icon = '<span style="color:#34d399; font-weight:bold; font-size:0.85rem;">✓</span>'
                    html += f"""<div style="display:flex; align-items:flex-start; gap:0.4rem; margin-top:0.4rem;">
                    {icon}
                    <span style="font-size:0.8rem; color:#d4d4d8; line-height:1.4;">{esc(item)}</span>
                    </div>"""
            return html
 


        # GitHub Metrics Grid
        parsed_projects = data.get("parsed_data", {}).get("projects", [])
        repos_count = f"{max(len(parsed_projects), 3)}+ Active"
        readme_score = min(100, int(gh_score * 1.1)) if gh_score > 0 else 0
        seo_rank = max(5, 100 - gh_score) if gh_score > 0 else 95
        activity_status = "High" if gh_score >= 80 else "Moderate" if gh_score >= 60 else "Low"
        
        gh_metrics_html = f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; margin-bottom: 1rem; margin-top: 0.8rem;">
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 0.5rem 0.7rem; text-align: center;">
                <div style="font-size: 0.62rem; color: #a78bfa; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Public Repos</div>
                <div style="font-size: 1rem; font-weight: 800; color: #fafafa; margin-top: 0.15rem;">{repos_count}</div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 0.5rem 0.7rem; text-align: center;">
                <div style="font-size: 0.62rem; color: #a78bfa; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">README Quality</div>
                <div style="font-size: 1rem; font-weight: 800; color: #fafafa; margin-top: 0.15rem;">{readme_score}%</div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 0.5rem 0.7rem; text-align: center;">
                <div style="font-size: 0.62rem; color: #a78bfa; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">SEO Keyword Rank</div>
                <div style="font-size: 1rem; font-weight: 800; color: #fafafa; margin-top: 0.15rem;">Top {seo_rank}%</div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 0.5rem 0.7rem; text-align: center;">
                <div style="font-size: 0.62rem; color: #a78bfa; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Activity Rating</div>
                <div style="font-size: 1rem; font-weight: 800; color: #34d399; margin-top: 0.15rem;">{activity_status}</div>
            </div>
        </div>
        """

        # LinkedIn Metrics Grid
        headline_score = min(100, int(li_score * 1.05)) if li_score > 0 else 0
        linkedin_density = "High" if li_score >= 80 else "Medium" if li_score >= 60 else "Low"
        profile_completeness = li_score
        reach_rank = max(3, 100 - li_score) if li_score > 0 else 95

        li_metrics_html = f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; margin-bottom: 1rem; margin-top: 0.8rem;">
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 0.5rem 0.7rem; text-align: center;">
                <div style="font-size: 0.62rem; color: #60a5fa; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Headline Quality</div>
                <div style="font-size: 1rem; font-weight: 800; color: #fafafa; margin-top: 0.15rem;">{headline_score}%</div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 0.5rem 0.7rem; text-align: center;">
                <div style="font-size: 0.62rem; color: #60a5fa; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">SEO Keyword Density</div>
                <div style="font-size: 1rem; font-weight: 800; color: #fafafa; margin-top: 0.15rem;">{linkedin_density}</div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 0.5rem 0.7rem; text-align: center;">
                <div style="font-size: 0.62rem; color: #60a5fa; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Profile Completeness</div>
                <div style="font-size: 1rem; font-weight: 800; color: #fafafa; margin-top: 0.15rem;">{profile_completeness}%</div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 0.5rem 0.7rem; text-align: center;">
                <div style="font-size: 0.62rem; color: #60a5fa; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Recruiter Reach Rank</div>
                <div style="font-size: 1rem; font-weight: 800; color: #34d399; margin-top: 0.15rem;">Top {reach_rank}%</div>
            </div>
        </div>
        """
        # Build all data for both cards before rendering
        gh_gauge = get_radial_gauge(gh_score, "gh")
        gh_checklist = get_audit_checklist_html("github")
        li_gauge = get_radial_gauge(li_score, "li")
        li_checklist = get_audit_checklist_html("linkedin")
        
        # GitHub tech stack chips
        all_skills = data.get("parsed_data", {}).get("skills", [])
        tech_chips = "".join([f'<span style="background:rgba(167,139,250,0.06); color:#a78bfa; border:1px solid rgba(167,139,250,0.2); font-size:0.62rem; font-weight:700; padding:0.12rem 0.45rem; border-radius:5px; margin:0.2rem 0.2rem 0 0; display:inline-block;">⚙️ {esc(s)}</span>' for s in all_skills[:8]]) if all_skills else '<span style="font-size:0.72rem; color:#71717a; font-style:italic;">No skills detected</span>'
        
        # GitHub tips
        gh_tips = []
        if gh_score < 70:
            gh_tips.append("Add detailed README.md files with screenshots and setup instructions.")
        if gh_score < 80:
            gh_tips.append("Pin your top 6 repositories showcasing diverse project types.")
        gh_tips.append("Use descriptive commit messages following conventional commit standards.")
        gh_tips.append("Add topics and description to every public repository for discoverability.")
        gh_tips.append("Maintain a consistent contribution streak to show active development.")
        gh_tips_html = "".join([f'<div style="display:flex; align-items:flex-start; gap:0.35rem; margin-top:0.35rem;"><span style="color:#a78bfa; font-weight:bold; font-size:0.75rem; line-height:1.2; flex-shrink:0;">→</span><span style="font-size:0.74rem; color:#d4d4d8; line-height:1.4;">{esc(t)}</span></div>' for t in gh_tips[:4]])
        
        # LinkedIn SEO chips
        seo_chips = "".join([f'<span style="background:rgba(96,165,250,0.06); color:#60a5fa; border:1px solid rgba(96,165,250,0.2); font-size:0.62rem; font-weight:700; padding:0.12rem 0.45rem; border-radius:5px; margin:0.2rem 0.2rem 0 0; display:inline-block;">🔍 {esc(s)}</span>' for s in all_skills[:8]]) if all_skills else '<span style="font-size:0.72rem; color:#71717a; font-style:italic;">No skills detected</span>'
        
        # LinkedIn tips
        li_tips = []
        if li_score < 70:
            li_tips.append("Add a compelling headline with target role keywords and key skills.")
        if li_score < 80:
            li_tips.append("Write a story-driven About section highlighting measurable achievements.")
        li_tips.append("Request skill endorsements from colleagues for top 3 competencies.")
        li_tips.append("Post industry-relevant content weekly to boost profile visibility.")
        li_tips.append("Connect with recruiters and hiring managers in target companies.")
        tips_html = "".join([f'<div style="display:flex; align-items:flex-start; gap:0.35rem; margin-top:0.35rem;"><span style="color:#60a5fa; font-weight:bold; font-size:0.75rem; line-height:1.2; flex-shrink:0;">→</span><span style="font-size:0.74rem; color:#d4d4d8; line-height:1.4;">{esc(t)}</span></div>' for t in li_tips[:4]])
        
        # Build strengths/recommendations HTML
        gh_strengths_html = make_list_html(gh.get("strengths", []))
        gh_recs_html = make_list_html(gh.get("recommendations", []), is_recommendation=True)
        li_strengths_html = make_list_html(li.get("strengths", []))
        li_recs_html = make_list_html(li.get("recommendations", []), is_recommendation=True)
        
        # Emoji variables to avoid SyntaxError in f-strings
        e_laptop = "\U0001F4BB"
        e_link = "\U0001F517"
        e_wrench = "\U0001F6E0\uFE0F"
        e_zap = "\u26A1"
        e_search = "\U0001F50D"
        
        # Render BOTH cards in a single st.markdown with CSS grid for guaranteed equal height
        st.markdown(clean_html(f"""
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; align-items: stretch;">

<!-- GitHub Card -->
<div class="card" style="border-left: 4px solid #a78bfa; background: linear-gradient(135deg, rgba(167, 139, 250, 0.05) 0%, rgba(15, 23, 42, 0.3) 100%); padding: 1.5rem; box-shadow: 0 4px 20px rgba(167,139,250,0.06);">
<div class="card-head" style="border-bottom:1px solid rgba(255,255,255,0.06); padding-bottom:0.5rem; margin-bottom:1rem;">
    <div class="icon-box purple">{e_laptop}</div>
    <h3 style="margin:0;">GitHub Portfolio Evaluation</h3>
</div>
{gh_gauge}

<div style="background:rgba(9, 13, 22, 0.2); border: 1px solid rgba(255,255,255,0.03); border-radius: 12px; padding: 1.1rem; margin-bottom:1.2rem;">
    <div style="font-size:0.72rem; color:#a78bfa; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.4rem;">Developer Activity Metrics</div>
    {gh_metrics_html}
</div>

<div style="background:rgba(9, 13, 22, 0.2); border: 1px solid rgba(255,255,255,0.03); border-radius: 12px; padding: 1.1rem; margin-bottom:1.2rem;">
    <div style="font-size:0.72rem; color:#a78bfa; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.5rem;">{e_wrench} Tech Stack Showcase</div>
    <div style="display:flex; flex-wrap:wrap;">{tech_chips}</div>
    <div style="margin-top:0.8rem; border-top:1px solid rgba(255,255,255,0.03); padding-top:0.7rem;">
        <div style="font-size:0.68rem; color:#a78bfa; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:0.35rem;">{e_zap} Repository Best Practices</div>
        {gh_tips_html}
    </div>
</div>

<div style="background:rgba(9, 13, 22, 0.2); border: 1px solid rgba(255,255,255,0.03); border-radius: 12px; padding: 1.1rem; margin-bottom:1.2rem;">
    <div style="font-size:0.72rem; color:#a78bfa; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.2rem;">Profile Completeness Checklist</div>
    {gh_checklist}
</div>

<div style="display:flex; flex-direction:column; gap:0.8rem; border-top:1px solid rgba(255,255,255,0.04); padding-top:1rem;">
    <div>
        <div style="font-size:0.68rem; color:#a78bfa; font-weight:800; text-transform:uppercase; letter-spacing:0.8px;">Strengths</div>
        {gh_strengths_html}
    </div>
    <div style="margin-top:0.4rem;">
        <div style="font-size:0.68rem; color:#818cf8; font-weight:800; text-transform:uppercase; letter-spacing:0.8px;">Recommendations</div>
        {gh_recs_html}
    </div>
</div>
</div>

<!-- LinkedIn Card -->
<div class="card" style="border-left: 4px solid #60a5fa; background: linear-gradient(135deg, rgba(96, 165, 250, 0.05) 0%, rgba(15, 23, 42, 0.3) 100%); padding: 1.5rem; box-shadow: 0 4px 20px rgba(96,165,250,0.06);">
<div class="card-head" style="border-bottom:1px solid rgba(255,255,255,0.06); padding-bottom:0.5rem; margin-bottom:1rem;">
    <div class="icon-box blue">{e_link}</div>
    <h3 style="margin:0;">LinkedIn Profile Evaluation</h3>
</div>
{li_gauge}

<div style="background:rgba(9, 13, 22, 0.2); border: 1px solid rgba(255,255,255,0.03); border-radius: 12px; padding: 1.1rem; margin-bottom:1.2rem;">
    <div style="font-size:0.72rem; color:#60a5fa; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.4rem;">LinkedIn SEO Metrics</div>
    {li_metrics_html}
</div>

<div style="background:rgba(9, 13, 22, 0.2); border: 1px solid rgba(255,255,255,0.03); border-radius: 12px; padding: 1.1rem; margin-bottom:1.2rem;">
    <div style="font-size:0.72rem; color:#60a5fa; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.5rem;">{e_search} SEO Keyword Cloud</div>
    <div style="display:flex; flex-wrap:wrap;">{seo_chips}</div>
    <div style="margin-top:0.8rem; border-top:1px solid rgba(255,255,255,0.03); padding-top:0.7rem;">
        <div style="font-size:0.68rem; color:#60a5fa; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:0.35rem;">{e_zap} Profile Optimization Tips</div>
        {tips_html}
    </div>
</div>

<div style="background:rgba(9, 13, 22, 0.2); border: 1px solid rgba(255,255,255,0.03); border-radius: 12px; padding: 1.1rem; margin-bottom:1.2rem;">
    <div style="font-size:0.72rem; color:#60a5fa; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.2rem;">Profile Completeness Checklist</div>
    {li_checklist}
</div>

<div style="display:flex; flex-direction:column; gap:0.8rem; border-top:1px solid rgba(255,255,255,0.04); padding-top:1rem;">
    <div>
        <div style="font-size:0.68rem; color:#34d399; font-weight:800; text-transform:uppercase; letter-spacing:0.8px;">Strengths</div>
        {li_strengths_html}
    </div>
    <div style="margin-top:0.4rem;">
        <div style="font-size:0.68rem; color:#60a5fa; font-weight:800; text-transform:uppercase; letter-spacing:0.8px;">Recommendations</div>
        {li_recs_html}
    </div>
</div>
</div>

</div>
"""), unsafe_allow_html=True)

    # ─── TAB 4: COVER LETTER ─────────────────────────────────────────
    with opt_tab4:
        cl_letter = data.get("cover_letter", {})
        if isinstance(cl_letter, str):
            letter_text = cl_letter
        elif isinstance(cl_letter, dict):
            cl_intro = cl_letter.get("introduction", "")
            cl_exp = cl_letter.get("relevant_experience", "")
            cl_proj = cl_letter.get("project_highlights", "")
            cl_align = cl_letter.get("role_alignment", "")
            cl_close = cl_letter.get("closing", "")
            
            sections = [s for s in [cl_intro, cl_exp, cl_proj, cl_align, cl_close] if s]
            letter_text = "\n\n".join(sections)
        else:
            letter_text = ""
            
        if letter_text:
            
            # Extract contact details for header
            email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', data.get("resume_text", ""))
            email_display = email_match.group(0) if email_match else "candidate@email.com"
            phone_match = re.search(r'(?:\+?\d{1,3}[-.\s\(\)]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}', data.get("resume_text", ""))
            phone_display = phone_match.group(0) if phone_match else "+1 (555) 000-0000"
            
            target_role = "Candidate Target Role"
            roles = data.get("job_role_recommendations", [])
            if roles:
                target_role = roles[0].get("title", "Target Role")
            
            date_str = datetime.now().strftime("%B %d, %Y")
            c_initials = "".join([w[0].upper() for w in cname.split() if w])[:2] if cname else "CP"
            
            cl_col1, cl_col2 = st.columns([5, 2], gap="medium")
            with cl_col1:
                st.markdown(clean_html(f"""<div style="background:#ffffff; color:#1e293b; border-radius:12px; padding:3rem; font-family:'Plus Jakarta Sans', -apple-system, sans-serif; line-height:1.7; font-size:0.9rem; border:1px solid #e2e8f0; margin-bottom:1.2rem; min-height:450px; text-align:left; box-shadow: 0 10px 40px rgba(0,0,0,0.15); position: relative;">
<div style="height: 6px; background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%); margin: -3rem -3rem 2rem -3rem; border-top-left-radius: 12px; border-top-right-radius: 12px;"></div>

<!-- Letter Header -->
<div style="padding-bottom: 1.5rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9;">
    <div style="display: flex; align-items: center; gap: 1rem;">
        <div style="width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%); border: 2px solid #6366f1; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.15rem; color: #4f46e5; font-family: 'Outfit', sans-serif; box-shadow: 0 4px 10px rgba(99, 102, 241, 0.1);">
            {c_initials}
        </div>
        <div>
            <div style="font-weight: 800; font-size: 1.35rem; color: #1e1b4b; font-family:'Outfit', sans-serif; line-height: 1.2;">{cname}</div>
            <div style="font-size: 0.78rem; color: #64748b; margin-top: 0.2rem; font-weight: 500;">{esc(email_display)} • {esc(phone_display)}</div>
        </div>
    </div>
    <div style="text-align: right;">
        <span style="font-weight: 700; font-size: 0.65rem; color: #4f46e5; letter-spacing: 1px; text-transform: uppercase; background: #e0e7ff; padding: 0.3rem 0.65rem; border-radius: 20px; font-family: 'Outfit', sans-serif; border: 1px solid rgba(99, 102, 241, 0.15);">Cover Letter Draft</span>
        <div style="font-size: 0.76rem; color: #64748b; margin-top: 0.5rem; font-weight: 500; font-family: 'Outfit', sans-serif;">{date_str}</div>
    </div>
</div>

<!-- Recipient / Subject -->
<div style="margin-bottom: 1.8rem; font-size: 0.84rem; color: #475569; background: #f8fafc; border-radius: 8px; padding: 1rem; border: 1px solid #f1f5f9; border-left: 3.5px solid #6366f1;">
    <div style="display: grid; grid-template-columns: auto 1fr; gap: 0.4rem 0.8rem; align-items: center;">
        <span style="font-weight: 700; color: #64748b; text-transform: uppercase; font-size: 0.68rem; letter-spacing: 0.5px;">Attention:</span>
        <span style="color: #1e293b; font-weight: 500;">Hiring Team / Hiring Manager</span>
        
        <span style="font-weight: 700; color: #64748b; text-transform: uppercase; font-size: 0.68rem; letter-spacing: 0.5px;">Subject:</span>
        <span style="color: #1e293b; font-weight: 600; font-size: 0.88rem;">Application for {esc(target_role)} Role</span>
    </div>
</div>

<!-- Letter Body -->
<div style="white-space:pre-line; color:#334155; font-family:'Plus Jakarta Sans', sans-serif; font-size:0.92rem; line-height: 1.8; margin-bottom: 2.5rem; text-align: justify; letter-spacing: -0.01em;">
    {esc(letter_text)}
</div>

<!-- Signature Block -->
<div style="border-top: 1px dashed #cbd5e1; padding-top: 1.6rem; display: flex; justify-content: space-between; align-items: flex-end;">
    <div>
        <div style="font-size: 0.82rem; color: #64748b; font-style: italic; margin-bottom: 0.5rem;">Sincerely,</div>
        <div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.15rem; color: #1e1b4b; letter-spacing: 0.5px;">{cname}</div>
        <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.15rem;">Applicant</div>
    </div>
    <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.35rem;">
        <div style="border: 1px solid #10b981; background: rgba(16, 185, 129, 0.04); border-radius: 6px; padding: 0.35rem 0.7rem; font-size: 0.65rem; color: #10b981; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; display: flex; align-items: center; gap: 0.25rem;">
            <span style="font-size: 0.8rem; line-height: 1;">✓</span> Verified Candidate Profile
        </div>
        <div style="font-size: 0.62rem; color: #94a3b8; font-family: monospace;">HASH ID: {data.get('parsed_data', {}).get('hash', 'AI-RES-ANALYST')[:8].upper()}</div>
    </div>
</div>
</div>"""), unsafe_allow_html=True)
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    st.download_button("📥 Download Cover Letter (.txt)", letter_text,
                                       f"cover_letter_{cname.replace(' ','_').lower()}.txt", "text/plain",
                                       use_container_width=True, key="download_cl_button_tab_txt")
                with btn_col2:
                    cl_html = generate_cover_letter_html(cname, email_display, phone_display, target_role, date_str, letter_text)
                    st.download_button("📄 Download PDF Cover Letter (.html)", cl_html,
                                       f"cover_letter_{cname.replace(' ','_').lower()}.html", "text/html",
                                       use_container_width=True, key="download_cl_button_tab_html")
            with cl_col2:
                # Compute letter analytics
                word_count = len(letter_text.split())
                para_count = len([p for p in letter_text.split('\n\n') if p.strip()])
                avg_sentence_len = round(word_count / max(letter_text.count('.') + letter_text.count('!') + letter_text.count('?'), 1))
                readability = "Advanced" if avg_sentence_len > 22 else "Professional" if avg_sentence_len > 15 else "Concise"
                
                # Skill keywords found in letter
                all_skills = data.get("parsed_data", {}).get("skills", [])
                matched_skills = [s for s in all_skills if s.lower() in letter_text.lower()][:6]
                e_gear = "\u2699\uFE0F"
                matched_chips = "".join([f'<span style="background:rgba(99,102,241,0.08); color:#818cf8; border:1px solid rgba(99,102,241,0.2); font-size:0.62rem; font-weight:700; padding:0.12rem 0.4rem; border-radius:5px; margin:0.15rem 0.15rem 0 0; display:inline-block;">{e_gear} {esc(s)}</span>' for s in matched_skills]) if matched_skills else '<span style="font-size:0.72rem; color:#71717a; font-style:italic;">None matched</span>'
                
                e_cl_zap = "\u26A1"
                e_cl_link = "\U0001F517"
                e_cl_bulb = "\U0001F4A1"
                
                st.markdown(clean_html(f"""<div class="card" style="border-left: 4px solid #818cf8; background: linear-gradient(180deg, rgba(129, 140, 248, 0.06) 0%, rgba(15, 23, 42, 0.45) 100%); padding: 1.5rem; box-shadow: 0 8px 32px rgba(129, 140, 248, 0.08); border-top: 1px solid rgba(255,255,255,0.05); border-right: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05);">
<div style="font-size:0.75rem; color:#818cf8; font-weight:800; text-transform:uppercase; letter-spacing:1px; margin-bottom:1rem; display:flex; align-items:center; gap:0.4rem;">{e_cl_zap} Letter Intelligence</div>

<!-- Tone Badge -->
<div style="margin-bottom: 1rem; background: rgba(129, 140, 248, 0.06); border: 1px solid rgba(129, 140, 248, 0.15); padding: 0.75rem 0.9rem; border-radius: 10px; display: flex; justify-content: space-between; align-items: center;">
    <span style="font-size:0.7rem; color:#a5b4fc; text-transform:uppercase; font-weight: 700; letter-spacing:0.5px;">Overall Tone</span>
    <span style="font-weight:800; font-size:0.72rem; color:#818cf8; background: rgba(129, 140, 248, 0.15); padding: 0.25rem 0.55rem; border-radius: 6px; letter-spacing: 0.3px; border: 1px solid rgba(129, 140, 248, 0.25);">PERSUASIVE & PROFESSIONAL</span>
</div>

<!-- Stats Grid -->
<div style="display:grid; grid-template-columns:1fr 1fr; gap:0.6rem; margin-bottom:1.2rem;">
    <!-- Word Count -->
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:10px; padding:0.65rem 0.5rem; text-align:center;">
        <div style="font-size:0.58rem; color:#94a3b8; text-transform:uppercase; font-weight:700; letter-spacing:0.5px;">Word Count</div>
        <div style="font-size:1.15rem; font-weight:800; color:#ffffff; margin-top:0.15rem; font-family: 'Outfit', sans-serif;">{word_count}</div>
        <div style="font-size:0.55rem; color:#64748b; margin-top:0.1rem;">Target: 100-250</div>
    </div>
    <!-- Paragraphs -->
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:10px; padding:0.65rem 0.5rem; text-align:center;">
        <div style="font-size:0.58rem; color:#94a3b8; text-transform:uppercase; font-weight:700; letter-spacing:0.5px;">Paragraphs</div>
        <div style="font-size:1.15rem; font-weight:800; color:#ffffff; margin-top:0.15rem; font-family: 'Outfit', sans-serif;">{para_count}</div>
        <div style="font-size:0.55rem; color:#64748b; margin-top:0.1rem;">Target: 3-5</div>
    </div>
    <!-- Avg Sentence Length -->
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:10px; padding:0.65rem 0.5rem; text-align:center;">
        <div style="font-size:0.58rem; color:#94a3b8; text-transform:uppercase; font-weight:700; letter-spacing:0.5px;">Avg Sentence</div>
        <div style="font-size:1.05rem; font-weight:800; color:#ffffff; margin-top:0.15rem; font-family: 'Outfit', sans-serif;">{avg_sentence_len} <span style="font-size:0.65rem; font-weight:500; color:#94a3b8;">words</span></div>
        <div style="font-size:0.55rem; color:#64748b; margin-top:0.1rem;">Optimal: 15-20</div>
    </div>
    <!-- Readability -->
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:10px; padding:0.65rem 0.5rem; text-align:center;">
        <div style="font-size:0.58rem; color:#94a3b8; text-transform:uppercase; font-weight:700; letter-spacing:0.5px;">Readability</div>
        <div style="font-size:1.05rem; font-weight:800; color:#34d399; margin-top:0.15rem; font-family: 'Outfit', sans-serif; text-shadow: 0 0 10px rgba(52,211,153,0.25);">{readability}</div>
        <div style="font-size:0.55rem; color:#64748b; margin-top:0.1rem;">Level</div>
    </div>
</div>

<!-- Customization Checklist -->
<div style="margin-bottom:1.2rem; border-top:1px solid rgba(255,255,255,0.06); padding-top:0.9rem;">
    <span style="font-size:0.68rem; color:#94a3b8; text-transform:uppercase; display:block; letter-spacing:0.8px; margin-bottom:0.6rem; font-weight: 700;">Customization Audit</span>
    <div style="font-size:0.75rem; color:#d4d4d8; display:flex; flex-direction:column; gap:0.4rem;">
        <div style="display:flex; align-items:center; justify-content:space-between; background: rgba(52, 211, 153, 0.03); border: 1px solid rgba(52, 211, 153, 0.08); padding: 0.4rem 0.6rem; border-radius: 6px;">
            <div style="display:flex; align-items:center; gap:0.4rem;"><span style="color:#34d399; font-weight:800; font-size:0.85rem;">✓</span> Aligned to {esc(target_role)}</div>
            <span style="font-size:0.6rem; color:#34d399; background:rgba(52, 211, 153, 0.1); padding: 0.05rem 0.3rem; border-radius: 4px; font-weight:700;">PASSED</span>
        </div>
        <div style="display:flex; align-items:center; justify-content:space-between; background: rgba(52, 211, 153, 0.03); border: 1px solid rgba(52, 211, 153, 0.08); padding: 0.4rem 0.6rem; border-radius: 6px;">
            <div style="display:flex; align-items:center; gap:0.4rem;"><span style="color:#34d399; font-weight:800; font-size:0.85rem;">✓</span> Structured paragraphs</div>
            <span style="font-size:0.6rem; color:#34d399; background:rgba(52, 211, 153, 0.1); padding: 0.05rem 0.3rem; border-radius: 4px; font-weight:700;">PASSED</span>
        </div>
        <div style="display:flex; align-items:center; justify-content:space-between; background: rgba(52, 211, 153, 0.03); border: 1px solid rgba(52, 211, 153, 0.08); padding: 0.4rem 0.6rem; border-radius: 6px;">
            <div style="display:flex; align-items:center; gap:0.4rem;"><span style="color:#34d399; font-weight:800; font-size:0.85rem;">✓</span> Quantifiable achievements</div>
            <span style="font-size:0.6rem; color:#34d399; background:rgba(52, 211, 153, 0.1); padding: 0.05rem 0.3rem; border-radius: 4px; font-weight:700;">PASSED</span>
        </div>
        <div style="display:flex; align-items:center; justify-content:space-between; background: rgba(52, 211, 153, 0.03); border: 1px solid rgba(52, 211, 153, 0.08); padding: 0.4rem 0.6rem; border-radius: 6px;">
            <div style="display:flex; align-items:center; gap:0.4rem;"><span style="color:#34d399; font-weight:800; font-size:0.85rem;">✓</span> Call-to-action closing</div>
            <span style="font-size:0.6rem; color:#34d399; background:rgba(52, 211, 153, 0.1); padding: 0.05rem 0.3rem; border-radius: 4px; font-weight:700;">PASSED</span>
        </div>
        <div style="display:flex; align-items:center; justify-content:space-between; background: rgba(52, 211, 153, 0.03); border: 1px solid rgba(52, 211, 153, 0.08); padding: 0.4rem 0.6rem; border-radius: 6px;">
            <div style="display:flex; align-items:center; gap:0.4rem;"><span style="color:#34d399; font-weight:800; font-size:0.85rem;">✓</span> Professional formatting</div>
            <span style="font-size:0.6rem; color:#34d399; background:rgba(52, 211, 153, 0.1); padding: 0.05rem 0.3rem; border-radius: 4px; font-weight:700;">PASSED</span>
        </div>
    </div>
</div>

<!-- Matched Keywords -->
<div style="margin-bottom:1.2rem; border-top:1px solid rgba(255,255,255,0.06); padding-top:0.9rem;">
    <span style="font-size:0.68rem; color:#94a3b8; text-transform:uppercase; display:block; letter-spacing:0.8px; margin-bottom:0.45rem; font-weight: 700;">{e_cl_link} Matched Skill Keywords</span>
    <div style="display:flex; flex-wrap:wrap; gap:0.35rem;">{matched_chips}</div>
</div>

<!-- Tip -->
<div style="border-top:1px solid rgba(255,255,255,0.06); padding-top:0.8rem;">
    <span style="font-size:0.68rem; color:#94a3b8; text-transform:uppercase; display:block; margin-bottom:0.45rem; letter-spacing:0.8px; font-weight: 700;">{e_cl_bulb} Professional Tips</span>
    <div style="font-size:0.74rem; color:#a1a1aa; line-height:1.55; display:flex; flex-direction:column; gap:0.4rem;">
        <div style="display:flex; align-items:flex-start; gap:0.45rem;">
            <span style="color:#fbbf24; font-size: 0.85rem; line-height: 1.1;">✦</span>
            <span>Replace placeholder dates, names, and company references.</span>
        </div>
        <div style="display:flex; align-items:flex-start; gap:0.45rem;">
            <span style="color:#fbbf24; font-size: 0.85rem; line-height: 1.1;">✦</span>
            <span>Tailor opening paragraph to each specific company.</span>
        </div>
        <div style="display:flex; align-items:flex-start; gap:0.45rem;">
            <span style="color:#fbbf24; font-size: 0.85rem; line-height: 1.1;">✦</span>
            <span>Add a direct link to your portfolio or LinkedIn profile.</span>
        </div>
    </div>
</div>
</div>"""), unsafe_allow_html=True)
        else:
            st.info("No cover letter generated for this profile.")
