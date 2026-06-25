import streamlit as st
from report_generator import esc, p_badge

def clean_html(html_str):
    if not html_str:
        return ""
    return "\n".join([line.strip() for line in html_str.split("\n")])

def get_strategy_for_question(q, category_key):
    q_lower = q.lower()
    
    # Check for behavioral/leadership/mentoring/team keywords
    if any(k in q_lower for k in ["mentor", "lead", "manage", "team", "conflict", "disagreement", "behavioral", "situation", "weakness", "strength", "describe a time", "tell me about"]):
        return [
            ("Context / Problem", "Briefly outline the situation and the task or stakes involved using the STAR methodology."),
            ("Your Personal Action", "Explain the specific decisions, communications, or steps you took (emphasize 'I' rather than 'we')."),
            ("Result & Key Learnings", "Finish with the measurable result and what you learned from the experience for future challenges.")
        ]
    # Check for scenario/design/architecture/scale/system keywords
    elif any(k in q_lower for k in ["design", "architecture", "scale", "system", "scenario", "how would you handle", "what would you do if"]):
        return [
            ("Clarify Scope & Assumptions", "Begin by highlighting any assumptions you make to narrow down the scenario."),
            ("Structured Deconstruction", "Break down the issue into immediate hotfixes versus long-term strategic solutions."),
            ("Decision Justification", "Weigh the trade-offs of other choices and explain how your solution aligns with business priority or system reliability.")
        ]
    # Check for project-specific keywords
    elif any(k in q_lower for k in ["project", "resume", "experience with", "built", "implemented in your"]):
        return [
            ("Situation & Role", "Set the context: introduce the project, the primary technical goal, and your ownership."),
            ("Technical Obstacle", "Explain the most complex challenge or roadblock you hit and how you diagnosed it."),
            ("Implementation Strategy", "Walk through the architectural choice, tools, or design patterns you implemented to solve it."),
            ("Quantified Outcome", "Share the performance gains, code reduction, or impact on the timeline to show results.")
        ]
    # Fallback to category key if available, otherwise technical
    else:
        if category_key == "behavioral":
            return [
                ("Context / Problem", "Briefly outline the situation and the task or stakes involved using the STAR methodology."),
                ("Your Personal Action", "Explain the specific decisions, communications, or steps you took (emphasize 'I' rather than 'we')."),
                ("Result & Key Learnings", "Finish with the measurable result and what you learned from the experience for future challenges.")
            ]
        elif category_key == "project_based":
            return [
                ("Situation & Role", "Set the context: introduce the project, the primary technical goal, and your ownership."),
                ("Technical Obstacle", "Explain the most complex challenge or roadblock you hit and how you diagnosed it."),
                ("Implementation Strategy", "Walk through the architectural choice, tools, or design patterns you implemented to solve it."),
                ("Quantified Outcome", "Share the performance gains, code reduction, or impact on the timeline to show results.")
            ]
        elif category_key == "role_specific":
            return [
                ("Clarify Scope & Assumptions", "Begin by highlighting any assumptions you make to narrow down the scenario."),
                ("Structured Deconstruction", "Break down the issue into immediate hotfixes versus long-term strategic solutions."),
                ("Decision Justification", "Weigh the trade-offs of other choices and explain how your solution aligns with business priority or system reliability.")
            ]
        else: # technical
            return [
                ("Core Concept definition", "Clearly define the technology or pattern. Keep it simple and focused on the key problem it solves."),
                ("Real-World application", "Describe a scenario or project where you applied this concept to achieve a practical outcome."),
                ("Trade-offs & limitations", "Discuss why you picked this approach, alternative solutions, and any potential bottlenecks or edge cases.")
            ]

def render_career_roadmap_tab(data, resume_text, candidate_id=None):
    cname = esc(data.get("candidate_name", "Candidate"))
    
    st.markdown('<div class="line"></div>', unsafe_allow_html=True)
    
    # Scoped Stylesheet for Career Roadmap Page
    st.markdown(clean_html("""
    <style>
    .roadmap-stepper {
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 1.5rem 0 2.5rem;
        padding: 0 2rem;
    }
    .stepper-line {
        position: absolute;
        top: 24px;
        left: 4.5rem;
        right: 4.5rem;
        height: 3px;
        background: linear-gradient(90deg, #818cf8 0%, #60a5fa 33%, #34d399 66%, #a78bfa 100%);
        z-index: 1;
        opacity: 0.25;
        border-radius: 4px;
    }
    .step {
        position: relative;
        z-index: 2;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    .step-circle {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: #0b1329;
        border: 3px solid var(--step-color);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-weight: 800;
        font-size: 1rem;
        font-family: 'Outfit', sans-serif;
        box-shadow: 0 0 15px rgba(15, 23, 42, 0.6), inset 0 0 10px var(--step-color);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .step:hover .step-circle {
        transform: scale(1.15);
        box-shadow: 0 0 25px var(--step-color), inset 0 0 10px rgba(255,255,255,0.2);
        background: var(--step-color);
        color: #030712;
    }
    .step-label {
        margin-top: 0.6rem;
        font-size: 0.75rem;
        font-weight: 800;
        color: #e2e8f0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: color 0.3s ease;
    }
    .step:hover .step-label {
        color: var(--step-color);
    }
    .step-sublabel {
        font-size: 0.65rem;
        color: #94a3b8;
        margin-top: 0.1rem;
        font-weight: 500;
    }

    .roadmap-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.25rem;
        align-items: stretch;
    }
    
    .roadmap-grid-3 {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.25rem;
        align-items: stretch;
    }

    .phase-card {
        background: rgba(15, 23, 42, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-top: 4px solid var(--phase-color) !important;
        border-radius: 16px;
        padding: 1.5rem 1.3rem;
        display: flex;
        flex-direction: column;
        height: 100%;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
    }
    .phase-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(180deg, var(--phase-color)03, transparent 50%);
        opacity: 0;
        transition: opacity 0.4s ease;
        pointer-events: none;
    }
    .phase-card:hover {
        transform: translateY(-8px);
        border-color: var(--phase-color)40;
        box-shadow: 0 20px 40px rgba(0,0,0,0.35), 0 0 20px var(--phase-color)15;
    }
    .phase-card:hover::before {
        opacity: 1;
    }

    .job-card-premium {
        background: rgba(15, 23, 42, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 1.4rem;
        margin-bottom: 0.6rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }
    .job-card-premium:hover {
        border-color: rgba(255, 255, 255, 0.1);
        box-shadow: 0 12px 30px rgba(0,0,0,0.25);
        background: rgba(15, 23, 42, 0.45);
    }

    .scenario-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 1.25rem;
        justify-content: flex-start;
        align-items: stretch;
    }

    .scenario-card {
        flex: 1 1 320px;
        max-width: 420px;
        background: rgba(15, 23, 42, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 1.5rem 1.4rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
    }
    .scenario-card:hover {
        border-color: rgba(167, 139, 250, 0.3);
        box-shadow: 0 12px 30px rgba(167, 139, 250, 0.08);
        transform: translateY(-4px);
    }

    .skill-gap-card {
        background: rgba(15, 23, 42, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 1.3rem;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }
    .skill-gap-card:hover {
        border-color: rgba(255, 255, 255, 0.1);
        background: rgba(15, 23, 42, 0.45);
    }

    .company-fit-row {
        display: flex;
        align-items: center;
        gap: 1.25rem;
        background: rgba(15, 23, 42, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 0.8rem;
        transition: all 0.3s ease;
    }
    .company-fit-row:hover {
        border-color: var(--row-color)30;
        box-shadow: 0 4px 15px var(--row-color)08;
        background: rgba(15, 23, 42, 0.45);
    }

    .prep-question-accordion {
        background: rgba(15, 23, 42, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        margin-bottom: 0.75rem;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .prep-question-accordion:hover {
        border-color: var(--accent-color)35;
        background: rgba(15, 23, 42, 0.35);
        box-shadow: 0 8px 25px var(--accent-color)08;
        transform: translateY(-2px);
    }
    .prep-question-summary {
        padding: 1.1rem 1.3rem;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        list-style: none;
        user-select: none;
    }
    .prep-question-summary::-webkit-details-marker {
        display: none;
    }
    .prep-question-header {
        display: flex;
        gap: 0.9rem;
        align-items: center;
        flex: 1;
        margin-right: 1rem;
    }
    .prep-question-badge {
        background: var(--accent-color)15;
        color: var(--accent-color);
        font-family: 'Outfit', sans-serif;
        font-size: 0.7rem;
        font-weight: 800;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        border: 1px solid var(--accent-color)25;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        flex-shrink: 0;
    }
    .prep-question-text {
        font-size: 0.9rem;
        color: #f1f5f9;
        font-weight: 600;
        line-height: 1.45;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .prep-question-icon {
        color: rgba(255, 255, 255, 0.3);
        font-size: 0.8rem;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        flex-shrink: 0;
    }
    .prep-question-accordion[open] .prep-question-icon {
        transform: rotate(180deg);
        color: var(--accent-color);
    }
    .prep-question-accordion[open] {
        border-color: var(--accent-color)40;
        background: rgba(15, 23, 42, 0.45);
        box-shadow: 0 10px 30px var(--accent-color)12;
    }
    .prep-question-content {
        padding: 0rem 1.3rem 1.2rem 1.3rem;
        border-top: 1px solid rgba(255, 255, 255, 0.03);
        background: rgba(3, 7, 18, 0.2);
    }
    .prep-question-accordion[open] .prep-question-content {
        animation: slideDown 0.3s ease-out;
    }
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-8px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .prep-strategy-title {
        font-size: 0.72rem;
        text-transform: uppercase;
        color: #94a3b8;
        letter-spacing: 1px;
        font-weight: 700;
        margin-top: 0.9rem;
        margin-bottom: 0.7rem;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }
    .strategy-step-container {
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
        margin: 0.2rem 0;
    }
    .strategy-step {
        display: flex;
        gap: 0.9rem;
        align-items: flex-start;
        background: rgba(255, 255, 255, 0.015);
        border: 1px solid rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        padding: 0.75rem 0.9rem;
        transition: all 0.25s ease;
    }
    .strategy-step:hover {
        background: rgba(255, 255, 255, 0.03);
        border-color: var(--accent-color)25;
        transform: translateX(4px);
    }
    .strategy-step-num {
        background: var(--accent-color)12;
        color: var(--accent-color);
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.72rem;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
        border: 1px solid var(--accent-color)20;
        flex-shrink: 0;
        box-shadow: 0 0 6px var(--accent-color)10;
        margin-top: 0.1rem;
    }
    .strategy-step-body {
        flex: 1;
    }
    .strategy-step-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.8rem;
        font-weight: 700;
        color: #fafafa;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.15rem;
    }
    .strategy-step-desc {
        font-size: 0.8rem;
        color: #94a3b8;
        line-height: 1.45;
        font-weight: 500;
    }

    @media (max-width: 1024px) {
        .roadmap-grid, .roadmap-grid-3 {
            grid-template-columns: repeat(2, 1fr) !important;
        }
        .stepper-line {
            display: none !important;
        }
        .roadmap-stepper {
            flex-direction: column !important;
            gap: 1.5rem !important;
            padding: 0 !important;
        }
    }
    @media (max-width: 640px) {
        .roadmap-grid, .roadmap-grid-3 {
            grid-template-columns: 1fr !important;
        }
    }
    </style>
    """), unsafe_allow_html=True)

    st.markdown(clean_html(f"""
    <div class="res-header" style="text-align: center; margin-bottom: 2rem; margin-top: 0.5rem;">
        <div style="font-size: 0.72rem; color: #a78bfa; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; margin-bottom: 0.35rem;">Career Intelligence Hub</div>
        <div style="font-size: 2.2rem; font-weight: 900; background: linear-gradient(90deg, #ffffff 0%, #cbd5e1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-family: 'Outfit', sans-serif; letter-spacing: -0.5px;">Career Path Roadmap</div>
    </div>
    """), unsafe_allow_html=True)

    # ─── 1. OVERVIEW: YOUR INTERVIEW CHANCES ──────────────────────────────────
    hp = data.get("hiring_probability", {})
    hp_ats = hp.get("ats_pass", "Low")
    hp_sl = hp.get("recruiter_shortlist", "Low")
    hp_int = hp.get("interview_call", "Low")
    hp_hp = hp.get("hiring_potential", "Low")
    hp_reason = hp.get("reasoning", "Not available")
    
    def custom_p_badge(val):
        v_lower = val.lower() if val else ""
        if "high" in v_lower:
            return '<span style="background: rgba(52, 211, 153, 0.08); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.25); border-radius: 20px; padding: 0.25rem 0.75rem; font-size: 0.74rem; font-weight: 700; display: inline-block; text-shadow: 0 0 8px rgba(52, 211, 153, 0.15);">High</span>'
        if "mod" in v_lower:
            return '<span style="background: rgba(96, 165, 250, 0.08); color: #60a5fa; border: 1px solid rgba(96, 165, 250, 0.25); border-radius: 20px; padding: 0.25rem 0.75rem; font-size: 0.74rem; font-weight: 700; display: inline-block; text-shadow: 0 0 8px rgba(96, 165, 250, 0.15);">Moderate</span>'
        return '<span style="background: rgba(248, 113, 113, 0.08); color: #f87171; border: 1px solid rgba(248, 113, 113, 0.25); border-radius: 20px; padding: 0.25rem 0.75rem; font-size: 0.74rem; font-weight: 700; display: inline-block; text-shadow: 0 0 8px rgba(248, 113, 113, 0.15);">Low</span>'

    custom_hp_card = f"""
    <div class="card" style="position: relative; overflow: hidden; background: linear-gradient(180deg, rgba(249, 115, 22, 0.03) 0%, rgba(15, 23, 42, 0.45) 100%); padding: 1.6rem 1.8rem; border: 1px solid rgba(255,255,255,0.06); box-shadow: 0 10px 30px rgba(0,0,0,0.25);">
        <!-- Flawless Rounded Accent Bar on Left -->
        <div style="position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: #f97316;"></div>
        
        <div style="font-size:0.75rem; color:#f97316; font-weight:800; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:1.4rem; display:flex; align-items:center; gap:0.5rem; font-family: 'Outfit', sans-serif;">📈 Your Interview Chances</div>
        
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; margin-bottom: 1.4rem;">
            <!-- ATS Pass Rate -->
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 1.1rem 0.8rem; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
                <div style="font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; font-weight:700; margin-bottom: 0.6rem;">ATS Pass Rate</div>
                <div>{custom_p_badge(hp_ats)}</div>
            </div>
            <!-- Recruiter Shortlist -->
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 1.1rem 0.8rem; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
                <div style="font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; font-weight:700; margin-bottom: 0.6rem;">Recruiter Shortlist</div>
                <div>{custom_p_badge(hp_sl)}</div>
            </div>
            <!-- Interview Call -->
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 1.1rem 0.8rem; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
                <div style="font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; font-weight:700; margin-bottom: 0.6rem;">Interview Call</div>
                <div>{custom_p_badge(hp_int)}</div>
            </div>
            <!-- Hiring Potential -->
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 1.1rem 0.8rem; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
                <div style="font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; font-weight:700; margin-bottom: 0.6rem;">Hiring Potential</div>
                <div>{custom_p_badge(hp_hp)}</div>
            </div>
        </div>
        
        <!-- Recruiter Rationale Section -->
        <div style="border-top: 1px solid rgba(255, 255, 255, 0.06); padding-top: 1.2rem; margin-top: 1.2rem; display: flex; gap: 0.8rem; align-items: flex-start;">
            <div style="background: rgba(249, 115, 22, 0.1); border: 1px solid rgba(249, 115, 22, 0.2); border-radius: 8px; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 1.15rem; flex-shrink: 0; color: #f97316;">
                📝
            </div>
            <div style="font-size: 0.86rem; color: #cbd5e1; line-height: 1.6;">
                <span style="font-weight: 800; color: #f97316; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 0.2rem;">Recruiter Rationale</span>
                {esc(hp_reason)}
            </div>
        </div>
    </div>
    """
    st.markdown(clean_html(custom_hp_card), unsafe_allow_html=True)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # ─── 2. CORE: Personalized Upskilling Roadmap ───────────────────────────────
    roadmap = data.get("roadmap", {})
    
    if roadmap and "days_0_3_months" in roadmap:
        phases = [
            ("days_0_3_months", "0 - 3 Months", "Foundation", "#818cf8"),
            ("days_3_6_months", "3 - 6 Months", "Development", "#60a5fa"),
            ("days_6_12_months", "6 - 12 Months", "Placement", "#34d399"),
            ("days_12_24_months", "12 - 24 Months", "Long-term", "#a78bfa")
        ]
        
        cards_html = ""
        for key, label, title, color in phases:
            phase_data = roadmap.get(key, {})
            focus = esc(phase_data.get("focus", "Not available"))
            skills_chips = "".join([f'<span style="background:{color}12; color:{color}; font-size:0.65rem; font-weight:700; padding:0.18rem 0.5rem; border-radius:6px; margin:0 0.25rem 0.25rem 0; display:inline-block; border:1px solid {color}22;">{esc(sk)}</span>' for sk in phase_data.get("skills", [])])
            if not skills_chips:
                skills_chips = '<span style="font-size:0.7rem; color:#52525b; font-style:italic;">None</span>'
            
            roles_list_html = "".join([f'<div style="display:flex; align-items:center; gap:0.45rem; font-size:0.75rem; color:#e4e4e7; margin-bottom:0.25rem;"><span style="color:{color}; font-size:0.6rem;">●</span><span>{esc(role)}</span></div>' for role in phase_data.get("roles_to_explore", [])[:2]])
            if not roles_list_html:
                roles_list_html = '<div style="font-size:0.72rem; color:#71717a; font-style:italic;">None</div>'
                
            actions = phase_data.get("actions", [])
            actions_list_html = "".join([f'<div style="display:flex; align-items:flex-start; gap:0.45rem; font-size:0.74rem; color:#d4d4d8; line-height:1.45; margin-bottom:0.35rem;"><span style="color:#34d399; font-size:0.8rem; font-weight:700; line-height:1;">✓</span><span>{esc(act)}</span></div>' for act in actions[:3]])
            if not actions_list_html:
                actions_list_html = '<div style="font-size:0.72rem; color:#71717a; font-style:italic;">None</div>'
            
            cards_html += f"""
            <div class="phase-card" style="--phase-color: {color};">
                <!-- Timeline Pill Badge -->
                <div style="margin-bottom: 0.6rem;">
                    <span style="background: {color}15; color: {color}; font-size: 0.62rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; padding: 0.2rem 0.6rem; border-radius: 20px; border: 1px solid {color}25; display: inline-block;">{label}</span>
                </div>
                <!-- Title -->
                <div style="font-weight: 800; color: #ffffff; font-size: 1.05rem; margin-bottom: 0.55rem; font-family: 'Outfit', sans-serif; letter-spacing: -0.2px;">{title}</div>
                <!-- Focus -->
                <div style="font-size: 0.78rem; color: #cbd5e1; line-height: 1.55; margin-bottom: 0.95rem; font-style: italic; opacity: 0.95;">"{focus}"</div>
                
                <!-- Key Skills -->
                <div style="margin-bottom: 0.95rem;">
                    <span style="font-size:0.6rem; color:#64748b; font-weight:800; text-transform:uppercase; display:block; margin-bottom:0.4rem; letter-spacing:0.5px;">🔑 Key Skills</span>
                    <div style="display:flex; flex-wrap:wrap;">{skills_chips}</div>
                </div>
                
                <!-- Target Roles -->
                <div style="margin-bottom: 1.1rem;">
                    <span style="font-size:0.6rem; color:#64748b; font-weight:800; text-transform:uppercase; display:block; margin-bottom:0.4rem; letter-spacing:0.5px;">🎯 Target Roles</span>
                    <div>{roles_list_html}</div>
                </div>
                
                <!-- Milestone Actions -->
                <div style="border-top: 1px dashed rgba(255,255,255,0.08); padding-top: 0.95rem; margin-top: auto;">
                    <span style="font-size:0.6rem; color:#34d399; font-weight:800; text-transform:uppercase; display:block; margin-bottom:0.45rem; letter-spacing:0.5px;">🏆 Milestone Actions</span>
                    <div>{actions_list_html}</div>
                </div>
            </div>
            """
            
        custom_roadmap_card = f"""
        <div class="card" style="position: relative; overflow: hidden; background: linear-gradient(180deg, rgba(59, 130, 246, 0.03) 0%, rgba(15, 23, 42, 0.45) 100%); padding: 1.8rem; border: 1px solid rgba(255,255,255,0.06); box-shadow: 0 10px 30px rgba(0,0,0,0.25);">
            <!-- Flawless Rounded Accent Bar on Left -->
            <div style="position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: #3b82f6;"></div>
            
            <div style="font-size:0.75rem; color:#3b82f6; font-weight:800; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:1.4rem; display:flex; align-items:center; gap:0.5rem; font-family: 'Outfit', sans-serif;">🚀 Personalized Upskilling Roadmap</div>
            
            <div class="roadmap-grid">
                {cards_html}
            </div>
        </div>
        """
        st.markdown(clean_html(custom_roadmap_card), unsafe_allow_html=True)
        
    else:
        legacy_roadmap = data.get("career_roadmap", {})
        rm30 = legacy_roadmap.get("days_30", "Not available")
        rm60 = legacy_roadmap.get("days_60", "Not available")
        rm90 = legacy_roadmap.get("days_90", "Not available")
        
        cards_html = f"""
        <div class="phase-card" style="--phase-color: #818cf8;">
            <div style="margin-bottom: 0.5rem;">
                <span style="background: rgba(129, 140, 248, 0.15); color: #818cf8; font-size: 0.62rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; padding: 0.2rem 0.6rem; border-radius: 20px; border: 1px solid rgba(129, 140, 248, 0.25); display: inline-block;">📅 30 Days</span>
            </div>
            <div style="font-weight: 800; color: #ffffff; font-size: 1.05rem; margin-bottom: 0.55rem; font-family: 'Outfit', sans-serif; letter-spacing: -0.2px;">Foundation</div>
            <div style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.6; opacity: 0.95;">{esc(rm30)}</div>
        </div>
        <div class="phase-card" style="--phase-color: #60a5fa;">
            <div style="margin-bottom: 0.5rem;">
                <span style="background: rgba(96, 165, 250, 0.15); color: #60a5fa; font-size: 0.62rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; padding: 0.2rem 0.6rem; border-radius: 20px; border: 1px solid rgba(96, 165, 250, 0.25); display: inline-block;">📅 60 Days</span>
            </div>
            <div style="font-weight: 800; color: #ffffff; font-size: 1.05rem; margin-bottom: 0.55rem; font-family: 'Outfit', sans-serif; letter-spacing: -0.2px;">Development</div>
            <div style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.6; opacity: 0.95;">{esc(rm60)}</div>
        </div>
        <div class="phase-card" style="--phase-color: #34d399;">
            <div style="margin-bottom: 0.5rem;">
                <span style="background: rgba(52, 211, 153, 0.15); color: #34d399; font-size: 0.62rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; padding: 0.2rem 0.6rem; border-radius: 20px; border: 1px solid rgba(52, 211, 153, 0.25); display: inline-block;">📅 90 Days</span>
            </div>
            <div style="font-weight: 800; color: #ffffff; font-size: 1.05rem; margin-bottom: 0.55rem; font-family: 'Outfit', sans-serif; letter-spacing: -0.2px;">Placement</div>
            <div style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.6; opacity: 0.95;">{esc(rm90)}</div>
        </div>
        """
        
        custom_roadmap_card = f"""
        <div class="card" style="position: relative; overflow: hidden; background: linear-gradient(180deg, rgba(59, 130, 246, 0.03) 0%, rgba(15, 23, 42, 0.45) 100%); padding: 1.8rem; border: 1px solid rgba(255,255,255,0.06); box-shadow: 0 10px 30px rgba(0,0,0,0.25);">
            <!-- Flawless Rounded Accent Bar on Left -->
            <div style="position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: #3b82f6;"></div>
            
            <div style="font-size:0.75rem; color:#3b82f6; font-weight:800; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:1.4rem; display:flex; align-items:center; gap:0.5rem; font-family: 'Outfit', sans-serif;">🚀 Personalized Upskilling Roadmap</div>
            
            <div class="roadmap-grid-3">
                {cards_html}
            </div>
        </div>
        """
        st.markdown(clean_html(custom_roadmap_card), unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    st.markdown(clean_html("""<div class="card-head" style="margin-bottom: 0.8rem;">
        <div class="icon-box purple">💼</div>
        <h3 style="margin:0;">Interactive Career Intelligence Deep-Dives</h3>
    </div>"""), unsafe_allow_html=True)

    # Sub-tabs for Career Intelligence
    car_tab1, car_tab5 = st.tabs([
        "Matched Jobs",
        "Interview Prep Questions"
    ])

    # Get resume skills
    sk_list = data.get("parsed_data", {}).get("skills", [])
    resume_skills_lower = [s.lower().strip() for s in sk_list] if sk_list else []
    
    if not resume_skills_lower:
        resume_skills_lower = [s.lower().strip() for s in data.get("profile_summary", {}).get("skills_identified", [])]
    if not resume_skills_lower and resume_text:
        resume_text_lower = resume_text.lower()
        jobs_database = [
            {"title": "AI/ML Intern", "company": "OpenAI", "logo": "🤖", "salary": "$45 - $60 / hr", "location": "SF, CA (Hybrid)", "skills": ["Python", "PyTorch", "Transformers", "Deep Learning", "NLP", "Machine Learning", "Git"]},
            {"title": "Software Engineer", "company": "Google", "logo": "🔍", "salary": "$125,000 - $165,000 / yr", "location": "MV, CA (Hybrid)", "skills": ["Java", "C++", "Python", "Data Structures", "Algorithms", "Distributed Systems", "SQL", "Git"]},
            {"title": "Data Analyst", "company": "Microsoft", "logo": "💻", "salary": "$95,000 - $120,000 / yr", "location": "Redmond, WA (Remote)", "skills": ["SQL", "Power BI", "Excel", "Python", "Statistics", "Pandas", "Data Visualization"]},
            {"title": "Data Scientist", "company": "Netflix", "logo": "🍿", "salary": "$140,000 - $190,000 / yr", "location": "Los Gatos, CA (Hybrid)", "skills": ["Python", "SQL", "R", "Machine Learning", "A/B Testing", "Spark", "Statistics"]},
            {"title": "Full Stack Engineer", "company": "Stripe", "logo": "💳", "salary": "$130,000 - $175,000 / yr", "location": "SF, CA (Hybrid)", "skills": ["React", "TypeScript", "Node.js", "Ruby on Rails", "API Design", "SQL", "Git", "HTML", "CSS"]},
            {"title": "DevOps Engineer", "company": "AWS", "logo": "☁️", "salary": "$120,000 - $160,000 / yr", "location": "Seattle, WA (Remote)", "skills": ["Docker", "Kubernetes", "AWS", "Terraform", "CI/CD", "Linux", "Python", "Bash"]},
            {"title": "Frontend Developer", "company": "Meta", "logo": "📱", "salary": "$115,000 - $155,000 / yr", "location": "Menlo Park, CA (Hybrid)", "skills": ["React", "JavaScript", "HTML", "CSS", "TypeScript", "GraphQL", "Git"]}
        ]
        for j in jobs_database:
            for s in j["skills"]:
                if s.lower() in resume_text_lower:
                    resume_skills_lower.append(s.lower())
        resume_skills_lower = list(set(resume_skills_lower))

    jobs_database = [
        {"title": "AI/ML Intern", "company": "OpenAI", "logo": "🤖", "salary": "$45 - $60 / hr", "location": "San Francisco, CA (Hybrid)", "skills": ["Python", "PyTorch", "Transformers", "Deep Learning", "NLP", "Machine Learning", "Git"]},
        {"title": "Software Engineer", "company": "Google", "logo": "🔍", "salary": "$125,000 - $165,000 / yr", "location": "Mountain View, CA (Hybrid)", "skills": ["Java", "C++", "Python", "Data Structures", "Algorithms", "Distributed Systems", "SQL", "Git"]},
        {"title": "Data Analyst", "company": "Microsoft", "logo": "💻", "salary": "$95,000 - $120,000 / yr", "location": "Redmond, WA (Remote)", "skills": ["SQL", "Power BI", "Excel", "Python", "Statistics", "Pandas", "Data Visualization"]},
        {"title": "Data Scientist", "company": "Netflix", "logo": "🍿", "salary": "$140,000 - $190,000 / yr", "location": "Los Gatos, CA (Hybrid)", "skills": ["Python", "SQL", "R", "Machine Learning", "A/B Testing", "Spark", "Statistics"]},
        {"title": "Full Stack Engineer", "company": "Stripe", "logo": "💳", "salary": "$130,000 - $175,000 / yr", "location": "San Francisco, CA (Hybrid)", "skills": ["React", "TypeScript", "Node.js", "Ruby on Rails", "API Design", "SQL", "Git", "HTML", "CSS"]},
        {"title": "DevOps Engineer", "company": "AWS", "logo": "☁️", "salary": "$120,000 - $160,000 / yr", "location": "Seattle, WA (Remote)", "skills": ["Docker", "Kubernetes", "AWS", "Terraform", "CI/CD", "Linux", "Python", "Bash"]},
        {"title": "Frontend Developer", "company": "Meta", "logo": "📱", "salary": "$115,000 - $155,000 / yr", "location": "Menlo Park, CA (Hybrid)", "skills": ["React", "JavaScript", "HTML", "CSS", "TypeScript", "GraphQL", "Git"]}
    ]

    matched_jobs = []
    for job in jobs_database:
        job_skills = job["skills"]
        matched = [s for s in job_skills if s.lower() in resume_skills_lower]
        missing = [s for s in job_skills if s.lower() not in resume_skills_lower]
        match_pct = int(round(len(matched) / len(job_skills) * 100)) if job_skills else 0
        if match_pct > 0:
            match_pct = min(100, match_pct + 10)
        
        matched_jobs.append({
            **job,
            "match_pct": match_pct,
            "matched_skills": matched,
            "missing_skills": missing
        })
    matched_jobs = sorted(matched_jobs, key=lambda x: x["match_pct"], reverse=True)

    # ─── TAB 1: MATCHED JOBS ─────────────────────────────────────────
    with car_tab1:

        j_cols = st.columns(2, gap="medium")
        for idx, j in enumerate(matched_jobs[:4]):
            j_title = esc(j["title"])
            j_comp = esc(j["company"])
            j_logo = esc(j["logo"])
            j_sal = esc(j["salary"])
            j_loc = esc(j["location"])
            j_pct = j["match_pct"]
            
            pct_color = "#34d399" if j_pct >= 75 else "#60a5fa" if j_pct >= 50 else "#fb923c"
            matched_chips = "".join([f'<span class="t t-green" style="font-size:0.7rem; margin-right:0.25rem; margin-bottom:0.3rem; display:inline-block; border-radius:4px; padding:0.15rem 0.4rem;">✓ {esc(s)}</span>' for s in j["matched_skills"]])
            missing_chips = "".join([f'<span class="t t-red" style="font-size:0.7rem; margin-right:0.25rem; margin-bottom:0.3rem; display:inline-block; border-radius:4px; padding:0.15rem 0.4rem;">✗ {esc(s)}</span>' for s in j["missing_skills"]])
            
            col_idx = idx % 2
            with j_cols[col_idx]:
                st.markdown(clean_html(f"""
                <div class="job-card-premium">
                    <!-- Glow Indicator Strip on Left -->
                    <div style="position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: {pct_color};"></div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem; flex-wrap: wrap; gap: 0.5rem;">
                        <div>
                            <span style="font-size:1.35rem; margin-right:0.4rem; vertical-align:middle;">{j_logo}</span>
                            <strong style="font-size:1.05rem; color:#fafafa; vertical-align:middle; font-family:'Outfit';">{j_title}</strong>
                            <span style="font-size:0.82rem; color:#94a3b8; margin-left:0.4rem; vertical-align:middle;">at {j_comp}</span>
                        </div>
                        <span style="background: {pct_color}15; color: {pct_color}; font-size: 0.72rem; font-weight: 800; padding: 0.2rem 0.5rem; border-radius: 20px; border: 1px solid {pct_color}30;">{j_pct}% Match</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 0.8rem; display: flex; gap: 0.8rem; align-items: center;">
                        <span>📍 {j_loc}</span>
                        <span style="opacity: 0.3;">|</span>
                        <span>💵 {j_sal}</span>
                    </div>
                    <div style="margin-bottom:0.5rem;">
                        <span style="font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; display: block; margin-bottom: 0.2rem; letter-spacing: 0.5px;">Matched Skills ({len(j["matched_skills"])})</span>
                        <div class="tag-wrap">{matched_chips if matched_chips else '<span style="font-size:0.72rem; color:#475569; font-style:italic;">None</span>'}</div>
                    </div>
                    <div>
                        <span style="font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; display: block; margin-bottom: 0.2rem; letter-spacing: 0.5px;">Missing Skills ({len(j["missing_skills"])})</span>
                        <div class="tag-wrap">{missing_chips if missing_chips else '<span style="font-size:0.72rem; color:#475569; font-style:italic;">None</span>'}</div>
                    </div>
                </div>
                """), unsafe_allow_html=True)
                if st.button("Apply Now", key=f"apply_job_{idx}_{j_comp.replace(' ', '_')}", use_container_width=True, type="primary"):
                    st.toast(f"🎉 Application submitted successfully to {j_comp} for {j_title}!")

    # ─── TAB 5: INTERVIEW PREP QUESTIONS ──────────────────────────────────
    with car_tab5:
        questions = data.get("interview_questions", {})
        if not isinstance(questions, dict):
            q_list = questions if isinstance(questions, list) else []
            questions = {"technical": q_list, "project_based": [], "behavioral": [], "role_specific": []}
            

        q_cats = [
            ("Technical Assessment", questions.get("technical", []), "#60a5fa", "💻", "technical"),
            ("Project-Based Deep-Dive", questions.get("project_based", []), "#4ade80", "🚀", "project_based"),
            ("Behavioral Alignment", questions.get("behavioral", []), "#fb923c", "🤝", "behavioral"),
            ("Role-Specific Scenario", questions.get("role_specific", []), "#a78bfa", "🎯", "role_specific")
        ]
        
        has_questions = False
        for label, q_list, color, emoji, cat_key in q_cats:
            if q_list:
                has_questions = True
                st.markdown(clean_html(f"""
                <div style="margin-top: 1.2rem; margin-bottom: 0.6rem; display: flex; align-items: center; gap: 0.4rem;">
                    <span style="font-size: 1rem;">{emoji}</span>
                    <span style="font-size:0.75rem; color:{color}; text-transform:uppercase; letter-spacing:1.2px; font-weight:800; font-family:'Outfit';">{label}</span>
                </div>
                """), unsafe_allow_html=True)
                for i, q in enumerate(q_list):
                    strategy_points = get_strategy_for_question(q, cat_key)
                    strategy_html = ""
                    if strategy_points:
                        steps_html = ""
                        for s_idx, (title, desc) in enumerate(strategy_points):
                            steps_html += f"""
                            <div class="strategy-step">
                                <div class="strategy-step-num">{s_idx + 1:02d}</div>
                                <div class="strategy-step-body">
                                    <div class="strategy-step-title">{esc(title)}</div>
                                    <div class="strategy-step-desc">{esc(desc)}</div>
                                </div>
                            </div>
                            """
                        strategy_html = f"""
                        <div class="prep-question-content">
                            <div class="prep-strategy-title">
                                <span>💡</span> Response Strategy Blueprint
                            </div>
                            <div class="strategy-step-container">
                                {steps_html}
                            </div>
                        </div>
                        """
                    st.markdown(clean_html(f"""
                    <details class="prep-question-accordion" style="--accent-color: {color};">
                        <summary class="prep-question-summary">
                            <div class="prep-question-header">
                                <span class="prep-question-badge">Q{i+1}</span>
                                <span class="prep-question-text">{esc(q)}</span>
                            </div>
                            <span class="prep-question-icon">▼</span>
                        </summary>
                        {strategy_html}
                    </details>
                    """), unsafe_allow_html=True)
        if not has_questions:
            st.info("No interview prep questions generated for this profile.")
