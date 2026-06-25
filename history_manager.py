import os
import json
import datetime

HISTORY_FILE = "resume_history.json"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except Exception:
        pass

def add_to_history(filename, job_description, analysis_data, resume_text, sel_model):
    history = load_history()
    candidate_name = analysis_data.get("candidate_name", "Not Found")
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for h in history:
        if h.get("candidate_name") == candidate_name and h.get("filename") == filename:
            h["timestamp"] = now_str
            h["ats_score"] = analysis_data.get("ats_score", 0)
            h["resume_quality_score"] = analysis_data.get("resume_quality_score", 0)
            h["interview_readiness_score"] = analysis_data.get("interview_readiness_score", 0)
            h["analysis_data"] = analysis_data
            h["resume_text"] = resume_text
            h["sel_model"] = sel_model
            h["job_description"] = job_description
            
            # Preserve or initialize versions, roadmap progress, mock interviews, applications
            if "versions" not in h or not h["versions"]:
                h["versions"] = [{"version_num": 1, "timestamp": now_str, "ats_score": h["ats_score"], "resume_text": resume_text, "change_summary": "Initial Upload"}]
            if "learning_progress" not in h:
                h["learning_progress"] = {}
            if "mock_interviews" not in h:
                h["mock_interviews"] = []
            if "job_applications" not in h:
                h["job_applications"] = []
            save_history(history)
            return

    new_id = str(datetime.datetime.now().timestamp())
    entry = {
        "id": new_id,
        "timestamp": now_str,
        "filename": filename,
        "candidate_name": candidate_name,
        "ats_score": analysis_data.get("ats_score", 0),
        "resume_quality_score": analysis_data.get("resume_quality_score", 0),
        "interview_readiness_score": analysis_data.get("interview_readiness_score", 0),
        "analysis_data": analysis_data,
        "resume_text": resume_text,
        "sel_model": sel_model,
        "job_description": job_description,
        "versions": [{"version_num": 1, "timestamp": now_str, "ats_score": analysis_data.get("ats_score", 0), "resume_text": resume_text, "change_summary": "Initial Upload"}],
        "learning_progress": {},
        "mock_interviews": [],
        "job_applications": []
    }
    history.append(entry)
    save_history(history)

def get_candidate_by_id(candidate_id):
    history = load_history()
    for h in history:
        if h.get("id") == candidate_id:
            # Backward compatibility fix if loaded from legacy JSON without these keys
            if "versions" not in h or not h["versions"]:
                h["versions"] = [{"version_num": 1, "timestamp": h.get("timestamp", ""), "ats_score": h.get("ats_score", 0), "resume_text": h.get("resume_text", ""), "change_summary": "Initial Upload"}]
            if "learning_progress" not in h:
                h["learning_progress"] = {}
            if "mock_interviews" not in h:
                h["mock_interviews"] = []
            if "job_applications" not in h:
                h["job_applications"] = []
            return h
    return None

def update_candidate_record(candidate_id, update_dict):
    history = load_history()
    for h in history:
        if h.get("id") == candidate_id:
            for key, val in update_dict.items():
                h[key] = val
            save_history(history)
            return True
    return False
