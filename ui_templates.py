import streamlit as st
from report_generator import esc

# ─────────────────────────────────────────────────────────────
# ATS RESUME TEMPLATES DATA
# ─────────────────────────────────────────────────────────────

TEMPLATES = {
    "Fresh Graduate": {
        "description": "Optimized for recent graduates with limited work experience. Places heavy emphasis on education, relevant coursework, academic projects, leadership activities, and certifications.",
        "icon": "🎓",
        "color": "#818cf8",
        "tips": [
            "**Education First**: Place your Education section at the top of the resume, including your degree, GPA (if 8.0+ or 3.5+), and expected graduation date.",
            "**Academic Projects**: Treat major projects like work experience. Use action verbs and detail the tools and methodologies used.",
            "**Coursework Relevance**: List 4-6 courses that directly relate to the job description to match automatic keyword screening.",
            "**Leadership/Extracurriculars**: Highlight student clubs, volunteer roles, or hackathons to demonstrate soft skills and drive."
        ],
        "content": """# [YOUR FULL NAME]
[City, State, Zip Code] | [Your Phone Number] | [Your Email Address]
[GitHub Profile Link] | [LinkedIn Profile Link] | [Personal Portfolio Website]

## EDUCATION
**[University/College Name]** — [City, State]
[Degree Name, e.g., B.Tech in Computer Science & Engineering] | GPA: [X.X/10.0 or Y.Y/4.0]
*Graduation Date: [Month, Year]*
* **Relevant Coursework:** [Data Structures & Algorithms, Database Management, Operating Systems, Machine Learning]
* **Honors/Awards:** [List top 1-2 honors, Dean's List, or academic scholarships]

## TECHNICAL SKILLS
* **Programming Languages:** [Python, SQL, Java, C++, JavaScript]
* **Frameworks & Tools:** [Git, PyTorch, React, Flask, Docker]
* **Databases & Cloud:** [MySQL, PostgreSQL, Google Cloud Platform (GCP)]
* **Core Competencies:** [Data Structures, Object-Oriented Programming, Problem Solving]

## TECHNICAL PROJECTS
### [Project Title / GitHub Link] — [Month, Year – Month, Year]
* **Technologies Used:** [Python, PyTorch, FastAPI, Git]
* Developed a [Brief Project Description] that [Action taken, e.g., predicted stock prices using LSTM networks].
* Achieved [Quantitative metric, e.g., 94% accuracy rate] by implementing [specific optimization or algorithm].
* Structured clean database pipelines using [e.g., PostgreSQL] to handle [e.g., 50,000+ test records].

### [Second Project Title / GitHub Link] — [Month, Year – Month, Year]
* **Technologies Used:** [React, Node.js, Express, MongoDB]
* Built a responsive [Brief Project Description] featuring [specific functionality, e.g., real-time chat with WebSockets].
* Optimized frontend loading speeds by [e.g., 25%] through [specific technique, e.g., image compression and lazy loading].
* Integrated secure [e.g., JWT user authentication] to handle secure endpoint routing.

## EXPERIENCE
**[Company/Organization Name]** — [City, State]
*Role: Software Engineering Intern* | *[Month, Year – Month, Year]*
* Collaborated with a team of [number] engineers to build and deploy [specific application feature].
* Wrote unit and integration tests using [specific framework, e.g., PyTest], increasing test coverage by [e.g., 15%].
* Fixed [number] high-priority bugs in the core [React/Python] codebase, improving daily application uptime.

## CERTIFICATIONS & ACHIEVEMENTS
* **[Name of Certification, e.g., AWS Cloud Practitioner]** — [Issuer Name, Year]
* **[Name of Certification, e.g., Google Data Analytics Certificate]** — [Issuer Name, Year]
* **[Name of Achievement, e.g., Hackathon 2nd Place Winner]** — [Event Name, Year]
"""
    },
    "Tech-Focused": {
        "description": "Optimized for core software engineering, data science, and IT roles. Prioritizes a highly visible, categorized technical skill grid, Git links, and framework proficiencies at the top.",
        "icon": "💻",
        "color": "#60a5fa",
        "tips": [
            "**Categorized Skill Grid**: Group your skills by domain (e.g., Languages, Libraries, Cloud/DevOps, Databases) to make parsing trivial for the ATS.",
            "**Action-Oriented Experience**: Focus on engineering-driven metrics (e.g., reduced API latency, optimized database queries, automated deployments).",
            "**Clean Formatting**: Avoid multi-column layouts, graphics, tables, or progress bars which corrupt standard ATS parsers."
        ],
        "content": """# [YOUR FULL NAME]
[City, State, Zip Code] | [Your Phone Number] | [Your Email Address]
[GitHub Profile Link] | [LinkedIn Profile Link] | [Personal Portfolio Website]

## TECHNICAL SKILLS
* **Languages:** [Python, Go, SQL, C++, TypeScript, Bash]
* **Frameworks & Libraries:** [Django, FastAPI, PyTorch, PySpark, NumPy, Pandas, React]
* **Cloud & DevOps:** [Docker, Kubernetes, AWS, Terraform, CI/CD Pipelines, Linux]
* **Databases & Cache:** [PostgreSQL, MongoDB, Redis, Elasticsearch]

## PROFESSIONAL EXPERIENCE
**[Company Name]** — [City, State]
*Role: Software Engineer* | *[Month, Year – Present]*
* Engineered a scalable RESTful microservice API using [FastAPI and PostgreSQL] that processed [e.g., 10M+ daily requests].
* Reduced system latency by [e.g., 35%] by implementing [Redis caching] and optimizing database index strategies.
* Automated CI/CD deployment pipelines using [GitHub Actions and Docker], cutting delivery time from [e.g., 2 hours to 10 minutes].
* Mentored [number] junior developers in writing clean, structured, and modular Python code.

**[Second Company Name]** — [City, State]
*Role: Associate Engineer* | *[Month, Year – Month, Year]*
* Developed [number] reusable UI components using [React and TypeScript] for the core user dashboard.
* Migrated a legacy system to [AWS cloud infrastructure], reducing infrastructure overhead cost by [e.g., 20%].
* Collaborated with product designers to resolve [number] critical application issues ahead of product release.

## TECHNICAL PROJECTS
### [Project Title / GitHub Link] — [Month, Year – Month, Year]
* **Technologies Used:** [Go, Docker, Redis, PostgreSQL]
* Developed a high-performance [Brief Project Description] utilizing [specific architectural pattern].
* Handled [e.g., 5,000 concurrent WebSocket connections] with minimal resource usage.
* Implemented clean architecture principles, ensuring high modularity and [e.g., 90% unit test coverage].

## EDUCATION
**[University Name]** — [City, State]
[Degree Name, e.g., Bachelor of Engineering in Information Technology]
*Graduation Date: [Month, Year]*
"""
    },
    "Project-Based": {
        "description": "Ideal for students, bootcamp graduates, or developers whose strongest assets are personal/open-source projects. Features deep-dives into project scope and architectural decisions.",
        "icon": "🛠️",
        "color": "#34d399",
        "tips": [
            "**Use Google X-Y-Z Formula**: Write project points as 'Accomplished [X] as measured by [Y], by doing [Z]'.",
            "**Architectural Decisions**: Mention why you chose specific tools (e.g., 'chose MongoDB for flexible document schema').",
            "**Links to Repositories**: Provide working links to GitHub repositories or live deployments so hiring managers can verify your code."
        ],
        "content": """# [YOUR FULL NAME]
[City, State, Zip Code] | [Your Phone Number] | [Your Email Address]
[GitHub Profile Link] | [LinkedIn Profile Link] | [Personal Portfolio Website]

## TECHNICAL PROJECTS
### [Major Project Title / GitHub Link] — [Month, Year – Month, Year]
* **Technologies Used:** [Python, PyTorch, Hugging Face Transformers, Streamlit, Docker]
* **GitHub Repository:** [Insert Repository Link] | **Live Link:** [Insert Deployment Link]
* Built an AI-powered [Brief Project Description] that processed [e.g., 500+ PDF documents] with a [e.g., 95% classification accuracy].
* Designed and deployed the pipeline as a microservice using [FastAPI and Docker] to [e.g., render real-time analytics].
* Optimized search queries by [e.g., 40%] using [Elasticsearch vector index search].

### [Second Project Title / GitHub Link] — [Month, Year – Month, Year]
* **Technologies Used:** [React, Redux, Node.js, Socket.io, MongoDB]
* **GitHub Repository:** [Insert Repository Link] | **Live Link:** [Insert Deployment Link]
* Developed a collaborative [Brief Project Description] featuring [specific functionality, e.g., real-time document editing].
* Reduced server sync overhead by [e.g., 30%] by implementing [custom conflict resolution algorithms].
* Styled a sleek, custom UI using [CSS/Sass] with dark mode support.

### [Third Project Title / GitHub Link] — [Month, Year – Month, Year]
* **Technologies Used:** [C++, OpenGL, Git]
* **GitHub Repository:** [Insert Repository Link]
* Engineered a custom 3D [Brief Project Description] rendering engine supporting [specific feature, e.g., real-time ray tracing].
* Optimized memory allocations, reducing GPU footprint by [e.g., 15%] under high load stress testing.

## TECHNICAL SKILLS
* **Programming Languages:** [Python, C++, SQL, Go, HTML, CSS]
* **Frameworks & Libraries:** [PyTorch, FastAPI, React, Node.js, Express]
* **Tools & Databases:** [Docker, Git, MongoDB, PostgreSQL, Elasticsearch]

## PROFESSIONAL EXPERIENCE
**[Company Name]** — [City, State]
*Role: Technical Intern* | *[Month, Year – Month, Year]*
* Supported the migration of [number] database services, improving query performance.
* Documented API schemas and codebases to accelerate onboarding of future interns.

## EDUCATION
**[University Name]** — [City, State]
[Degree Name, e.g., B.Tech in Electronics & Communication]
*Graduation Date: [Month, Year]*
"""
    },
    "Minimal": {
        "description": "A classic, elegant, single-column design. High-level readability that stands out for its simplicity and clean typography. Perfect for standard, highly corporate, or traditional companies.",
        "icon": "📄",
        "color": "#a1a1aa",
        "tips": [
            "**Simple Formatting**: Avoid complex symbols, custom fonts, or colored shapes. Use clear headers and standard bullet points.",
            "**Standard Section Names**: Use classic headers: Education, Experience, Projects, Skills. ATS parsers categorize information based on these.",
            "**Conciseness**: Keep the content strictly within one page by removing fluff and focusing on your top accomplishments."
        ],
        "content": """# [YOUR FULL NAME]
[City, State, Zip Code] | [Your Phone Number] | [Your Email Address]
[GitHub Profile Link] | [LinkedIn Profile Link]

## EDUCATION
**[University Name]** — [City, State]
[Degree Name, e.g., Bachelor of Science in Computer Science]
*Graduation Date: [Month, Year]* | GPA: [X.X/4.0]

## EXPERIENCE
**[Company Name]** — [City, State]
*Role: Software Engineer* | *[Month, Year – Present]*
* Developed [specific features] for a core customer-facing application, increasing user engagement by [e.g., 12%].
* Streamlined data workflows by rewriting inefficient queries, resulting in a [e.g., 20% latency reduction].
* Authored clean documentation and integration tests, decreasing post-deployment errors by [e.g., 18%].

**[Second Company Name]** — [City, State]
*Role: Junior Developer* | *[Month, Year – Month, Year]*
* Maintained and updated front-end screens, ensuring cross-browser compatibility and responsive layout.
* Collaborated with backend teams to integrate REST APIs, handling secure data serialization.

## PROJECTS
### [Project Title] — [Month, Year]
* Developed an open-source tool that automates [specific task] using [Python and Git].
* Integrated [specific technology, e.g., SQLite] database to store user configuration profiles.
* Attracted [e.g., 100+ GitHub stars] and resolved issues opened by active community members.

## TECHNICAL SKILLS
* **Languages:** [Python, Java, SQL, JavaScript]
* **Web Technologies:** [HTML5, CSS3, React, Node.js]
* **Database & Cloud:** [PostgreSQL, MongoDB, AWS (EC2/S3)]
* **Developer Tools:** [Git, Docker, VS Code, Linux]
"""
    },
    "Skill-First": {
        "description": "Optimized for career changers, self-taught developers, or candidates with strong technical credentials but non-traditional professional background. Groups skills and certifications at the top.",
        "icon": "🎯",
        "color": "#a78bfa",
        "tips": [
            "**Skills Highlight**: Put your categorized skills at the very top. Prove your competencies through projects before listing past experiences.",
            "**Certifications Validation**: Show credible industry certifications (e.g., AWS, GCP, Oracle) immediately after your skills list to build trust.",
            "**Transferable Experience**: Frame past non-technical experiences in terms of project management, collaboration, and structured reasoning."
        ],
        "content": """# [YOUR FULL NAME]
[City, State, Zip Code] | [Your Phone Number] | [Your Email Address]
[GitHub Profile Link] | [LinkedIn Profile Link] | [Personal Portfolio Website]

## TECHNICAL COMPETENCIES
* **Frontend Web Development:** [React, JavaScript, HTML5, CSS3, TailwindCSS, TypeScript]
* **Backend Engineering:** [Node.js, Express, Python, FastAPI, API Integration]
* **Databases & Cloud:** [PostgreSQL, MongoDB, SQL, AWS (S3, Lambda)]
* **Developer Workflows:** [Git, GitHub, Docker, CI/CD, Agile/Scrum]

## PROFESSIONAL CERTIFICATIONS
* **[Name of Certification, e.g., AWS Certified Developer – Associate]** — [Issuer Name, Year]
* **[Name of Certification, e.g., Professional Scrum Master I (PSM I)]** — [Issuer Name, Year]

## TECHNICAL PROJECTS
### [Project Title / GitHub Link] — [Month, Year – Month, Year]
* **Technologies Used:** [React, Node.js, Express, PostgreSQL, Git]
* **GitHub Repository:** [Insert Repository Link] | **Live Link:** [Insert Deployment Link]
* Developed a full-stack [Brief Project Description] to solve [specific problem].
* Structured relational database schemas in [PostgreSQL], writing optimized join queries.
* Deployed the project to [e.g., AWS EC2], configuring secure domain and SSL certificates.

### [Second Project Title / GitHub Link] — [Month, Year – Month, Year]
* **Technologies Used:** [Python, FastAPI, MongoDB, Docker]
* **GitHub Repository:** [Insert Repository Link]
* Created a [Brief Project Description] API supporting [specific functionality].
* Utilized [MongoDB] document schema to allow fast unstructured database retrieval.

## PROFESSIONAL EXPERIENCE
**[Company Name]** — [City, State]
*Role: Project Coordinator (Transferable Role)* | *[Month, Year – Month, Year]*
* Managed timelines and project resources for a team of [number] members, delivering milestones [e.g., 10%] ahead of schedule.
* Analyzed business requirement logs and translated stakeholder feedback into technical task backlogs.

## EDUCATION
**[University Name]** — [City, State]
[Degree Name, e.g., Bachelor of Commerce (B.Com)]
*Graduation Date: [Month, Year]*
"""
    }
}

# ─────────────────────────────────────────────────────────────
# TAB RENDERING FUNCTION
# ─────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
# WIZARD STATE INITIALIZATION & COMPILATION
# ─────────────────────────────────────────────────────────────

def init_wizard_state():
    defaults = {
        "wizard_name": "Jane Doe",
        "wizard_email": "jane.doe@example.com",
        "wizard_phone": "+1 (555) 019-2834",
        "wizard_location": "San Francisco, CA",
        "wizard_github": "github.com/janedoe",
        "wizard_linkedin": "linkedin.com/in/janedoe",
        "wizard_portfolio": "janedoe.dev",
        
        "wizard_edu_count": 1,
        "wizard_school_1": "State University",
        "wizard_school_loc_1": "San Francisco, CA",
        "wizard_degree_1": "Bachelor of Science in Computer Science",
        "wizard_grad_1": "May 2026",
        "wizard_gpa_1": "3.8/4.0",
        "wizard_courses_1": "Data Structures, Algorithms, Systems Programming, Database Systems",
        "wizard_honors_1": "Dean's List (All Semesters), Academic Excellence Scholarship",
        
        "wizard_school_2": "",
        "wizard_school_loc_2": "",
        "wizard_degree_2": "",
        "wizard_grad_2": "",
        "wizard_gpa_2": "",
        "wizard_courses_2": "",
        "wizard_honors_2": "",
        
        "wizard_languages": "Python, SQL, JavaScript, C++, Bash",
        "wizard_frameworks": "React, Node.js, Django, FastAPI, PyTorch",
        "wizard_databases": "PostgreSQL, MongoDB, Redis, Docker, Git",
        "wizard_tools": "AWS (S3, EC2), GitHub Actions, Linux, Postman",
        
        "wizard_proj_count": 2,
        "wizard_proj_title_1": "AI Resume Analyzer",
        "wizard_proj_tech_1": "Python, Streamlit, PyPDF2, Gemini API",
        "wizard_proj_link_1": "github.com/janedoe/resume-analyzer",
        "wizard_proj_bullet1_1": "Built an interactive ATS scoring dashboard analyzing keyword match rates and document readability.",
        "wizard_proj_bullet2_1": "Implemented PDF text extraction and integrated LLM prompts with a 92% accuracy rating for profile extraction.",
        "wizard_proj_bullet3_1": "Designed dynamic SVG skill gauges and interactive roadmap visualization using Streamlit components.",
        
        "wizard_proj_title_2": "E-Commerce Cloud API",
        "wizard_proj_tech_2": "Go, Docker, PostgreSQL, Redis",
        "wizard_proj_link_2": "github.com/janedoe/ecommerce-api",
        "wizard_proj_bullet1_2": "Engineered a containerized microservice REST API processing up to 2,000 requests per second.",
        "wizard_proj_bullet2_2": "Implemented Redis caching layer, decreasing read query latency by 45%.",
        "wizard_proj_bullet3_2": "Configured automated CI/CD unit testing workflows using GitHub Actions and Docker Compose.",
        
        "wizard_proj_title_3": "",
        "wizard_proj_tech_3": "",
        "wizard_proj_link_3": "",
        "wizard_proj_bullet1_3": "",
        "wizard_proj_bullet2_3": "",
        "wizard_proj_bullet3_3": "",
        
        "wizard_exp_count": 1,
        "wizard_exp_company_1": "Tech Innovation Labs",
        "wizard_exp_loc_1": "San Jose, CA (Hybrid)",
        "wizard_exp_title_1": "Software Engineering Intern",
        "wizard_exp_dates_1": "June 2025 – August 2025",
        "wizard_exp_bullet1_1": "Developed and deployed 5+ user-facing React components, improving load times by 15%.",
        "wizard_exp_bullet2_1": "Wrote 30+ PyTest integration tests, increasing core backend coverage from 72% to 85%.",
        "wizard_exp_bullet3_1": "Collaborated with team leads to debug and patch critical production API routing errors.",
        
        "wizard_exp_company_2": "",
        "wizard_exp_loc_2": "",
        "wizard_exp_title_2": "",
        "wizard_exp_dates_2": "",
        "wizard_exp_bullet1_2": "",
        "wizard_exp_bullet2_2": "",
        "wizard_exp_bullet3_2": "",
        
        "wizard_exp_company_3": "",
        "wizard_exp_loc_3": "",
        "wizard_exp_title_3": "",
        "wizard_exp_dates_3": "",
        "wizard_exp_bullet1_3": "",
        "wizard_exp_bullet2_3": "",
        "wizard_exp_bullet3_3": "",
        
        "wizard_certs": "AWS Certified Developer – Associate (2025)\nGoogle Advanced Data Analytics Certificate (2024)"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def clear_wizard_form():
    for k in list(st.session_state.keys()):
        if k.startswith("wizard_"):
            if "count" in k:
                st.session_state[k] = 1
            else:
                st.session_state[k] = ""

def compile_wizard_markdown():
    lines = []
    
    # Header Details
    name = st.session_state.get("wizard_name", "").strip()
    if name:
        lines.append(f"# {name}")
    
    contact_parts = []
    loc = st.session_state.get("wizard_location", "").strip()
    if loc: contact_parts.append(loc)
    phone = st.session_state.get("wizard_phone", "").strip()
    if phone: contact_parts.append(phone)
    email = st.session_state.get("wizard_email", "").strip()
    if email: contact_parts.append(email)
    
    if contact_parts:
        lines.append(" | ".join(contact_parts))
        
    links_parts = []
    github = st.session_state.get("wizard_github", "").strip()
    if github: links_parts.append(github)
    linkedin = st.session_state.get("wizard_linkedin", "").strip()
    if linkedin: links_parts.append(linkedin)
    portfolio = st.session_state.get("wizard_portfolio", "").strip()
    if portfolio: links_parts.append(portfolio)
    
    if links_parts:
        lines.append(" | ".join(links_parts))
        
    lines.append("")
    
    # Education
    edu_count = st.session_state.get("wizard_edu_count", 1)
    has_edu = False
    for i in range(1, int(edu_count) + 1):
        school = st.session_state.get(f"wizard_school_{i}", "").strip()
        if school:
            has_edu = True
            break
            
    if has_edu:
        lines.append("## EDUCATION")
        for i in range(1, int(edu_count) + 1):
            school = st.session_state.get(f"wizard_school_{i}", "").strip()
            if not school:
                continue
            loc_val = st.session_state.get(f"wizard_school_loc_{i}", "").strip()
            loc_str = f" — {loc_val}" if loc_val else ""
            lines.append(f"**{school}**{loc_str}")
            
            deg = st.session_state.get(f"wizard_degree_{i}", "").strip()
            gpa = st.session_state.get(f"wizard_gpa_{i}", "").strip()
            gpa_str = f" | GPA: {gpa}" if gpa else ""
            if deg or gpa_str:
                lines.append(f"{deg}{gpa_str}")
                
            grad = st.session_state.get(f"wizard_grad_{i}", "").strip()
            if grad:
                lines.append(f"*Graduation Date: {grad}*")
                
            courses = st.session_state.get(f"wizard_courses_{i}", "").strip()
            if courses:
                lines.append(f"* **Relevant Coursework:** {courses}")
                
            honors = st.session_state.get(f"wizard_honors_{i}", "").strip()
            if honors:
                lines.append(f"* **Honors/Awards:** {honors}")
            lines.append("")
            
    # Technical Skills
    langs = st.session_state.get("wizard_languages", "").strip()
    fworks = st.session_state.get("wizard_frameworks", "").strip()
    dbs = st.session_state.get("wizard_databases", "").strip()
    tools = st.session_state.get("wizard_tools", "").strip()
    
    if langs or fworks or dbs or tools:
        lines.append("## TECHNICAL SKILLS")
        if langs:
            lines.append(f"* **Programming Languages:** {langs}")
        if fworks:
            lines.append(f"* **Frameworks & Tools:** {fworks}")
        if dbs:
            lines.append(f"* **Databases & Cloud:** {dbs}")
        if tools:
            lines.append(f"* **Developer Tools:** {tools}")
        lines.append("")
        
    # Technical Projects
    proj_count = st.session_state.get("wizard_proj_count", 2)
    has_proj = False
    for i in range(1, int(proj_count) + 1):
        title = st.session_state.get(f"wizard_proj_title_{i}", "").strip()
        if title:
            has_proj = True
            break
            
    if has_proj:
        lines.append("## TECHNICAL PROJECTS")
        for i in range(1, int(proj_count) + 1):
            title = st.session_state.get(f"wizard_proj_title_{i}", "").strip()
            if not title:
                continue
            tech = st.session_state.get(f"wizard_proj_tech_{i}", "").strip()
            tech_str = f" — {tech}" if tech else ""
            link = st.session_state.get(f"wizard_proj_link_{i}", "").strip()
            link_str = f" | {link}" if link else ""
            lines.append(f"### {title}{tech_str}{link_str}")
            
            b1 = st.session_state.get(f"wizard_proj_bullet1_{i}", "").strip()
            if b1:
                lines.append(f"* {b1}")
            b2 = st.session_state.get(f"wizard_proj_bullet2_{i}", "").strip()
            if b2:
                lines.append(f"* {b2}")
            b3 = st.session_state.get(f"wizard_proj_bullet3_{i}", "").strip()
            if b3:
                lines.append(f"* {b3}")
            lines.append("")
            
    # Professional Experience
    exp_count = st.session_state.get("wizard_exp_count", 1)
    has_exp = False
    for i in range(1, int(exp_count) + 1):
        comp = st.session_state.get(f"wizard_exp_company_{i}", "").strip()
        if comp:
            has_exp = True
            break
            
    if has_exp:
        lines.append("## PROFESSIONAL EXPERIENCE")
        for i in range(1, int(exp_count) + 1):
            comp = st.session_state.get(f"wizard_exp_company_{i}", "").strip()
            if not comp:
                continue
            loc_val = st.session_state.get(f"wizard_exp_loc_{i}", "").strip()
            loc_str = f" — {loc_val}" if loc_val else ""
            title = st.session_state.get(f"wizard_exp_title_{i}", "").strip()
            dates = st.session_state.get(f"wizard_exp_dates_{i}", "").strip()
            
            role_line = []
            if title: role_line.append(f"Role: {title}")
            if dates: role_line.append(dates)
            role_str = " | ".join(role_line)
            role_fmt = f"* {role_str}*" if role_str else ""
            
            lines.append(f"**{comp}**{loc_str}")
            if role_fmt:
                lines.append(role_fmt)
                
            b1 = st.session_state.get(f"wizard_exp_bullet1_{i}", "").strip()
            if b1:
                lines.append(f"* {b1}")
            b2 = st.session_state.get(f"wizard_exp_bullet2_{i}", "").strip()
            if b2:
                lines.append(f"* {b2}")
            b3 = st.session_state.get(f"wizard_exp_bullet3_{i}", "").strip()
            if b3:
                lines.append(f"* {b3}")
            lines.append("")
            
    # Certifications
    certs = st.session_state.get("wizard_certs", "").strip()
    if certs:
        lines.append("## CERTIFICATIONS & ACHIEVEMENTS")
        for c in certs.split("\n"):
            c = c.strip()
            if c:
                if not c.startswith("*"):
                    lines.append(f"* {c}")
                else:
                    lines.append(c)
        lines.append("")
        
    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────
# TAB RENDERING FUNCTION
# ─────────────────────────────────────────────────────────────

def render_templates_tab():
    st.markdown('<div class="line"></div>', unsafe_allow_html=True)
    st.markdown("""<div class="res-header">
<div class="over">Resume Builder</div>
<div class="name">Resume Builder & Templates</div>
</div>""", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size: 0.88rem; color: #a1a1aa; margin-top: -0.5rem; margin-bottom: 1.5rem;'>Create an ATS-optimized resume from scratch using our interactive Wizard, or download copy-pasteable Markdown templates.</p>", unsafe_allow_html=True)
    
    init_wizard_state()
    
    # Toggle between Wizard and Templates
    view_mode = st.radio(
        "Choose Mode:",
        options=["🧙‍♂️ Interactive Resume Wizard", "📄 Copy-Paste Markdown Templates"],
        horizontal=True,
        key="resume_view_mode_selection"
    )
    
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    
    if view_mode == "📄 Copy-Paste Markdown Templates":
        # Template Selection Radio / Cards
        with st.container(border=True):
            st.markdown("""<div class="card-head" style="margin-bottom: 0.8rem;">
                <div class="icon-box purple">📋</div><h3 style="margin:0;">Select a Resume Layout</h3></div>""", unsafe_allow_html=True)
                
            t_keys = list(TEMPLATES.keys())
            selected_key = st.radio(
                "Choose a template layout that fits your background:",
                options=t_keys,
                format_func=lambda x: f"{TEMPLATES[x]['icon']} {x} Template",
                horizontal=True,
                key="selected_resume_template_key"
            )
            
        # Active Template View
        if selected_key:
            t_data = TEMPLATES[selected_key]
            t_color = t_data["color"]
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            # Details & Guidance Card
            with st.container(border=True):
                st.markdown(f"""
                <div style="border-left: 4px solid {t_color}; padding-left: 0.8rem; margin-bottom: 0.6rem;">
                    <div style="font-size: 0.68rem; color: {t_color}; text-transform: uppercase; font-weight: 800; letter-spacing: 0.8px;">Overview & Recommendation</div>
                    <strong style="font-size: 1.1rem; color: #fafafa;">{t_data['icon']} {selected_key} Layout</strong>
                </div>
                <p style="font-size: 0.86rem; color: #d4d4d8; line-height: 1.6; margin-bottom: 1rem;">{t_data['description']}</p>
                """, unsafe_allow_html=True)
                
                st.markdown("<strong style='font-size:0.75rem; color:#71717a; text-transform:uppercase; font-weight:700; letter-spacing:0.5px; display:block; margin-bottom:0.4rem;'>ATS Formatting Tips for this Layout:</strong>", unsafe_allow_html=True)
                for tip in t_data["tips"]:
                    st.markdown(f"<div style='font-size:0.82rem; color:#a1a1aa; margin-bottom:0.35rem;'>• {tip}</div>", unsafe_allow_html=True)
                    
            # Preview and Action Tools
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            t_col_l, t_col_r = st.columns([2, 1], gap="medium")
            
            with t_col_l:
                with st.container(border=True):
                    st.markdown("""<div class="card-head" style="margin-bottom: 0.6rem;">
                        <div class="icon-box green">📝</div><h3 style="margin:0;">Markdown Template Code</h3></div>""", unsafe_allow_html=True)
                    st.markdown("<p style='font-size:0.75rem; color:#71717a; margin-top:-0.3rem;'>Copy this text, save it as a <code>.md</code> file, or paste it in a text editor to fill out your details:</p>", unsafe_allow_html=True)
                    
                    # Copy block code
                    st.code(t_data["content"], language="markdown")
                    
            with t_col_r:
                with st.container(border=True):
                    st.markdown("""<div class="card-head" style="margin-bottom: 0.6rem;">
                        <div class="icon-box blue">📥</div><h3 style="margin:0;">Actions & Downloads</h3></div>""", unsafe_allow_html=True)
                    
                    f_name_txt = f"{selected_key.lower().replace(' ', '_')}_template.txt"
                    f_name_md = f"{selected_key.lower().replace(' ', '_')}_template.md"
                    
                    st.download_button(
                        label="📥 Download Template as Markdown (.md)",
                        data=t_data["content"],
                        file_name=f_name_md,
                        mime="text/markdown",
                        use_container_width=True,
                        type="primary"
                    )
                    
                    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                    
                    st.download_button(
                        label="📄 Download Template as Text (.txt)",
                        data=t_data["content"],
                        file_name=f_name_txt,
                        mime="text/plain",
                        use_container_width=True,
                        type="secondary"
                    )
                    
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.015); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 0.8rem; margin-top: 1rem; font-size: 0.78rem; color: #a1a1aa; line-height: 1.45;">
                        💡 <strong>Pro Tip</strong>: After filling out your details in one of these templates, you can print/save the file as a PDF from your browser or editor and upload it in the sidebar pool to test your score in the dashboard!
                    </div>
                    """, unsafe_allow_html=True)
                    
    else:
        # Wizard Mode
        st.markdown("""
        <div style="border-left: 4px solid #6366f1; padding-left: 0.8rem; margin-bottom: 1rem;">
            <strong style="font-size: 1.1rem; color: #fafafa;">🧙‍♂️ Resume Builder Wizard</strong>
            <p style="font-size: 0.85rem; color: #a1a1aa; margin: 0;">Fill in the details below section by section. The builder automatically formats it into an ATS-friendly, single-column markdown resume structure.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Reset and Demo buttons in a small row
        col_actions_l, col_actions_r = st.columns([1, 1])
        with col_actions_l:
            if st.button("🔄 Reset Form (Start Blank)", use_container_width=True, key="wizard_reset_btn"):
                clear_wizard_form()
                st.rerun()
        with col_actions_r:
            if st.button("💡 Load Sample Data", use_container_width=True, key="wizard_load_sample_btn"):
                for k in list(st.session_state.keys()):
                    if k.startswith("wizard_"):
                        del st.session_state[k]
                init_wizard_state()
                st.rerun()
                
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        # Section selector tabs / radio
        wizard_sections = [
            "👤 Contact Info",
            "🎓 Education",
            "💻 Technical Skills",
            "🛠️ Projects",
            "💼 Experience",
            "🏆 Certifications",
            "👀 Preview & Export"
        ]
        
        selected_section = st.radio(
            "Select Section to Edit/View:",
            options=wizard_sections,
            horizontal=True,
            key="wizard_section_selection"
        )
        
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        if selected_section == "👤 Contact Info":
            with st.container(border=True):
                st.markdown("### 👤 Contact Information")
                st.text_input("Full Name", key="wizard_name")
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Email Address", key="wizard_email")
                    st.text_input("Phone Number", key="wizard_phone")
                with col2:
                    st.text_input("Location (City, State)", key="wizard_location")
                    st.text_input("Portfolio Website URL", key="wizard_portfolio")
                col3, col4 = st.columns(2)
                with col3:
                    st.text_input("GitHub Profile URL", key="wizard_github")
                with col4:
                    st.text_input("LinkedIn Profile URL", key="wizard_linkedin")
                    
        elif selected_section == "🎓 Education":
            with st.container(border=True):
                st.markdown("### 🎓 Education History")
                edu_count = st.number_input("Number of Education Records:", min_value=1, max_value=2, step=1, key="wizard_edu_count")
                
                for i in range(1, int(edu_count) + 1):
                    st.markdown(f"#### School {i}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_input("University/College Name", key=f"wizard_school_{i}")
                        st.text_input("Degree Name (e.g. B.Tech Computer Science)", key=f"wizard_degree_{i}")
                        st.text_input("GPA (e.g. 3.8/4.0 or 8.5/10.0)", key=f"wizard_gpa_{i}")
                    with col2:
                        st.text_input("Location (City, State)", key=f"wizard_school_loc_{i}")
                        st.text_input("Graduation Date (e.g. May 2026)", key=f"wizard_grad_{i}")
                    st.text_area("Relevant Coursework (comma separated)", key=f"wizard_courses_{i}", height=60, placeholder="Data Structures, Algorithms, Operating Systems")
                    st.text_input("Honors, Awards, or Scholarships", key=f"wizard_honors_{i}", placeholder="Dean's List, Academic Scholarship")
                    if i < edu_count:
                        st.markdown("---")
                        
        elif selected_section == "💻 Technical Skills":
            with st.container(border=True):
                st.markdown("### 💻 Technical Skills Grid")
                st.markdown("<p style='font-size:0.8rem; color:#71717a;'>Categorizing skills makes it extremely easy for ATS scanner parsing.</p>", unsafe_allow_html=True)
                st.text_area("Programming Languages", key="wizard_languages", height=60, placeholder="Python, SQL, C++, Java, JavaScript")
                st.text_area("Frameworks & Libraries", key="wizard_frameworks", height=60, placeholder="React, Node.js, Django, FastAPI, PyTorch")
                st.text_area("Databases & Cache Technologies", key="wizard_databases", height=60, placeholder="PostgreSQL, MongoDB, MySQL, Redis")
                st.text_area("Developer Tools & Platforms", key="wizard_tools", height=60, placeholder="Git, Docker, AWS (S3, EC2), GitHub Actions, Linux")
                
        elif selected_section == "🛠️ Projects":
            with st.container(border=True):
                st.markdown("### 🛠️ Technical Projects")
                proj_count = st.number_input("Number of Projects:", min_value=1, max_value=3, step=1, key="wizard_proj_count")
                
                for i in range(1, int(proj_count) + 1):
                    st.markdown(f"#### Project {i}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_input("Project Title", key=f"wizard_proj_title_{i}")
                        st.text_input("GitHub / Live Link", key=f"wizard_proj_link_{i}")
                    with col2:
                        st.text_input("Technologies Used (comma separated)", key=f"wizard_proj_tech_{i}", placeholder="Python, FastAPI, Streamlit, Docker")
                    st.text_input("Key Accomplishment 1 (Action + Result)", key=f"wizard_proj_bullet1_{i}", placeholder="Developed a real-time analytics dashboard using Streamlit, processing 50+ resume files in parallel.")
                    st.text_input("Key Accomplishment 2 (Technical Details)", key=f"wizard_proj_bullet2_{i}", placeholder="Integrated Gemini API using custom structured system prompts, improving classification accuracy by 15%.")
                    st.text_input("Key Accomplishment 3 (Performance/Scale)", key=f"wizard_proj_bullet3_{i}", placeholder="Configured automated testing workflow in GitHub Actions, reducing manual validation time by 80%.")
                    if i < proj_count:
                        st.markdown("---")
                        
        elif selected_section == "💼 Experience":
            with st.container(border=True):
                st.markdown("### 💼 Professional Experience")
                st.markdown("<p style='font-size:0.8rem; color:#71717a;'>If you are a fresher without formal work experience, you can include internships, volunteer roles, or student organization positions here.</p>", unsafe_allow_html=True)
                exp_count = st.number_input("Number of Experience Records:", min_value=1, max_value=3, step=1, key="wizard_exp_count")
                
                for i in range(1, int(exp_count) + 1):
                    st.markdown(f"#### Experience {i}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_input("Company / Organization Name", key=f"wizard_exp_company_{i}")
                        st.text_input("Job Title / Role", key=f"wizard_exp_title_{i}")
                    with col2:
                        st.text_input("Location (City, State)", key=f"wizard_exp_loc_{i}")
                        st.text_input("Employment Dates (e.g. June 2025 - Present)", key=f"wizard_exp_dates_{i}")
                    st.text_input("Key Responsibility 1", key=f"wizard_exp_bullet1_{i}", placeholder="Collaborated with 3 engineers to develop core API endpoints using FastAPI and PostgreSQL.")
                    st.text_input("Key Responsibility 2", key=f"wizard_exp_bullet2_{i}", placeholder="Optimized database index strategies, improving query response latency by 30%.")
                    st.text_input("Key Responsibility 3", key=f"wizard_exp_bullet3_{i}", placeholder="Created automated test suites using PyTest, achieving 85% coverage.")
                    if i < exp_count:
                        st.markdown("---")
                        
        elif selected_section == "🏆 Certifications":
            with st.container(border=True):
                st.markdown("### 🏆 Certifications & Achievements")
                st.markdown("<p style='font-size:0.8rem; color:#71717a;'>Add professional certifications, hackathon awards, or scholarships. Enter one per line.</p>", unsafe_allow_html=True)
                st.text_area("Certifications & Achievements (one per line)", key="wizard_certs", height=150, placeholder="AWS Certified Developer – Associate (2025)\nGoogle Advanced Data Analytics Certificate (2024)")
                
        elif selected_section == "👀 Preview & Export":
            compiled_md = compile_wizard_markdown()
            
            t_col_l, t_col_r = st.columns([3, 2], gap="medium")
            
            with t_col_l:
                with st.container(border=True):
                    st.markdown("""<div class="card-head" style="margin-bottom: 0.6rem;">
                        <div class="icon-box green">👁️</div><h3 style="margin:0;">Live Preview</h3></div>""", unsafe_allow_html=True)
                    st.markdown("<p style='font-size:0.75rem; color:#71717a;'>This is how your markdown parses visually. Copy or download using the panel on the right.</p>", unsafe_allow_html=True)
                    
                    st.markdown(compiled_md)
                    
            with t_col_r:
                with st.container(border=True):
                    st.markdown("""<div class="card-head" style="margin-bottom: 0.6rem;">
                        <div class="icon-box blue">📥</div><h3 style="margin:0;">Actions & Export</h3></div>""", unsafe_allow_html=True)
                    
                    st.download_button(
                        label="📥 Download Resume as Markdown (.md)",
                        data=compiled_md,
                        file_name="my_ats_resume.md",
                        mime="text/markdown",
                        use_container_width=True,
                        type="primary"
                    )
                    
                    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                    
                    st.download_button(
                        label="📄 Download Resume as Text (.txt)",
                        data=compiled_md,
                        file_name="my_ats_resume.txt",
                        mime="text/plain",
                        use_container_width=True,
                        type="secondary"
                    )
                    
                    st.markdown("""
                    <div style="background: rgba(255,255,255,0.015); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 0.8rem; margin-top: 1rem; font-size: 0.78rem; color: #a1a1aa; line-height: 1.45;">
                        💡 <strong>ATS Submission Tip</strong>: After exporting as <code>.md</code>, you can open it in any markdown editor or online renderer, or copy the content into a Word processor, export it as a <strong>PDF or DOCX</strong>, and then upload it back into ResumeIQ to see your score improvement!
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("🛠️ View raw Markdown source code", expanded=False):
                        st.code(compiled_md, language="markdown")

