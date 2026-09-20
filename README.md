<div align="center">

# 🚀 ResumeIQ 🚀

### Analyze. Optimize. Stand Out.

![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-1.0.0-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)
![Type](https://img.shields.io/badge/Type-AI%20Resume%20Analyzer-D97757?style=for-the-badge)

An AI-powered resume analysis and optimization platform. Upload your resume and a target job description to get ATS scoring, skill gap analysis, bullet rewrites, and a personalized career roadmap, all in one dashboard.

*Turn resume review into a data-driven process.*

</div>

---

## 🚀 Live Demo

<div align="center">

### **[▶️ LAUNCH RESUMEIQ - Live Demo](https://resumeiq-aybfmvsyuvh5mra4savae2.streamlit.app)**

*Upload a resume, paste a job description, and get your full analysis in your browser!*

</div>

---

## ✨ Features

- 📊 **ATS Evaluation** - Compatibility, resume quality, interview readiness, and pass-rate prediction
- 🎯 **Skills Intelligence** - Keyword matching, missing requirements, and upskilling recommendations
- 🔧 **Bullet Optimization** - AI bullet rewriting, action-verb strength, and impact metrics
- 🗺️ **Career Roadmap** - A 2-year plan with milestones and target role suggestions
- 🔍 **Profile Intelligence** - GitHub and LinkedIn audits with tech-stack showcase tips
- 🎤 **Interview Prep** - Role-specific practice questions
- 📈 **Interactive Dashboard** - Dimension-wise radar chart and matched vs. missing skills
- 🛟 **Automatic Fallback** - Seamless switch between LLM providers if a quota is reached
- 📄 **PDF & DOCX Upload** - Structured extraction from your resume and the job description

---

## 🏁 Quick Start

### Use Online
No installation needed! [Launch the live demo](https://resumeiq-aybfmvsyuvh5mra4savae2.streamlit.app)

### Run Locally

**Prerequisites:** Python 3.8+, an [Anthropic API key](https://console.anthropic.com/), and (optionally) a [Groq API key](https://console.groq.com/keys) for fallback

1. Clone the repository:
```bash
git clone https://github.com/kschouhanpali-coder/ResumeIQ.git
cd ResumeIQ
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
cp .env.example .env
```
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

4. Start the app:
```bash
streamlit run app.py
```

5. Open `http://localhost:8501` in your browser

---

## 🎯 How to Use

1. **Open Analyze New Resume** from the sidebar
2. **Upload** your resume (PDF or DOCX)
3. **Paste** the target job description
4. **Click Analyze Resume** to generate your report
5. **Review** the ATS dashboard, skill gaps, rewritten bullets, career roadmap, and interview questions
6. **Configure** API keys any time under **Settings**

---

## 🗂️ Analysis Modules

| Module | Description |
|--------|-------------|
| **📊 ATS Evaluation** | Compatibility scoring, formatting, and pass-rate prediction |
| **🎯 Skills Intelligence** | Keyword matching, gap detection, and requirement mapping |
| **🔧 Optimization** | Bullet rewriting, impact statements, and metrics extraction |
| **🗺️ Career Roadmap** | 2-year planning, milestones, and role targeting |
| **🔍 Profile Intelligence** | GitHub and LinkedIn audits and network insights |

---

## 💻 Technologies Used

- **Frontend:** Streamlit
- **Primary LLM:** Anthropic Claude
- **Fallback LLM:** Groq
- **Core Libraries:** `streamlit`, `anthropic`, `groq`, `python-dotenv`, `requests`
- **Deployment:** Streamlit Cloud

---

## 📝 License

MIT License - Free to use and modify

---

<div align="center">

**[Live Demo](https://resumeiq-aybfmvsyuvh5mra4savae2.streamlit.app) | [GitHub](https://github.com/kschouhanpali-coder/ResumeIQ) | [Report Issues](https://github.com/kschouhanpali-coder/ResumeIQ/issues)**

*Turn resume review into a data-driven process.* 🚀

</div>
