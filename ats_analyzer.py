"""
ats_analyzer.py — Uses Groq API to analyze resumes against job descriptions.
Enhanced ATS engine with profile breakdown, career improvement, and recruiter-style output.
"""

import json
import re
import math
import string
import requests
import urllib3
import httpx
from groq import Groq

# Suppress SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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


def calculate_local_matching(resume_text, job_description):
    """
    Computes a mathematical TF-IDF Cosine Similarity score and identifies missing keywords.
    """
    # Simple stopwords list
    stopwords = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at", 
        "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "did", "do", 
        "does", "doing", "don", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", 
        "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", 
        "is", "it", "its", "itself", "just", "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", 
        "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she", 
        "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", 
        "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", 
        "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "with", "you", "your", 
        "yours", "yourself", "yourselves"
    }

    def clean_and_tokenize(text):
        if not text:
            return []
        text = text.lower()
        # Remove punctuation by replacing with space to preserve word boundaries
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        text = text.translate(translator)
        tokens = text.split()
        # Keep tokens that are longer than 1 char and not stopwords
        return [t for t in tokens if len(t) > 1 and t not in stopwords]

    tokens_res = clean_and_tokenize(resume_text)
    tokens_jd = clean_and_tokenize(job_description)

    if not tokens_res or not tokens_jd:
        return 0, []

    # Get unique words across both docs
    vocab = set(tokens_res).union(set(tokens_jd))

    # Term frequencies
    tf_res = {}
    for t in tokens_res:
        tf_res[t] = tf_res.get(t, 0) + 1
    tf_jd = {}
    for t in tokens_jd:
        tf_jd[t] = tf_jd.get(t, 0) + 1

    # In our corpus (N = 2: Resume and JD)
    # IDF = log(1 + N / DF)
    vec_res = {}
    vec_jd = {}
    for word in vocab:
        df = 0
        if word in tf_res:
            df += 1
        if word in tf_jd:
            df += 1
        
        idf = math.log(1 + 2.0 / (df if df > 0 else 1))
        
        vec_res[word] = tf_res.get(word, 0) * idf
        vec_jd[word] = tf_jd.get(word, 0) * idf

    # Cosine similarity calculation
    dot_prod = sum(vec_res[w] * vec_jd[w] for w in vocab)
    mag_res = math.sqrt(sum(vec_res[w] ** 2 for w in vocab))
    mag_jd = math.sqrt(sum(vec_jd[w] ** 2 for w in vocab))

    cosine_similarity = 0.0
    if mag_res > 0 and mag_jd > 0:
        cosine_similarity = dot_prod / (mag_res * mag_jd)

    # Convert to percentage
    similarity_percentage = int(round(cosine_similarity * 100))

    # Identify missing keywords: words that are in JD but not in Resume.
    missing_freqs = {}
    res_set = set(tokens_res)
    for word in tokens_jd:
        if word not in res_set:
            if not word.isdigit() and len(word) >= 3:
                missing_freqs[word] = missing_freqs.get(word, 0) + 1

    # Sort by frequency descending and pick top 15 missing keywords
    sorted_missing = sorted(missing_freqs.items(), key=lambda x: x[1], reverse=True)
    missing_keywords = [item[0] for item in sorted_missing[:15]]

    return similarity_percentage, missing_keywords


ATS_SYSTEM_PROMPT = """You are ResumePro, an enterprise-grade AI Career Intelligence Platform.
Your purpose is to analyze resumes against a target job description and provide structured feedback.
You will run as a multi-agent system combining:
1. **Resume Parser Agent**: Extracts education, skills, projects, and experience.
2. **Intelligent Scorer Agent**: Scores the candidate across 7 dimensions:
   - Technical Skills Match (25% weight)
   - Experience Relevance (25% weight)
   - Leadership & Growth (15% weight)
   - Cultural Fit (10% weight)
   - Presentation Quality (10% weight)
   - Sustainability (10% weight)
   - Innovation & Impact (5% weight)
3. **Job Matcher Agent**: Evaluates match score, matching breakdown, gaps (with severity), and strengths.
4. **Career Intelligence Agent**: Identifies career path scenarios (Technical, People, Specialist, Transition), skill gaps (with Coursera/Udemy/practice projects resources), and roadmaps (0-3m, 3-6m, 6-12m, 12-24m).
5. **Insight Generator Agent**: Formulates specific recruiter/hiring manager recommendations and interview questions.

---

## QUALITY, PRESENTATION, AND TONE DIRECTIVES:
- **Strict Content Grounding & Factuality (CRITICAL)**: All evaluations, scores, matched skills, missing skills, and statements must be strictly grounded on the factual content of the provided `RESUME TEXT` and `JOB DESCRIPTION`. You must never hallucinate skills, projects, degrees, or certifications that are not explicitly present or directly derivable from the resume. Any identified skill gap or missing requirement must correspond to a real, verifiable requirement in the job description that is absent in the candidate's resume.
- **Comprehensive Exhaustiveness (CRITICAL)**: You must analyze the resume and job description in extreme, exhaustive detail. Vague, short, or summary answers are unacceptable. Every explanation, recommendation, audit, and rating statement must be a multi-sentence (at least 3-4 sentences), highly thorough, and granular professional breakdown. Speak like an expert Principal Recruiter and Technical Director.
- **Tone & Professionalism**: The analysis must be professional, authoritative, objective, constructive, and highly detailed. All generated descriptions, verdicts, feedback, and explanations must be presented in a neat, clean, well-spaced, and highly professional manner. Bolding key industry terminology and using clear bullet points for lists is encouraged to ensure maximum visual clarity and readability.
- **Granular and Specific**: Avoid brief, lazy, or generic answers (e.g., "improve Python", "good job", "no issues"). Every response, recommendation, and explanation must be fully fleshed out with actionable steps, professional details, and industry-standard context.
- **Exhaustive Rationale for Dimensions (CRITICAL)**: For each of the 7 scoring dimensions in the `dimensions` JSON object, the `explanation` MUST be a detailed, professional evaluation of at least 3-4 sentences. It must explicitly outline: (1) what specific evidence was found in the resume, (2) what critical requirements from the job description are met or missing, and (3) a constructive suggestion or recommendation on how the candidate can bridge the gap or leverage this strength. Vague, single-sentence explanations (like "lacks experience in machine learning") are strictly prohibited.
- **Resume Rewrite Suggestions (CRITICAL)**: Identify 3-5 weak, passive, or non-impact statements in the resume and rewrite them using the **Google X-Y-Z Formula**: *"Accomplished [X], as measured by [Y], by doing [Z]"*. For example, rewrite *"Helped build a web app"* to *"Optimized load speed by 28% (Accomplished X) by implementing dynamic code-splitting and Redis page caching (doing Z) as verified by Chrome Lighthouse metrics (measured by Y)"*. Ensure the suggestions use strong action verbs (e.g., Spearheaded, Architected, Implemented) and are technically authentic.
- **AI-Generated Cover Letter (CRITICAL)**: Generate a highly polished, bespoke cover letter with a premium corporate tone. It must feature structured paragraphs: Introduction & Target Role, Key Value Proposition / Technical Depth, Project Highlight demonstrating core impact, Company Cultural Alignment, and a professional Call to Action closing. Do not output placeholder template brackets if candidate/job details are available; resolve them into a clean, ready-to-use letter.
- **Project Evaluation Deep-Dive**: For every project evaluated, provide concrete technical recommendations (e.g., specific architectural styles, caching layers, testing frameworks, CI/CD tools, or query optimization strategies) rather than generalities.
- **Skill Learning Hub**: Recommendations must list specific, industry-respected online courses, professional certifications, or concrete open-source milestones (e.g., "Deep Learning Specialization by Andrew Ng on Coursera", "AWS Certified Developer Associate") rather than vague advice.
- **Formatting and Structure**: Use clean paragraph styling or bullet points in string outputs, ensuring all lists are neatly presented without conversational filler.
- **No Placeholders**: Do not return placeholders like "N/A" or "Not Found" if you can synthesize a professional response from the available resume data.
- **Grammar & Casing**: Ensure professional grammar and capitalization (e.g., proper capitalization of skills like "Python", "SQL", "React").
- **Job Role Recommendations & Career Paths (CRITICAL)**: Ensure these are realistic, premium corporate pathways based on the candidate's core and transferable competencies. Under `career_paths`, you MUST generate exactly 3 to 4 diverse alternative career trajectories (such as Technical Leadership, Specialist/Deep Tech, People Management, and/or Hybrid/Transition roles) suitable for the candidate. Each trajectory must include a detailed 3-4 sentence description explaining the path, progression, and transition.
- **Constructive Gaps & Feedback**: Frame gaps as professional development opportunities (e.g., "Competency Expansion: PyTorch") rather than negative criticism.

---

## OUTPUT FORMAT:
You MUST respond with valid JSON only. No markdown, no extra text, no code fences.
Use this EXACT structure:

{
  "candidate_name": "Name or 'Not Found'",
  "parsed_data": {
    "education": [
      {
        "institution": "Institution Name",
        "degree": "Degree/Major",
        "gpa": "GPA or grade",
        "years": "Duration (e.g., 2020 - 2024)"
      }
    ],
    "skills": ["extracted_skill1", "extracted_skill2"],
    "projects": [
      {
        "title": "Project Title",
        "description": "Short summary of work done",
        "technologies": ["tech1", "tech2"]
      }
    ],
    "experience": [
      {
        "company": "Company Name",
        "role": "Role Title",
        "duration": "Duration (e.g., 2022 - Present)",
        "summary": "Key responsibilities and achievements"
      }
    ]
  },
  "profile_summary": {
    "skills_identified": ["skill1", "skill2"],
    "experience_summary": "Summary of work experience",
    "education_summary": "Education info",
    "projects_summary": "Key projects overview"
  },
  "overall_score": 0,
  "score_explanation": "A high-level professional recruitment rationale summarizing why the candidate received this overall score and their suitability.",
  "tier": "Strong Candidate", // Exceptional (90+), Strong (75-89), Qualified (60-74), Below Average (<60)
  "dimensions": {
    "technical_skills": {"score": 0, "explanation": "Detailed rationale..."},
    "experience_relevance": {"score": 0, "explanation": "Detailed rationale..."},
    "leadership_growth": {"score": 0, "explanation": "Detailed rationale..."},
    "cultural_fit": {"score": 0, "explanation": "Detailed rationale..."},
    "presentation_quality": {"score": 0, "explanation": "Detailed rationale..."},
    "sustainability": {"score": 0, "explanation": "Detailed rationale..."},
    "innovation_impact": {"score": 0, "explanation": "Detailed rationale..."}
  },
  "job_matching": {
    "match_score": 0,
    "match_breakdown": {
      "hard_skills": 0,
      "experience": 0,
      "growth_potential": 0,
      "cultural_fit": 0
    },
    "critical_gaps": [
      {"skill": "Skill Name", "severity": "high/medium/low", "candidate_level": "none/beginner", "required": "advanced"}
    ],
    "transferable_strengths": [
      {"strength": "Strength Name", "relevance": "directly applicable description..."}
    ],
    "match_tier": "Excellent Fit", // Excellent Fit (85+), Good Fit (70-84), Moderate Fit (55-69), Poor Fit (<55)
    "recommendation": "Overall recommendation..."
  },
  "skill_gaps": [
    {
      "skill": "Skill Name",
      "current_level": "beginner/none",
      "target_level": "intermediate/advanced",
      "importance": "critical/high/medium",
      "learning_time_months": 4,
      "learning_resources": [
        {"type": "course/project/certification", "name": "Course Name", "platform": "Coursera/Udemy/etc.", "duration": "Duration (e.g., 3 weeks)"}
      ],
      "career_impact": "+$10K salary increase potential..."
    }
  ],
  "roadmap": {
    "days_0_3_months": {
      "focus": "Focus description...",
      "skills": ["Skill1", "Skill2"],
      "actions": ["Action1", "Action2"],
      "roles_to_explore": ["Role1", "Role2"]
    },
    "days_3_6_months": {
      "focus": "Focus description...",
      "skills": ["Skill1", "Skill2"],
      "actions": ["Action1", "Action2"],
      "roles_to_explore": ["Role1", "Role2"]
    },
    "days_6_12_months": {
      "focus": "Focus description...",
      "skills": ["Skill1", "Skill2"],
      "actions": ["Action1", "Action2"],
      "roles_to_explore": ["Role1", "Role2"]
    },
    "days_12_24_months": {
      "focus": "Focus description...",
      "skills": ["Skill1", "Skill2"],
      "actions": ["Action1", "Action2"],
      "roles_to_explore": ["Role1", "Role2"]
    }
  },
  "career_paths": [
    {
      "path_name": "Technical Leadership",
      "description": "Exhaustive 3-4 sentence details on transitioning to a Tech Lead/Principal role, highlighting leadership progression.",
      "timeline_years": 5,
      "salary_potential": "$140K - $180K"
    },
    {
      "path_name": "Deep Tech Specialist",
      "description": "Exhaustive 3-4 sentence details on progressing to a Subject Matter Expert/Individual Contributor specialist role.",
      "timeline_years": 3,
      "salary_potential": "$130K - $160K"
    },
    {
      "path_name": "People Management",
      "description": "Exhaustive 3-4 sentence details on transitioning into Engineering/Product Management or team leadership roles.",
      "timeline_years": 5,
      "salary_potential": "$135K - $175K"
    }
  ],
  "recommendations_for_hiring_manager": ["Rec1", "Rec2"],
  "recommendations_for_candidate": ["Rec1", "Rec2"],
  "risk_assessment": {
    "retention_risk": "Low/Medium/High",
    "explanation": "Rationale..."
  },
  "interview_questions": ["Question 1", "Question 2"],
  "resume_quality_report": {
    "score": 0,
    "analysis": "Formatting, structure, readability details...",
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"]
  },
  "project_evaluation": [
    {
      "name": "Project Name",
      "score": 0,
      "complexity": "High/Medium/Low",
      "innovation": "Innovation comments",
      "value": "Business value comments",
      "deployment": "Deployment comments",
      "relevance": "Industry relevance comments",
      "strengths": ["Strength 1"],
      "weaknesses": ["Weakness 1"],
      "suggestions": ["Suggestion 1"]
    }
  ],
  "ats_benchmark": {
    "candidate_score": 0,
    "average_score": 0,
    "top_score": 0,
    "candidate_ranking": "Top 10% / Top 25% / Top 50%"
  },
  "cover_letter": {
    "introduction": "Cover letter intro...",
    "relevant_experience": "Experience alignment...",
    "project_highlights": "Project highlight...",
    "role_alignment": "Role alignment...",
    "closing": "Professional closing..."
  },
  "company_fit_analysis": {
    "ai_startups": 0,
    "saas_companies": 0,
    "product_based_companies": 0,
    "enterprise_organizations": 0,
    "faang_level_roles": 0
  },
  "github_analysis": {
    "score": 0,
    "strengths": ["Strength 1"],
    "weaknesses": ["Weakness 1"],
    "recommendations": ["Recommendation 1"]
  },
  "linkedin_analysis": {
    "score": 0,
    "strengths": ["Strength 1"],
    "weaknesses": ["Weakness 1"],
    "recommendations": ["Recommendation 1"]
  },
  "final_recruiter_verdict": {
    "verdict": "Strong Match / Good Match / Weak Match",
    "verdict_emoji": "🟢 / 🟡 / 🔴",
    "conclusion": "Conclusion statement and next steps"
  },
  "hiring_probability": {
    "ats_pass": "High/Medium/Low",
    "recruiter_shortlist": "High/Medium/Low",
    "interview_call": "High/Medium/Low",
    "hiring_potential": "High/Medium/Low",
    "reasoning": "Detailed prediction rationale"
  },
  "market_competitiveness": {
    "level": "Highly Competitive / Moderately Competitive / Below Competitive",
    "explanation": "Detailed market analysis explanation"
  },
  "rewritten_statements": [
    {
      "original": "Original weak statement from the resume",
      "suggested": "Stronger, impact-oriented rewritten statement"
    }
  ],
  "hiring_risks": [
    {
      "risk": "Risk description",
      "priority": "High/Medium/Low"
    }
  ],
  "job_role_recommendations": [
    {
      "role_tier": "Best Match / Secondary Match / Alternative Role",
      "title": "Job title",
      "match_percentage": 85,
      "reasoning": "Reasoning details"
    }
  ]
}
"""


def analyze_resume(
    resume_text: str,
    job_description: str,
    api_key: str,
    model: str = "llama-3.3-70b-versatile",
) -> dict:
    """
    Send the resume + JD to Groq or Gemini and return the structured ATS analysis.
    Handles JSON parsing, retries, and error cases.
    Bypasses proxy SSL verification errors using a custom http_client.
    """
    user_message = f"""
### RESUME TEXT:
\"\"\"
{resume_text}
\"\"\"

### JOB DESCRIPTION:
\"\"\"
{job_description}
\"\"\"

Analyze the resume against the job description. Respond ONLY with valid JSON matching the specified format. No markdown, no explanation outside JSON.
"""

    if api_key.strip().startswith("AIzaSy"):
        # Use Gemini REST API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key.strip()}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "systemInstruction": {
                "parts": [{"text": ATS_SYSTEM_PROMPT}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_message}]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.15
            }
        }
        try:
            response = requests.post(url, headers=headers, json=payload, verify=False, timeout=60)
            if response.status_code != 200:
                error_info = response.text
                try:
                    error_json = response.json()
                    error_info = error_json.get("error", {}).get("message", response.text)
                except Exception:
                    pass
                return {
                    "success": False,
                    "error": f"Gemini API Error (status {response.status_code}): {error_info}",
                    "raw": response.text
                }
            
            resp_data = response.json()
            raw_response = resp_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            # Parse JSON — handle code fences, stray text, etc.
            try:
                result = json.loads(raw_response)
                return {"success": True, "data": _validate_result(result, resume_text, job_description)}
            except json.JSONDecodeError:
                pass

            json_match = re.search(r"\{[\s\S]*\}", raw_response)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return {"success": True, "data": _validate_result(result, resume_text, job_description)}
                except json.JSONDecodeError:
                    pass

            return {
                "success": False,
                "error": "Failed to parse Gemini response as JSON.",
                "raw": raw_response
            }
        except Exception as e:
            return {"success": False, "error": f"Gemini connection error: {e}", "raw": ""}

    else:
        # Create a custom HTTP client with SSL verification disabled and trust_env=False to bypass proxy certificate errors
        http_client = httpx.Client(verify=False, trust_env=False)
        client = Groq(api_key=api_key, http_client=http_client)

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": ATS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                model=model,
                temperature=0.15,
                max_tokens=4096,
                top_p=0.9,
            )

            raw_response = chat_completion.choices[0].message.content.strip()

            # Parse JSON — handle code fences, stray text, etc.
            # Try direct parse first
            try:
                result = json.loads(raw_response)
                return {"success": True, "data": _validate_result(result, resume_text, job_description)}
            except json.JSONDecodeError:
                pass

            # Try extracting JSON from markdown/code fences
            json_match = re.search(r"\{[\s\S]*\}", raw_response)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return {"success": True, "data": _validate_result(result, resume_text, job_description)}
                except json.JSONDecodeError:
                    pass

            return {
                "success": False,
                "error": "Failed to parse AI response as JSON. The model returned an unexpected format. Please try again.",
                "raw": raw_response,
            }

        except Exception as e:
            error_msg = str(e)
            # Provide user-friendly error messages
            if "connection" in error_msg.lower() or "proxy" in error_msg.lower() or "tunnel" in error_msg.lower() or "403" in error_msg or "unreachable" in error_msg.lower():
                error_msg = (
                    "Connection error. The IDE sandbox proxy blocks connections to the Groq API (api.groq.com). "
                    "To resolve this, you can either: 1) Run `streamlit run app.py` in your local terminal "
                    "outside this IDE sandbox to connect to Groq, or 2) Enter a Google Gemini API Key "
                    "(starts with 'AIzaSy') in the sidebar to run the analysis directly within this sandbox."
                )
            elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower() or "401" in error_msg:
                error_msg = "Invalid API key. Please check your Groq API key and try again."
            elif "rate_limit" in error_msg.lower() or "429" in error_msg:
                error_msg = "Rate limit exceeded. Please wait a moment and try again."
            elif "model" in error_msg.lower() and "not found" in error_msg.lower():
                error_msg = "Selected model is not available. Please try a different model."

            return {"success": False, "error": error_msg, "raw": ""}


def _run_compliance_audit(resume_text: str) -> dict:
    if not resume_text:
        return {
            "has_email": False,
            "has_phone": False,
            "has_github": False,
            "has_linkedin": False,
            "has_experience": False,
            "has_education": False,
            "has_skills": False,
            "has_projects": False,
            "metrics_count": 0,
            "metrics_rating": "Low",
            "word_count": 0,
            "word_count_status": "Vague"
        }
        
    resume_lower = resume_text.lower()
    
    # 1. Contact details checks
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    has_email = bool(re.search(email_pattern, resume_text))
    
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,12}'
    has_phone = bool(re.search(phone_pattern, resume_text))
    
    has_github = "github.com/" in resume_lower or "github.io" in resume_lower
    has_linkedin = "linkedin.com/in/" in resume_lower or "linkedin.com/pub/" in resume_lower or "linkedin.com/company/" in resume_lower
    
    # 2. Section Checks
    exp_keywords = ["experience", "employment", "history", "work", "professional background", "career"]
    has_experience = any(kw in resume_lower for kw in exp_keywords)
    
    edu_keywords = ["education", "academic", "degree", "university", "college", "school"]
    has_education = any(kw in resume_lower for kw in edu_keywords)
    
    skills_keywords = ["skills", "technologies", "languages", "competencies", "expertise", "tools"]
    has_skills = any(kw in resume_lower for kw in skills_keywords)
    
    proj_keywords = ["projects", "key projects", "academic projects", "portfolio", "developments"]
    has_projects = any(kw in resume_lower for kw in proj_keywords)
    
    # 3. Quantifiable Metrics
    metrics_patterns = [
        r'\d+%',
        r'[\$\£\€\¥\₹]\s?\d+',
        r'\b\d+(?:,\d+)?\+?\s?(?:million|billion|k|lpa|ctc|cr|lakh|lakhs)\b',
        r'\b\d+x\b',
        r'\b\d{2,}\+?\b'
    ]
    metrics_count = 0
    for pattern in metrics_patterns:
        matches = re.findall(pattern, resume_lower)
        metrics_count += len(matches)
        
    if metrics_count >= 8:
        metrics_rating = "Excellent"
    elif metrics_count >= 3:
        metrics_rating = "Moderate"
    else:
        metrics_rating = "Low"
        
    # 4. Word Count Check
    words = resume_text.split()
    word_count = len(words)
    if word_count > 1500:
        word_count_status = "Long"
    elif word_count >= 400:
        word_count_status = "Optimal"
    else:
        word_count_status = "Vague"
        
    return {
        "has_email": has_email,
        "has_phone": has_phone,
        "has_github": has_github,
        "has_linkedin": has_linkedin,
        "has_experience": has_experience,
        "has_education": has_education,
        "has_skills": has_skills,
        "has_projects": has_projects,
        "metrics_count": metrics_count,
        "metrics_rating": metrics_rating,
        "word_count": word_count,
        "word_count_status": word_count_status
    }


def _validate_result(data: dict, resume_text: str = "", job_description: str = "") -> dict:
    """Ensure all expected fields exist with sensible defaults."""
    defaults = {
        "candidate_name": "Not Found",
        "parsed_data": {
            "education": [],
            "skills": [],
            "projects": [],
            "experience": []
        },
        "profile_summary": {
            "skills_identified": [],
            "experience_summary": "Not available",
            "education_summary": "Not available",
            "projects_summary": "Not available",
        },
        "overall_score": 0,
        "score_explanation": "No explanation available.",
        "ats_score": 0,
        "resume_quality_score": 0,
        "interview_readiness_score": 0,
        "tier": "Below Average",
        "dimensions": {
            "technical_skills": {"score": 0, "explanation": "Not available"},
            "experience_relevance": {"score": 0, "explanation": "Not available"},
            "leadership_growth": {"score": 0, "explanation": "Not available"},
            "cultural_fit": {"score": 0, "explanation": "Not available"},
            "presentation_quality": {"score": 0, "explanation": "Not available"},
            "sustainability": {"score": 0, "explanation": "Not available"},
            "innovation_impact": {"score": 0, "explanation": "Not available"}
        },
        "job_matching": {
            "match_score": 0,
            "match_breakdown": {
                "hard_skills": 0,
                "experience": 0,
                "growth_potential": 0,
                "cultural_fit": 0
            },
            "critical_gaps": [],
            "transferable_strengths": [],
            "match_tier": "Poor Fit",
            "recommendation": "Not available"
        },
        "skill_gaps": [],
        "roadmap": {
            "days_0_3_months": {"focus": "Not available", "skills": [], "actions": [], "roles_to_explore": []},
            "days_3_6_months": {"focus": "Not available", "skills": [], "actions": [], "roles_to_explore": []},
            "days_6_12_months": {"focus": "Not available", "skills": [], "actions": [], "roles_to_explore": []},
            "days_12_24_months": {"focus": "Not available", "skills": [], "actions": [], "roles_to_explore": []}
        },
        "career_paths": [],
        "recommendations_for_hiring_manager": [],
        "recommendations_for_candidate": [],
        "risk_assessment": {
            "retention_risk": "Low",
            "explanation": "Not available"
        },
        "interview_questions": [],
        "resume_quality_report": {
            "score": 0,
            "analysis": "Not available",
            "strengths": [],
            "weaknesses": []
        },
        "project_evaluation": [],
        "ats_benchmark": {
            "candidate_score": 0,
            "average_score": 0,
            "top_score": 0,
            "candidate_ranking": "Not available"
        },
        "cover_letter": {
            "introduction": "",
            "relevant_experience": "",
            "project_highlights": "",
            "role_alignment": "",
            "closing": ""
        },
        "company_fit_analysis": {
            "ai_startups": 0,
            "saas_companies": 0,
            "product_based_companies": 0,
            "enterprise_organizations": 0,
            "faang_level_roles": 0
        },
        "github_analysis": {
            "score": 0,
            "strengths": [],
            "weaknesses": [],
            "recommendations": []
        },
        "linkedin_analysis": {
            "score": 0,
            "strengths": [],
            "weaknesses": [],
            "recommendations": []
        },
        "final_recruiter_verdict": {
            "verdict": "Weak Match",
            "verdict_emoji": "🔴",
            "conclusion": "Not available"
        },
        "hiring_probability": {
            "ats_pass": "Low",
            "recruiter_shortlist": "Low",
            "interview_call": "Low",
            "hiring_potential": "Low",
            "reasoning": "Not available"
        },
        "market_competitiveness": {
            "level": "Below Competitive",
            "explanation": "Not available"
        },
        "rewritten_statements": [],
        "hiring_risks": [],
        "job_role_recommendations": [],
        "local_match_score": 0,
        "missing_keywords": [],
        "matched_skills": [],
        "missing_skills": [],
        "critical_missing_skills": [],
        "recommended_skills": [],
        "compliance_audit": {
            "has_email": False,
            "has_phone": False,
            "has_github": False,
            "has_linkedin": False,
            "has_experience": False,
            "has_education": False,
            "has_skills": False,
            "has_projects": False,
            "metrics_count": 0,
            "metrics_rating": "Low",
            "word_count": 0,
            "word_count_status": "Vague"
        }
    }

    for key, default_val in defaults.items():
        if key not in data:
            data[key] = default_val
        elif isinstance(default_val, dict):
            for sub_key, sub_default in default_val.items():
                if sub_key not in data[key]:
                    data[key][sub_key] = sub_default

    # Run compliance audit if resume_text is provided
    if resume_text:
        data["compliance_audit"] = _run_compliance_audit(resume_text)

    # Calculate local match metrics if not already done
    if resume_text and job_description:
        local_score, missing_kws = calculate_local_matching(resume_text, job_description)
        data["local_match_score"] = local_score
        data["missing_keywords"] = missing_kws

    # Validate and clamp dimension scores
    if "dimensions" in data and isinstance(data["dimensions"], dict):
        for dim_k in ["technical_skills", "experience_relevance", "leadership_growth", "cultural_fit", "presentation_quality", "sustainability", "innovation_impact"]:
            if dim_k not in data["dimensions"]:
                data["dimensions"][dim_k] = {"score": 0, "explanation": "Not available"}
            try:
                data["dimensions"][dim_k]["score"] = max(0, min(100, int(data["dimensions"][dim_k].get("score", 0))))
            except Exception:
                data["dimensions"][dim_k]["score"] = 0

    # Enforce overall score calculation:
    # (Technical × 0.25) + (Experience × 0.25) + (Leadership × 0.15) + (Cultural × 0.10) + (Presentation × 0.10) + (Sustainability × 0.10) + (Innovation × 0.05)
    if "dimensions" in data and isinstance(data["dimensions"], dict):
        dims = data["dimensions"]
        t = dims.get("technical_skills", {}).get("score", 0)
        e = dims.get("experience_relevance", {}).get("score", 0)
        l = dims.get("leadership_growth", {}).get("score", 0)
        c = dims.get("cultural_fit", {}).get("score", 0)
        p = dims.get("presentation_quality", {}).get("score", 0)
        s = dims.get("sustainability", {}).get("score", 0)
        i = dims.get("innovation_impact", {}).get("score", 0)
        calculated_overall = int(round(t * 0.25 + e * 0.25 + l * 0.15 + c * 0.10 + p * 0.10 + s * 0.10 + i * 0.05))
        data["overall_score"] = max(0, min(100, calculated_overall))
    else:
        try:
            data["overall_score"] = max(0, min(100, int(data.get("overall_score", 0))))
        except Exception:
            data["overall_score"] = 0

    # Enforce legacy field mapping so existing history items don't break
    data["ats_score"] = data["overall_score"]

    # Deduce tier based on score
    score = data["overall_score"]
    if score >= 90:
        data["tier"] = "Exceptional Candidate"
    elif score >= 75:
        data["tier"] = "Strong Candidate"
    elif score >= 60:
        data["tier"] = "Qualified Candidate"
    else:
        data["tier"] = "Below Average Candidate"

    # Pull and compute resume quality score dynamically if 0 or missing
    rq_score = data.get("resume_quality_score", 0)
    if not rq_score:
        rq_score = data.get("resume_quality_report", {}).get("score", 0)
    if not rq_score:
        rq_score = data.get("dimensions", {}).get("presentation_quality", {}).get("score", 0)
    if not rq_score:
        rq_score = int(round(data.get("overall_score", 70) * 1.05))
    data["resume_quality_score"] = max(10, min(100, int(rq_score)))

    # Pull and compute interview readiness score dynamically if 0 or missing
    ir_score = data.get("interview_readiness_score", 0)
    if not ir_score:
        t_score = data.get("dimensions", {}).get("technical_skills", {}).get("score", 70)
        e_score = data.get("dimensions", {}).get("experience_relevance", {}).get("score", 70)
        c_score_val = data.get("dimensions", {}).get("cultural_fit", {}).get("score", 70)
        ir_score = int(round(t_score * 0.4 + e_score * 0.4 + c_score_val * 0.2))
    if not ir_score:
        ir_score = int(round(data.get("overall_score", 70) * 0.95))
    data["interview_readiness_score"] = max(10, min(100, int(ir_score)))

    # Dynamic hiring probability matching overall score
    overall = data["overall_score"]
    hp = data.get("hiring_probability", {})
    if not isinstance(hp, dict):
        hp = {}
    
    if "ats_pass" not in hp or hp.get("ats_pass") in ["Low", "Medium", "High", "Not available"]:
        if overall >= 80:
            hp["ats_pass"] = "High"
        elif overall >= 60:
            hp["ats_pass"] = "Medium"
        else:
            hp["ats_pass"] = "Low"
            
    if "recruiter_shortlist" not in hp or hp.get("recruiter_shortlist") in ["Low", "Medium", "High", "Not available"]:
        if overall >= 85:
            hp["recruiter_shortlist"] = "High"
        elif overall >= 65:
            hp["recruiter_shortlist"] = "Medium"
        else:
            hp["recruiter_shortlist"] = "Low"
            
    if "interview_call" not in hp or hp.get("interview_call") in ["Low", "Medium", "High", "Not available"]:
        if overall >= 80:
            hp["interview_call"] = "High"
        elif overall >= 65:
            hp["interview_call"] = "Medium"
        else:
            hp["interview_call"] = "Low"
            
    if "hiring_potential" not in hp or hp.get("hiring_potential") in ["Low", "Medium", "High", "Not available"]:
        if overall >= 85:
            hp["hiring_potential"] = "High"
        elif overall >= 70:
            hp["hiring_potential"] = "Medium"
        else:
            hp["hiring_potential"] = "Low"
            
    data["hiring_probability"] = hp

    # Legacy score breakdown mapping for backward compatibility with radar charts, etc.
    data["score_breakdown"] = {
        "skills": data["dimensions"].get("technical_skills", {}).get("score", 0),
        "experience": data["dimensions"].get("experience_relevance", {}).get("score", 0),
        "projects": data["dimensions"].get("innovation_impact", {}).get("score", 0),
        "formatting": data["dimensions"].get("presentation_quality", {}).get("score", 0)
    }

    # Validate project scores
    if "project_evaluation" in data and isinstance(data["project_evaluation"], list):
        for proj in data["project_evaluation"]:
            if isinstance(proj, dict):
                try:
                    proj["score"] = max(0, min(100, int(proj.get("score", 0))))
                except Exception:
                    proj["score"] = 0

    # Validate benchmark scores
    if "ats_benchmark" in data and isinstance(data["ats_benchmark"], dict):
        for b_key in ["candidate_score", "average_score", "top_score"]:
            try:
                data["ats_benchmark"][b_key] = max(0, min(100, int(data["ats_benchmark"].get(b_key, 0))))
            except Exception:
                data["ats_benchmark"][b_key] = 0

    # Validate company fit scores
    if "company_fit_analysis" in data and isinstance(data["company_fit_analysis"], dict):
        for c_key in data["company_fit_analysis"]:
            try:
                data["company_fit_analysis"][c_key] = max(0, min(100, int(data["company_fit_analysis"].get(c_key, 0))))
            except Exception:
                data["company_fit_analysis"][c_key] = 0

    # Validate social profile scores
    for profile_key in ["github_analysis", "linkedin_analysis"]:
        if profile_key in data and isinstance(data[profile_key], dict):
            try:
                data[profile_key]["score"] = max(0, min(100, int(data[profile_key].get("score", 0))))
            except Exception:
                data[profile_key]["score"] = 0

    # Normalize interview_questions to a dictionary of categories
    questions = data.get("interview_questions")
    if not isinstance(questions, dict):
        q_list = questions if isinstance(questions, list) else []
        data["interview_questions"] = {
            "technical": q_list,
            "project_based": [],
            "behavioral": [],
            "role_specific": []
        }

    # Dynamic generation of skills intelligence metrics
    resume_skills = data.get("parsed_data", {}).get("skills", [])
    if not resume_skills:
        resume_skills = data.get("profile_summary", {}).get("skills_identified", [])
        
    if resume_text and not resume_skills:
        # Simple fallback parsing from raw text
        resume_skills = [s.strip() for s in resume_text.split(",") if len(s.strip()) < 30][:10]

    # Clean and format resume skills
    formatted_resume_skills = []
    for sk in resume_skills:
        fmt = format_keyword(sk)
        if fmt and fmt not in formatted_resume_skills:
            formatted_resume_skills.append(fmt)
    if not formatted_resume_skills and resume_skills:
        formatted_resume_skills = [sk.title() for sk in resume_skills]

    # Matched skills computation
    jd_lower = job_description.lower() if job_description else ""
    matched_skills = []
    for sk in formatted_resume_skills:
        if jd_lower and sk.lower() in jd_lower:
            matched_skills.append(sk)
            
    # Fallback matching based on gaps
    if not matched_skills and formatted_resume_skills:
        gaps_set = {g.get("skill", "").lower() for g in data.get("job_matching", {}).get("critical_gaps", [])}
        matched_skills = [sk for sk in formatted_resume_skills if sk.lower() not in gaps_set]
        
    data["matched_skills"] = matched_skills

    # Extract missing skills from AI job matching gaps
    gaps = data.get("job_matching", {}).get("critical_gaps", [])
    critical_missing = []
    other_missing = []
    
    for g in gaps:
        skill_name = g.get("skill")
        if skill_name:
            fmt_skill = format_keyword(skill_name)
            if not fmt_skill:
                continue
            if fmt_skill in matched_skills:
                continue
            if g.get("severity", "").lower() in ["high", "critical"]:
                if fmt_skill not in critical_missing:
                    critical_missing.append(fmt_skill)
            else:
                if fmt_skill not in other_missing:
                    other_missing.append(fmt_skill)
                    
    # Fallback to local missing keywords
    missing_kws = data.get("missing_keywords", [])
    formatted_missing_kws = []
    for kw in missing_kws:
        fmt = format_keyword(kw)
        if fmt and fmt not in formatted_missing_kws:
            if fmt not in matched_skills and fmt not in critical_missing and fmt not in other_missing:
                formatted_missing_kws.append(fmt)
            
    if not critical_missing and formatted_missing_kws:
        critical_missing = formatted_missing_kws[:4]
        formatted_missing_kws = formatted_missing_kws[4:]
    if not other_missing and formatted_missing_kws:
        other_missing = formatted_missing_kws[:6]
        
    data["critical_missing_skills"] = critical_missing
    data["missing_skills"] = other_missing

    # Extract recommended skills
    rec_skills = []
    for item in data.get("skill_gaps", []):
        sk = item.get("skill")
        if sk:
            fmt = format_keyword(sk)
            if fmt and fmt not in rec_skills and fmt not in matched_skills and fmt not in critical_missing and fmt not in other_missing:
                rec_skills.append(fmt)
                
    # Fallback to roadmap
    if not rec_skills:
        rm = data.get("roadmap", {})
        for phase in ["days_0_3_months", "days_3_6_months"]:
            for sk in rm.get(phase, {}).get("skills", []):
                fmt = format_keyword(sk)
                if fmt and fmt not in rec_skills and fmt not in matched_skills and fmt not in critical_missing and fmt not in other_missing:
                    rec_skills.append(fmt)
                    
    data["recommended_skills"] = rec_skills

    return data



