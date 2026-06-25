import plotly.graph_objects as go

def make_gauge(score):
    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0.0
    color = "#4ade80" if score >= 80 else "#60a5fa" if score >= 60 else "#fbbf24" if score >= 40 else "#f87171"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={"font": {"size": 54, "color": color, "family": "Outfit"}, "suffix": "<span style='font-size:20px;color:#52525b'> / 100</span>"},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": "rgba(0,0,0,0)",
                     "tickfont": {"color": "#3f3f46", "size": 9}, "dtick": 25},
            "bar": {"color": color, "thickness": 0.7},
            "bgcolor": "rgba(255,255,255,0.015)", "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(248,113,113,0.04)"},
                {"range": [40, 60], "color": "rgba(251,191,36,0.04)"},
                {"range": [60, 80], "color": "rgba(96,165,250,0.04)"},
                {"range": [80, 100], "color": "rgba(74,222,128,0.04)"},
            ],
            "threshold": {"line": {"color": color, "width": 2}, "thickness": 0.8, "value": score},
        },
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      height=255, margin=dict(l=25, r=25, t=30, b=5), font=dict(family="Plus Jakarta Sans"))
    return fig

def make_radar(data_or_bd):
    if not isinstance(data_or_bd, dict):
        data_or_bd = {}
        
    # Check if this contains the new dimensions
    if "technical_skills" in data_or_bd or "experience_relevance" in data_or_bd:
        cats = [
            "Technical Skills", "Experience Relevance", "Leadership & Growth", 
            "Cultural/Team Fit", "Presentation Quality", "Sustainability", "Innovation & Impact"
        ]
        keys = [
            "technical_skills", "experience_relevance", "leadership_growth", 
            "cultural_fit", "presentation_quality", "sustainability", "innovation_impact"
        ]
        vals = []
        for k in keys:
            val_obj = data_or_bd.get(k, {})
            if isinstance(val_obj, dict):
                score = val_obj.get("score", 0)
            else:
                try:
                    score = float(val_obj)
                except (TypeError, ValueError):
                    score = 0
            vals.append(float(score))
    else:
        # Fallback to old score_breakdown
        cats = ["Skills Match", "Experience Align", "Projects Eval", "Formatting & Quality"]
        keys = ["skills", "experience", "projects", "formatting"]
        vals = []
        for k in keys:
            try:
                # Handle conversion if old key exists in the input dictionary
                old_keys = {
                    "skills": "skill_match",
                    "experience": "experience_relevance",
                    "projects": "project_relevance",
                    "formatting": "resume_quality"
                }
                val = data_or_bd.get(k)
                if val is None and k in old_keys:
                    val = data_or_bd.get(old_keys[k], 0)
                vals.append(float(val if val is not None else 0))
            except (TypeError, ValueError):
                vals.append(0.0)
                
    vals.append(vals[0]); cats.append(cats[0])
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals, theta=cats, fill="toself",
        fillcolor="rgba(99,102,241,0.08)", line=dict(color="#6366f1", width=2),
        marker=dict(size=6, color="#818cf8"),
    ))
    fig.update_layout(
        polar=dict(bgcolor="rgba(0,0,0,0)",
                   radialaxis=dict(visible=True, range=[0,100], tickfont=dict(color="#3f3f46",size=8),
                                   gridcolor="rgba(255,255,255,0.03)", linecolor="rgba(255,255,255,0.03)"),
                   angularaxis=dict(tickfont=dict(color="#71717a",size=9,family="Plus Jakarta Sans"),
                                    gridcolor="rgba(255,255,255,0.03)", linecolor="rgba(255,255,255,0.04)")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False, height=280, margin=dict(l=60,r=60,t=25,b=25), font=dict(family="Plus Jakarta Sans"),
    )
    return fig
