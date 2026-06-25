def esc(t):
    if not isinstance(t, str):
        return str(t)
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def v_cls(v):
    vl = v.lower()
    if "strong" in vl:
        return "vp-strong"
    if "good" in vl:
        return "vp-good"
    return "vp-weak"

def s_label(s):
    try:
        s = float(s)
    except (TypeError, ValueError):
        return "Needs Improvement"
    if s >= 85:
        return "Excellent"
    if s >= 70:
        return "Good"
    if s >= 50:
        return "Average"
    if s >= 30:
        return "Below Average"
    return "Needs Improvement"

def p_badge(val):
    v_lower = val.lower()
    if "high" in v_lower:
        return '<span class="t t-green">High</span>'
    if "mod" in v_lower:
        return '<span class="t t-blue">Moderate</span>'
    return '<span class="t t-red">Low</span>'

def generate_html_report(data):
    cname = esc(data.get("candidate_name", "Candidate"))
    ats = data.get("ats_score", 0)
    tier = esc(data.get("tier", "N/A"))
    
    def render_list_items(lst):
        if not lst:
            return "<li>None identified</li>"
        return "".join([f"<li>{esc(item)}</li>" for item in lst])

    def get_progress_bar(val, color="#4f46e5"):
        return f'''
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
            <div style="flex: 1; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden;">
                <div style="width: {val}%; height: 100%; background: {color}; border-radius: 4px;"></div>
            </div>
            <span style="font-size: 13px; font-weight: 700; color: #475569; width: 35px; text-align: right;">{val}%</span>
        </div>
        '''

    dims = data.get("dimensions", {})
    dim_html = ""
    dim_titles = {
        "technical_skills": "Technical Skills Match",
        "experience_relevance": "Experience Relevance",
        "leadership_growth": "Leadership & Growth",
        "cultural_fit": "Cultural Fit",
        "presentation_quality": "Presentation Quality",
        "sustainability": "Sustainability",
        "innovation_impact": "Innovation & Impact"
    }
    for k, title in dim_titles.items():
        dim_data = dims.get(k, {})
        d_score = dim_data.get("score", 0)
        d_exp = esc(dim_data.get("explanation", "Not available"))
        dim_html += f"""
        <div style="margin-bottom: 12px; page-break-inside: avoid;">
            <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: 700; color: #1e293b; margin-bottom: 3px;">
                <span>{title}</span>
                <span>{d_score}/100</span>
            </div>
            {get_progress_bar(d_score, "#6366f1")}
            <div style="font-size: 11px; color: #64748b; line-height: 1.4; margin-top: -3px; margin-bottom: 10px;">{d_exp}</div>
        </div>
        """

    jm = data.get("job_matching", {})
    gaps = jm.get("critical_gaps", [])
    gaps_html = ""
    if gaps:
        for g in gaps:
            g_skill = esc(g.get("skill", ""))
            g_sev = esc(g.get("severity", "medium")).lower()
            g_cand = esc(g.get("candidate_level", "none"))
            g_req = esc(g.get("required", "advanced"))
            sev_color = "#ef4444" if g_sev in ["high", "critical"] else "#f97316" if g_sev == "medium" else "#3b82f6"
            gaps_html += f"""
            <div style="margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #f1f5f9;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; font-size: 13px; color: #0f172a;">{g_skill}</span>
                    <span style="background: {sev_color}11; color: {sev_color}; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; text-transform: uppercase;">{g_sev}</span>
                </div>
                <div style="font-size: 12px; color: #64748b; margin-top: 2px;">Required: <strong>{g_req}</strong> | Candidate: <span style="color: #ef4444;">{g_cand}</span></div>
            </div>
            """
    else:
        gaps_html = '<div style="color: #94a3b8; font-size: 13px;">No critical requirement gaps detected.</div>'

    strengths = jm.get("transferable_strengths", [])
    strengths_html = ""
    if strengths:
        for s in strengths:
            s_name = esc(s.get("strength", ""))
            s_rel = esc(s.get("relevance", ""))
            strengths_html += f"""
            <div style="margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #f1f5f9;">
                <div style="font-weight: 700; font-size: 13px; color: #15803d;">✓ {s_name}</div>
                <div style="font-size: 12px; color: #64748b; margin-top: 2px;">{s_rel}</div>
            </div>
            """
    else:
        strengths_html = '<div style="color: #94a3b8; font-size: 13px;">No transferable strengths identified.</div>'

    roadmap = data.get("roadmap", {})
    phases = [
        ("days_0_3_months", "Phase 1: 0 - 3 Months", "Foundation", "#818cf8"),
        ("days_3_6_months", "Phase 2: 3 - 6 Months", "Development", "#60a5fa"),
        ("days_6_12_months", "Phase 3: 6 - 12 Months", "Placement", "#34d399"),
        ("days_12_24_months", "Phase 4: 12 - 24 Months", "Long-term", "#a78bfa")
    ]
    roadmap_html = ""
    for k, label, title, color in phases:
        p_data = roadmap.get(k, {})
        p_focus = esc(p_data.get("focus", "Not available"))
        p_skills = ", ".join([esc(s) for s in p_data.get("skills", [])])
        p_actions = "".join([f"<li>{esc(a)}</li>" for a in p_data.get("actions", [])])
        p_roles = ", ".join([esc(r) for r in p_data.get("roles_to_explore", [])])
        
        roadmap_html += f"""
        <div style="margin-bottom: 20px; border-left: 4px solid {color}; padding-left: 15px; page-break-inside: avoid;">
            <div style="font-size: 12px; font-weight: 700; color: {color}; text-transform: uppercase; letter-spacing: 0.5px;">{label}</div>
            <div style="font-size: 16px; font-weight: 800; color: #0f172a; margin-top: 2px;">{title}</div>
            <div style="font-size: 13px; color: #475569; font-style: italic; margin-top: 4px; margin-bottom: 8px;">{p_focus}</div>
            
            <div style="font-size: 13px; margin-bottom: 6px;">
                <strong>Key Skills:</strong> <span style="color: {color}; font-weight: 600;">{p_skills if p_skills else 'None'}</span>
            </div>
            
            <div style="font-size: 13px; margin-bottom: 6px;">
                <strong>Recommended Actions:</strong>
                <ul style="margin: 4px 0; padding-left: 20px; line-height: 1.4;">
                    {p_actions if p_actions else '<li>None</li>'}
                </ul>
            </div>
            
            <div style="font-size: 13px;">
                <strong>Roles to Explore:</strong> <span style="color: #475569;">{p_roles if p_roles else 'None'}</span>
            </div>
        </div>
        """

    paths = data.get("career_paths", [])
    paths_html = ""
    if paths:
        for p in paths[:3]:
            p_name = esc(p.get("path_name", "N/A"))
            p_sal = esc(p.get("salary_potential", "N/A"))
            p_time = p.get("timeline_years", 5)
            p_desc = esc(p.get("description", "N/A"))
            paths_html += f"""
            <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; background: #f8fafc; page-break-inside: avoid; margin-bottom: 12px;">
                <div style="font-weight: 700; font-size: 15px; color: #4f46e5; margin-bottom: 4px;">{p_name}</div>
                <div style="display: flex; gap: 10px; margin-bottom: 8px; align-items: center;">
                    <span style="background: #f0fdf4; color: #166534; font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 4px;">💵 {p_sal}</span>
                    <span style="font-size: 11px; color: #64748b; font-weight: 600;">⏱️ Timeline: {p_time} Years</span>
                </div>
                <div style="font-size: 12px; color: #475569; line-height: 1.5;">{p_desc}</div>
            </div>
            """
    else:
        paths_html = '<div style="color: #94a3b8; font-size: 13px;">No career path scenarios identified.</div>'

    rv = data.get("final_recruiter_verdict", {})
    verdict = esc(rv.get("verdict", "N/A"))
    verdict_emoji = esc(rv.get("verdict_emoji", "📋"))
    conclusion = esc(rv.get("conclusion", "N/A"))

    questions = data.get("interview_questions", {})
    if not isinstance(questions, dict):
        q_list = questions if isinstance(questions, list) else []
        questions = {
            "technical": q_list,
            "project_based": [],
            "behavioral": [],
            "role_specific": []
        }
    questions_html = ""
    q_cats = [
        ("Technical Assessment Questions", questions.get("technical", []), "#3b82f6"),
        ("Project-Based Deep-Dive", questions.get("project_based", []), "#10b981"),
        ("Behavioral & Team Alignment", questions.get("behavioral", []), "#f59e0b"),
        ("Role-Specific Scenario Questions", questions.get("role_specific", []), "#8b5cf6")
    ]
    for label, q_list, q_color in q_cats:
        if q_list:
            questions_html += f"""
            <div style="margin-top: 15px; page-break-inside: avoid;">
                <div style="font-size: 12px; font-weight: 700; color: {q_color}; text-transform: uppercase; letter-spacing: 0.5px; border-left: 3px solid {q_color}; padding-left: 8px; margin-bottom: 6px;">{label}</div>
                <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #334155; line-height: 1.5;">
                    {"".join([f"<li style='margin-bottom: 5px;'>{esc(q)}</li>" for q in q_list[:3]])}
                </ul>
            </div>
            """
    if not questions_html:
        questions_html = '<div style="color: #94a3b8; font-size: 13px;">No interview questions available.</div>'

    rq = data.get("resume_quality_report", {})
    rq_score = rq.get("score", 0)
    rq_analysis = esc(rq.get("analysis", "Not available"))
    rq_strengths = render_list_items(rq.get("strengths", []))
    rq_weaknesses = render_list_items(rq.get("weaknesses", []))

    p_summary = data.get("profile_summary", {})
    skills_identified = ", ".join([esc(s) for s in p_summary.get("skills_identified", [])])
    exp_summary = esc(p_summary.get("experience_summary", "Not available"))
    edu_summary = esc(p_summary.get("education_summary", "Not available"))
    proj_summary = esc(p_summary.get("projects_summary", "Not available"))

    v_bg, v_text = "#f1f5f9", "#475569"
    if "strong" in verdict.lower() or "exceptional" in verdict.lower():
        v_bg, v_text = "#f0fdf4", "#166534"
    elif "qualified" in verdict.lower() or "average" in verdict.lower() or "weak" not in verdict.lower():
        v_bg, v_text = "#eff6ff", "#1d4ed8"
    else:
        v_bg, v_text = "#fef2f2", "#991b1b"

    hard_s = jm.get("match_breakdown", {}).get("hard_skills", 0)
    exp_s = jm.get("match_breakdown", {}).get("experience", 0)
    growth_s = jm.get("match_breakdown", {}).get("growth_potential", 0)
    cult_s = jm.get("match_breakdown", {}).get("cultural_fit", 0)
    m_rec = esc(jm.get("recommendation", "N/A"))

    rec_hm = data.get("recommendations_for_hiring_manager", [])
    rec_cand = data.get("recommendations_for_candidate", [])

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ATS Candidate Report - {cname}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700;900&display=swap');
        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1e293b;
            background-color: #f8fafc;
            line-height: 1.5;
            margin: 0;
            padding: 0;
        }}
        .no-print-bar {{
            background: #ffffff;
            border-bottom: 1px solid #e2e8f0;
            padding: 12px;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .print-btn {{
            background: #4f46e5;
            color: #ffffff;
            border: none;
            padding: 8px 18px;
            font-size: 14px;
            font-weight: 700;
            border-radius: 6px;
            cursor: pointer;
            box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.1);
            font-family: 'Plus Jakarta Sans', sans-serif;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .print-btn:hover {{
            background: #4338ca;
        }}
        .container {{
            max-width: 840px;
            margin: 30px auto;
            background: #ffffff;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            border: 1px solid #e2e8f0;
        }}
        h1, h2, h3, h4, h5 {{
            font-family: 'Outfit', sans-serif;
            color: #0f172a;
            margin-top: 0;
        }}
        .header-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 2px solid #f1f5f9;
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        .logo {{
            font-family: 'Outfit', sans-serif;
            font-size: 20px;
            font-weight: 900;
            color: #4f46e5;
        }}
        .logo span {{
            color: #f97316;
        }}
        .candidate-meta {{
            margin-top: 10px;
        }}
        .candidate-name {{
            font-size: 28px;
            font-weight: 900;
            color: #0f172a;
            letter-spacing: -0.5px;
            margin: 0 0 4px 0;
        }}
        .candidate-title {{
            font-size: 14px;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 0;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 24px;
            margin-bottom: 30px;
        }}
        .score-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        .score-circle {{
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: #4f46e5;
            color: #ffffff;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin-bottom: 12px;
            font-family: 'Outfit', sans-serif;
        }}
        .score-val {{
            font-size: 36px;
            font-weight: 900;
            line-height: 1;
        }}
        .score-lbl {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            opacity: 0.9;
        }}
        .tier-badge {{
            background: #e0e7ff;
            color: #4338ca;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 10px;
            margin-bottom: 8px;
        }}
        .section-box {{
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            page-break-inside: avoid;
        }}
        .section-title {{
            font-size: 16px;
            font-weight: 700;
            color: #0f172a;
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 8px;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .two-col-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        ul {{
            margin: 0;
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 5px;
        }}
        .page-break {{
            page-break-before: always;
        }}
        @media print {{
            body {{
                background: #ffffff;
                color: #000000;
            }}
            .no-print-bar {{
                display: none !important;
            }}
            .container {{
                margin: 0;
                padding: 0;
                border: none;
                box-shadow: none;
                max-width: 100%;
            }}
            .score-circle {{
                background: #4f46e5 !important;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            .tier-badge {{
                background: #e0e7ff !important;
                color: #4338ca !important;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
        }}
    </style>
</head>
<body>
    <div class="no-print-bar">
        <button class="print-btn" onclick="window.print()">🖨️ Export PDF / Print Report</button>
    </div>
    
    <div class="container">
        <!-- Header -->
        <div class="header-row">
            <div class="candidate-meta">
                <h1 class="candidate-name">{cname}</h1>
                <p class="candidate-title">ATS Candidate Evaluation Report</p>
            </div>
            <div style="text-align: right;">
                <div class="logo">Resume<span>IQ</span></div>
                <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Recruitment Engine v3.0</div>
            </div>
        </div>
        
        <!-- Summary Section -->
        <div class="summary-grid">
            <div class="score-card">
                <div class="score-circle">
                    <span class="score-val">{ats}</span>
                    <span class="score-lbl">ATS Match</span>
                </div>
                <div class="tier-badge">{tier}</div>
                <div style="font-size: 11px; color: #64748b; line-height: 1.3;">
                    Quality: {rq_score}/100<br>
                    Readiness: {data.get("interview_readiness_score", 0)}/100
                </div>
            </div>
            
            <div class="section-box" style="margin: 0;">
                <div class="section-title" style="border: none; margin-bottom: 6px;">Profile Summary</div>
                <div style="font-size: 13px; color: #475569; line-height: 1.5;">
                    <div style="margin-bottom: 8px;"><strong>Skills:</strong> {skills_identified if skills_identified else 'N/A'}</div>
                    <div style="margin-bottom: 8px;"><strong>Experience:</strong> {exp_summary}</div>
                    <div style="margin-bottom: 8px;"><strong>Education:</strong> {edu_summary}</div>
                    <div><strong>Projects:</strong> {proj_summary}</div>
                </div>
            </div>
        </div>

        <!-- 7 Scoring Dimensions -->
        <div class="section-box">
            <div class="section-title">7-Axis Intelligence Scoring</div>
            <div class="two-col-grid">
                <div style="grid-column: 1 / span 2;">
                    {dim_html}
                </div>
            </div>
        </div>

        <div class="page-break"></div>

        <!-- Job Fit Engine -->
        <div class="section-box">
            <div class="section-title">Intelligent Job Fit Match</div>
            
            <div style="display: flex; gap: 15px; margin-bottom: 15px; background: #f8fafc; border-radius: 8px; padding: 12px; font-size: 13px;">
                <div style="flex: 1; text-align: center; border-right: 1px solid #e2e8f0;">
                    <strong style="color: #4f46e5; font-size: 15px;">{hard_s}%</strong><br><span style="color: #64748b; font-size: 11px;">Hard Skills</span>
                </div>
                <div style="flex: 1; text-align: center; border-right: 1px solid #e2e8f0;">
                    <strong style="color: #0284c7; font-size: 15px;">{exp_s}%</strong><br><span style="color: #64748b; font-size: 11px;">Experience</span>
                </div>
                <div style="flex: 1; text-align: center; border-right: 1px solid #e2e8f0;">
                    <strong style="color: #7c3aed; font-size: 15px;">{growth_s}%</strong><br><span style="color: #64748b; font-size: 11px;">Growth</span>
                </div>
                <div style="flex: 1; text-align: center;">
                    <strong style="color: #16a34a; font-size: 15px;">{cult_s}%</strong><br><span style="color: #64748b; font-size: 11px;">Soft Skills</span>
                </div>
            </div>
            
            <div style="font-size: 13px; margin-bottom: 15px; line-height: 1.5; background: {v_bg}; border-left: 4px solid {v_text}; padding: 10px; border-radius: 0 6px 6px 0; color: {v_text};">
                <strong>Verdict Match:</strong> {m_rec}
            </div>

            <div class="two-col-grid">
                <div style="border: 1px solid #ffe4e4; background: #fff8f8; border-radius: 8px; padding: 12px;">
                    <div style="font-weight: 700; font-size: 12px; color: #ef4444; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">⚠️ Critical Gaps</div>
                    {gaps_html}
                </div>
                <div style="border: 1px solid #d1fae5; background: #f0fdf4; border-radius: 8px; padding: 12px;">
                    <div style="font-weight: 700; font-size: 12px; color: #065f46; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">✨ Transferable Strengths</div>
                    {strengths_html}
                </div>
            </div>
        </div>

        <!-- Personalised Upskilling Roadmap -->
        <div class="section-box">
            <div class="section-title">Personalized Upskilling Roadmap</div>
            {roadmap_html}
        </div>

        <div class="page-break"></div>

        <!-- Career Path Scenarios -->
        <div class="section-box">
            <div class="section-title">Career Path Scenarios</div>
            <div style="display: grid; grid-template-columns: 1fr; gap: 12px;">
                {paths_html}
            </div>
        </div>

        <!-- Recruiter Verdict -->
        <div class="section-box">
            <div class="section-title">Recruitment Verdict & Verdict Details</div>
            
            <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                <div style="flex: 1; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase;">Final Verdict</div>
                    <div style="font-size: 18px; font-weight: 800; color: #0f172a; margin-top: 4px;">{verdict_emoji} {verdict}</div>
                </div>
                <div style="flex: 1; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase;">Retention Risk</div>
                    <div style="font-size: 18px; font-weight: 800; color: #ef4444; margin-top: 4px;">{esc(data.get("risk_assessment", {}).get("retention_risk", "Low"))}</div>
                </div>
            </div>
            
            <div style="font-size: 13px; color: #475569; line-height: 1.5; margin-bottom: 15px;">
                <strong>Recruiter Verdict Conclusion:</strong> {conclusion}
            </div>
            
            <div style="font-size: 13px; color: #475569; line-height: 1.5; margin-bottom: 15px;">
                <strong>Retention Risk Justification:</strong> {esc(data.get("risk_assessment", {}).get("explanation", "Not available"))}
            </div>

            <div class="two-col-grid" style="margin-top: 15px;">
                <div>
                    <div style="font-weight: 700; font-size: 12px; color: #0f172a; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px;">📋 For Hiring Managers</div>
                    <ul style="font-size: 13px; color: #475569; padding-left: 20px;">
                        {render_list_items(rec_hm)}
                    </ul>
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 12px; color: #0f172a; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px;">👤 For Candidate Improvement</div>
                    <ul style="font-size: 13px; color: #475569; padding-left: 20px;">
                        {render_list_items(rec_cand)}
                    </ul>
                </div>
            </div>
        </div>

        <!-- Resume Quality Evaluation -->
        <div class="section-box">
            <div class="section-title">Resume Quality Evaluation (ATS Compatibility)</div>
            <div style="font-size: 13px; color: #475569; line-height: 1.5; margin-bottom: 15px;">
                <strong>ATS Evaluation Quality Score:</strong> <span style="font-weight: 700; color: #4f46e5;">{rq_score}/100</span>
                <p>{rq_analysis}</p>
            </div>
            <div class="two-col-grid">
                <div>
                    <div style="font-weight: 700; font-size: 12px; color: #16a34a; text-transform: uppercase; margin-bottom: 6px;">Strengths</div>
                    <ul style="font-size: 13px; color: #475569; padding-left: 20px;">
                        {rq_strengths}
                    </ul>
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 12px; color: #dc2626; text-transform: uppercase; margin-bottom: 6px;">Weaknesses</div>
                    <ul style="font-size: 13px; color: #475569; padding-left: 20px;">
                        {rq_weaknesses}
                    </ul>
                </div>
            </div>
        </div>

        <!-- Curated Interview Prep Questions -->
        <div class="section-box">
            <div class="section-title">Curated Interview Assessment Questions</div>
            {questions_html}
        </div>
        
        <div style="text-align: center; font-size: 11px; color: #94a3b8; margin-top: 30px; border-top: 1px solid #f1f5f9; padding-top: 15px;">
            Report generated automatically by ResumePro.
        </div>
    </div>
</body>
</html>
"""
    return html_content
