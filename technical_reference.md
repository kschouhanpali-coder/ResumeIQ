# ResumeIQ - Technical Reference Guide

## Database Schema & API Endpoints

---

## 📁 Complete Database Schema

### User Management

```sql
-- Users table (extends existing auth)
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255),
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  profile_picture_url TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP,
  subscription_plan VARCHAR(50), -- 'free', 'pro', 'enterprise'
  subscription_expires_at TIMESTAMP,
  preferences JSONB, -- User preferences like theme, notifications, etc
  deleted_at TIMESTAMP -- Soft delete
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription_plan ON users(subscription_plan);
```

### Resume Management

```sql
-- Resumes
CREATE TABLE resumes (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255), -- e.g., "Senior ML Engineer Resume"
  content JSONB NOT NULL, -- Rich text content
  raw_text TEXT, -- Plain text for searching
  ats_score INT,
  readability_score INT,
  keyword_density INT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_analyzed_at TIMESTAMP,
  status VARCHAR(50), -- 'draft', 'active', 'archived'
  is_default BOOLEAN DEFAULT FALSE,
  version INT DEFAULT 1
);

CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_resumes_status ON resumes(status);

-- Resume versions (complete history)
CREATE TABLE resume_versions (
  id UUID PRIMARY KEY,
  resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
  version_num INT NOT NULL,
  content JSONB NOT NULL,
  previous_version_id UUID REFERENCES resume_versions(id),
  ats_score INT,
  readability_score INT,
  created_at TIMESTAMP DEFAULT NOW(),
  created_by UUID REFERENCES users(id),
  tag VARCHAR(255), -- 'Final for Netflix', 'Tech roles v2'
  notes TEXT,
  change_summary TEXT
);

CREATE INDEX idx_resume_versions_resume_id ON resume_versions(resume_id);
CREATE INDEX idx_resume_versions_version_num ON resume_versions(version_num);

-- Resume issues/feedback
CREATE TABLE resume_issues (
  id UUID PRIMARY KEY,
  resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
  issue_type VARCHAR(100), -- 'missing_action_verb', 'weak_description', 'no_metrics'
  severity VARCHAR(50), -- 'critical', 'high', 'medium', 'low'
  section VARCHAR(100), -- 'summary', 'experience', 'skills', 'education'
  line_number INT,
  message TEXT NOT NULL,
  suggested_fix TEXT,
  examples JSON, -- Array of example fixes
  resolved BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_resume_issues_resume_id ON resumes(id);
CREATE INDEX idx_resume_issues_severity ON resume_issues(severity);
```

### Skills & Learning

```sql
-- Skills master database
CREATE TABLE skills (
  id UUID PRIMARY KEY,
  skill_name VARCHAR(255) UNIQUE NOT NULL,
  category VARCHAR(100), -- 'Programming', 'ML', 'DevOps', 'Soft Skills'
  subcategory VARCHAR(100),
  description TEXT,
  difficulty_level INT, -- 1-5 scale
  job_demand_percentage INT, -- % of jobs requiring this skill
  avg_salary_boost INT, -- $ increase with this skill
  estimated_learning_hours INT,
  prerequisites JSON, -- Array of skill IDs
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_job_demand ON skills(job_demand_percentage);

-- User skill proficiency
CREATE TABLE user_skills (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  skill_id UUID NOT NULL REFERENCES skills(id),
  proficiency_level VARCHAR(50), -- 'beginner', 'intermediate', 'advanced', 'expert'
  years_experience DECIMAL(3,1),
  verified BOOLEAN DEFAULT FALSE,
  verified_by VARCHAR(100), -- 'self', 'course', 'exam', 'work_experience', 'peer'
  certificate_url TEXT,
  verified_at TIMESTAMP,
  verified_by_user_id UUID REFERENCES users(id),
  endorsements_count INT DEFAULT 0,
  added_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_user_skills_unique ON user_skills(user_id, skill_id);
CREATE INDEX idx_user_skills_verified ON user_skills(verified);

-- Learning paths
CREATE TABLE learning_paths (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  target_role VARCHAR(255), -- 'ML Engineer', 'Data Scientist', etc
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  completion_timeline_months INT, -- 3, 6, 12
  learning_style VARCHAR(50), -- 'video', 'interactive', 'project-based', 'mixed'
  status VARCHAR(50), -- 'active', 'paused', 'completed'
  completion_percentage INT DEFAULT 0,
  estimated_hours INT,
  actual_hours INT DEFAULT 0
);

CREATE INDEX idx_learning_paths_user_id ON learning_paths(user_id);
CREATE INDEX idx_learning_paths_status ON learning_paths(status);

-- Learning path steps/milestones
CREATE TABLE learning_path_steps (
  id UUID PRIMARY KEY,
  learning_path_id UUID NOT NULL REFERENCES learning_paths(id) ON DELETE CASCADE,
  step_number INT NOT NULL,
  skill_id UUID REFERENCES skills(id),
  title VARCHAR(255),
  description TEXT,
  courses JSON, -- Array of {course_id, platform, title, url, cost, duration, rating}
  projects JSON, -- Array of project recommendations
  estimated_hours INT,
  status VARCHAR(50), -- 'not_started', 'in_progress', 'completed'
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  notes TEXT
);

CREATE INDEX idx_learning_path_steps_learning_path ON learning_path_steps(learning_path_id);

-- Courses (external)
CREATE TABLE courses (
  id UUID PRIMARY KEY,
  skill_id UUID REFERENCES skills(id),
  platform VARCHAR(100), -- 'udemy', 'coursera', 'pluralsight', 'youtube', 'official_docs'
  external_id VARCHAR(255), -- Platform's_course_id
  title VARCHAR(255) NOT NULL,
  description TEXT,
  course_url TEXT NOT NULL,
  instructor_name VARCHAR(255),
  price DECIMAL(10, 2),
  is_free BOOLEAN DEFAULT FALSE,
  duration_hours INT,
  difficulty VARCHAR(50),
  rating FLOAT, -- 0-5
  review_count INT,
  student_count INT,
  created_at TIMESTAMP DEFAULT NOW(),
  last_updated TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_courses_skill_id ON courses(skill_id);
CREATE INDEX idx_courses_platform ON courses(platform);

-- Certifications
CREATE TABLE certifications (
  id UUID PRIMARY KEY,
  skill_id UUID REFERENCES skills(id),
  certification_name VARCHAR(255), -- 'AWS Solutions Architect'
  provider VARCHAR(255), -- 'Amazon', 'Google', etc
  description TEXT,
  exam_cost DECIMAL(10, 2),
  prep_hours INT,
  validity_years INT,
  salary_boost INT,
  difficulty VARCHAR(50),
  official_link TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- User certifications earned
CREATE TABLE user_certifications (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  certification_id UUID NOT NULL REFERENCES certifications(id),
  certificate_url TEXT,
  earned_date DATE,
  expiry_date DATE,
  credential_id VARCHAR(255),
  verification_url TEXT,
  added_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_certifications_user_id ON user_certifications(user_id);
CREATE INDEX idx_user_certifications_earned_date ON user_certifications(earned_date);
```

### Interview Preparation

```sql
-- Interview questions database
CREATE TABLE interview_questions (
  id UUID PRIMARY KEY,
  question_text TEXT NOT NULL,
  job_title VARCHAR(255), -- 'Data Scientist', 'ML Engineer'
  company_name VARCHAR(255), -- 'Netflix', 'Google'
  question_type VARCHAR(50), -- 'behavioral', 'technical', 'domain', 'situational'
  question_category VARCHAR(100), -- 'Problem Solving', 'Communication', etc
  difficulty VARCHAR(50), -- 'easy', 'medium', 'hard'
  answer_template TEXT,
  follow_up_questions JSON, -- Array of follow-up questions
  success_tips TEXT,
  common_mistakes TEXT,
  time_estimate_minutes INT,
  created_at TIMESTAMP DEFAULT NOW(),
  created_by VARCHAR(255), -- 'community', 'admin'
  helpful_count INT DEFAULT 0,
  view_count INT DEFAULT 0
);

CREATE INDEX idx_interview_questions_job_title ON interview_questions(job_title);
CREATE INDEX idx_interview_questions_company ON interview_questions(company_name);
CREATE INDEX idx_interview_questions_type ON interview_questions(question_type);

-- Mock interview sessions
CREATE TABLE mock_interviews (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  interview_type VARCHAR(50), -- 'behavioral', 'technical', 'system_design'
  duration_minutes INT,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  status VARCHAR(50), -- 'in_progress', 'completed', 'abandoned'
  questions_asked JSON, -- Array of question IDs
  user_responses JSON, -- Array of {question_id, response_type, response_url_or_text, duration}
  overall_score INT, -- 0-100
  feedback TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_mock_interviews_user_id ON mock_interviews(user_id);
CREATE INDEX idx_mock_interviews_status ON mock_interviews(status);
CREATE INDEX idx_mock_interviews_created_at ON mock_interviews(created_at);

-- Interview performance scores
CREATE TABLE interview_performance_scores (
  id UUID PRIMARY KEY,
  mock_interview_id UUID NOT NULL REFERENCES mock_interviews(id) ON DELETE CASCADE,
  communication_clarity INT, -- 0-100
  technical_accuracy INT,
  problem_solving INT,
  confidence INT,
  time_management INT,
  structure_and_clarity INT,
  overall_score INT, -- 0-100
  detailed_feedback TEXT,
  improvements_suggested JSON, -- Array of improvement suggestions
  video_analysis JSON, -- {eye_contact_score, pace_score, filler_words_count, etc}
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_performance_scores_mock_interview ON interview_performance_scores(mock_interview_id);

-- Interview frameworks
CREATE TABLE interview_frameworks (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  framework_type VARCHAR(50), -- 'STAR', 'RTRT', 'System Design', 'Case Study'
  title VARCHAR(255),
  content TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Job Applications Tracking

```sql
-- Job applications
CREATE TABLE job_applications (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  job_title VARCHAR(255) NOT NULL,
  company_name VARCHAR(255) NOT NULL,
  location VARCHAR(255),
  job_description TEXT,
  application_date DATE NOT NULL,
  source VARCHAR(100), -- 'linkedin', 'indeed', 'company_site', 'referral', 'manual'
  source_url TEXT,
  salary_range_min INT,
  salary_range_max INT,
  currency VARCHAR(10), -- 'USD', 'INR', etc
  contact_person_name VARCHAR(255),
  contact_person_email VARCHAR(255),
  contact_person_phone VARCHAR(20),
  company_website TEXT,
  status VARCHAR(50), -- See status list
  current_stage VARCHAR(50), -- 'applied', 'screening', 'technical', 'final', 'offer'
  status_updated_at TIMESTAMP,
  estimated_decision_date DATE,
  notes TEXT,
  tags JSON, -- Array of tags for filtering
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Application status: applied, under_review, phone_screen_scheduled, phone_screen_completed, 
-- technical_scheduled, technical_completed, final_scheduled, final_completed, 
-- offer_received, offer_negotiating, accepted, rejected, ghosted

CREATE INDEX idx_job_applications_user_id ON job_applications(user_id);
CREATE INDEX idx_job_applications_status ON job_applications(status);
CREATE INDEX idx_job_applications_company ON job_applications(company_name);
CREATE INDEX idx_job_applications_date ON job_applications(application_date);

-- Application status history
CREATE TABLE application_status_history (
  id UUID PRIMARY KEY,
  application_id UUID NOT NULL REFERENCES job_applications(id) ON DELETE CASCADE,
  old_status VARCHAR(50),
  new_status VARCHAR(50),
  changed_at TIMESTAMP DEFAULT NOW(),
  changed_by_user_id UUID REFERENCES users(id),
  notes TEXT
);

-- Interview schedule for applications
CREATE TABLE interview_schedules (
  id UUID PRIMARY KEY,
  application_id UUID NOT NULL REFERENCES job_applications(id) ON DELETE CASCADE,
  interview_round INT, -- 1, 2, 3 etc
  interview_type VARCHAR(50), -- 'phone_screen', 'technical', 'behavioral', 'final'
  scheduled_for TIMESTAMP NOT NULL,
  duration_minutes INT,
  interviewer_name VARCHAR(255),
  interviewer_email VARCHAR(255),
  interview_format VARCHAR(50), -- 'phone', 'video', 'in_person', 'async'
  video_link TEXT,
  location VARCHAR(255), -- For in-person
  meeting_platform VARCHAR(100), -- 'zoom', 'teams', 'google_meet'
  calendar_event_id VARCHAR(255), -- Google Calendar ID
  status VARCHAR(50), -- 'scheduled', 'in_progress', 'completed', 'cancelled'
  reminder_sent_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_interview_schedules_application ON interview_schedules(application_id);
CREATE INDEX idx_interview_schedules_scheduled_for ON interview_schedules(scheduled_for);

-- Communication log
CREATE TABLE communications (
  id UUID PRIMARY KEY,
  application_id UUID NOT NULL REFERENCES job_applications(id) ON DELETE CASCADE,
  communication_date TIMESTAMP NOT NULL,
  communication_type VARCHAR(50), -- 'email', 'phone_call', 'linkedin_message', 'in_person', 'note'
  subject VARCHAR(255),
  message_body TEXT,
  from_email VARCHAR(255),
  to_email VARCHAR(255),
  direction VARCHAR(10), -- 'sent', 'received'
  sender_name VARCHAR(255),
  recipient_name VARCHAR(255),
  attachment_urls JSON,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_communications_application ON communications(application_id);
CREATE INDEX idx_communications_date ON communications(communication_date);

-- Interview notes
CREATE TABLE interview_notes (
  id UUID PRIMARY KEY,
  interview_schedule_id UUID REFERENCES interview_schedules(id) ON DELETE SET NULL,
  application_id UUID NOT NULL REFERENCES job_applications(id) ON DELETE CASCADE,
  pre_interview_notes TEXT,
  company_research_notes TEXT,
  topics_discussed TEXT,
  interviewer_feedback TEXT,
  interviewer_name VARCHAR(255),
  candidate_interest_level INT, -- 1-10
  interviewer_impression INT, -- 1-10
  salary_discussed INT,
  next_steps TEXT,
  follow_up_date DATE,
  decision_expected_date DATE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_interview_notes_application ON interview_notes(application_id);
```

### Job Offers & Career Roadmap

```sql
-- Job offers received
CREATE TABLE job_offers (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  application_id UUID REFERENCES job_applications(id),
  job_title VARCHAR(255),
  company_name VARCHAR(255),
  salary INT,
  currency VARCHAR(10),
  signing_bonus INT,
  equity_percentage DECIMAL(5,3),
  equity_type VARCHAR(50), -- 'stock_options', 'rsu'
  benefits JSON, -- {health_insurance, 401k, pto_days, etc}
  start_date DATE,
  offer_expires_at DATE,
  status VARCHAR(50), -- 'pending', 'negotiating', 'accepted', 'rejected'
  base_offer_letter TEXT,
  received_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Career roadmap
CREATE TABLE career_roadmaps (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  current_role VARCHAR(255),
  current_experience_years DECIMAL(4,1),
  target_role VARCHAR(255),
  roadmap_horizon_years INT, -- 1, 3, 5
  preferred_path VARCHAR(50), -- 'technical', 'leadership', 'specialist', 'entrepreneur'
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Career milestones/checkpoints
CREATE TABLE career_milestones (
  id UUID PRIMARY KEY,
  roadmap_id UUID NOT NULL REFERENCES career_roadmaps(id) ON DELETE CASCADE,
  milestone_year INT, -- 1, 3, 5
  target_role VARCHAR(255),
  target_salary INT,
  target_company VARCHAR(255),
  target_location VARCHAR(255),
  required_skills JSON,
  required_certifications JSON,
  required_experience_years INT,
  status VARCHAR(50), -- 'not_started', 'in_progress', 'achieved'
  achieved_date DATE
);
```

---

## 🔌 API Endpoints

### Authentication
```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh-token
POST /api/v1/auth/logout
POST /api/v1/auth/forgot-password
POST /api/v1/auth/reset-password
```

### User Profile
```
GET /api/v1/users/me
PUT /api/v1/users/me
GET /api/v1/users/:id
DELETE /api/v1/users/:id
PUT /api/v1/users/me/preferences
```

### Resume Management
```
GET /api/v1/resumes
GET /api/v1/resumes/:id
POST /api/v1/resumes
PUT /api/v1/resumes/:id
DELETE /api/v1/resumes/:id
POST /api/v1/resumes/:id/analyze
GET /api/v1/resumes/:id/versions
GET /api/v1/resumes/:id/versions/:versionId
POST /api/v1/resumes/:id/versions/:versionId/restore
GET /api/v1/resumes/:id/issues
POST /api/v1/resumes/:id/export (pdf/docx)
GET /api/v1/resumes/:id/compare/:otherId
```

### Skills & Learning
```
GET /api/v1/skills
GET /api/v1/skills/:id
GET /api/v1/skills/search?q=python
GET /api/v1/user-skills
POST /api/v1/user-skills
PUT /api/v1/user-skills/:id
DELETE /api/v1/user-skills/:id
GET /api/v1/learning-paths
POST /api/v1/learning-paths
PUT /api/v1/learning-paths/:id
GET /api/v1/learning-paths/:id/steps
PUT /api/v1/learning-paths/:id/steps/:stepId
GET /api/v1/courses?skill=python&platform=udemy
POST /api/v1/user-certifications
GET /api/v1/user-certifications
```

### Interview Preparation
```
GET /api/v1/interview-questions?job=Data%20Scientist&difficulty=hard
GET /api/v1/interview-questions/:id
POST /api/v1/mock-interviews
GET /api/v1/mock-interviews
GET /api/v1/mock-interviews/:id
GET /api/v1/mock-interviews/:id/scores
POST /api/v1/mock-interviews/:id/submit-response
GET /api/v1/interview-frameworks
POST /api/v1/interview-frameworks
```

### Job Applications
```
GET /api/v1/applications
POST /api/v1/applications
GET /api/v1/applications/:id
PUT /api/v1/applications/:id
DELETE /api/v1/applications/:id
PUT /api/v1/applications/:id/status (change status)
GET /api/v1/applications/:id/communications
POST /api/v1/applications/:id/communications
GET /api/v1/applications/:id/interviews
POST /api/v1/applications/:id/interviews (schedule)
GET /api/v1/applications/analytics (dashboard stats)
POST /api/v1/applications/bulk-import
```

### Job Offers
```
GET /api/v1/offers
POST /api/v1/offers
GET /api/v1/offers/:id
PUT /api/v1/offers/:id/compare/:otherId
POST /api/v1/offers/:id/accept
POST /api/v1/offers/:id/reject
```

### Career Roadmap
```
GET /api/v1/career-roadmaps
POST /api/v1/career-roadmaps
GET /api/v1/career-roadmaps/:id
PUT /api/v1/career-roadmaps/:id
GET /api/v1/career-roadmaps/:id/milestones
POST /api/v1/career-roadmaps/:id/milestones
```

---

## 🗂️ File Storage Structure (S3/Cloud)

```
s3://resumeiq-storage/
├── resumes/
│   ├── {user_id}/
│   │   ├── {resume_id}/
│   │   │   ├── original.pdf
│   │   │   ├── versions/
│   │   │   │   ├── v1.json
│   │   │   │   ├── v2.json
│   │   │   │   └── v{n}.json
│   │   │   └── exports/
│   │   │       ├── {timestamp}.pdf
│   │   │       └── {timestamp}.docx
│   │   └── ...
├── mock-interviews/
│   ├── {user_id}/
│   │   ├── {interview_id}/
│   │   │   ├── {question_id}_response.webm
│   │   │   ├── transcript.txt
│   │   │   └── analysis.json
│   │   └── ...
├── certificates/
│   ├── {user_id}/
│   │   ├── {cert_id}.pdf
│   │   └── ...
├── portfolio/
│   ├── {user_id}/
│   │   ├── projects/
│   │   │   ├── {project_id}/
│   │   │   │   ├── images/
│   │   │   │   ├── videos/
│   │   │   │   └── data.json
│   │   └── ...
└── temp/
    └── uploads/ (auto-cleaned after 24hrs)
```

---

## 🔐 Security Considerations

```javascript
// Encryption for sensitive data
- Resume content: AES-256-GCM
- Salary information: AES-256-GCM
- Application credentials: AES-256-GCM

// Access control
- Users can only view their own data
- Recruiters have different permissions (Phase 3)
- API rate limiting: 1000 requests/hour per user
- CORS only for trusted domains

// Authentication
- JWT with 1-hour expiry
- Refresh tokens with 30-day expiry
- 2FA optional for premium users
- OAuth2 for Google/LinkedIn login

// Data retention
- Resume versions: 5 years
- Application history: 3 years
- Mock interview videos: 6 months
- Soft deletes for user privacy
```

---

## 📊 Indexing Strategy

```sql
-- High-priority indexes for performance
CREATE INDEX idx_resumes_user_created ON resumes(user_id, created_at DESC);
CREATE INDEX idx_applications_user_status_date ON job_applications(user_id, status, application_date DESC);
CREATE INDEX idx_user_skills_user_verified ON user_skills(user_id, verified);
CREATE INDEX idx_interview_questions_type_difficulty ON interview_questions(question_type, difficulty);
CREATE INDEX idx_mock_interviews_user_created ON mock_interviews(user_id, created_at DESC);

-- Aggregate functions for analytics
CREATE MATERIALIZED VIEW application_funnel_stats AS
SELECT 
  user_id,
  COUNT(*) as total_applications,
  COUNT(CASE WHEN status='applied' THEN 1 END) as applied_count,
  COUNT(CASE WHEN status IN ('offer_received','accepted') THEN 1 END) as offer_count,
  ROUND(100.0 * COUNT(CASE WHEN status='accepted' THEN 1 END) / NULLIF(COUNT(*),0), 2) as conversion_rate
FROM job_applications
GROUP BY user_id;
```

---

## 🔄 Data Sync & Real-time Updates

```javascript
// WebSocket events for real-time updates
- resume:updated (when resume content changes)
- application:status_changed (when status updates)
- interview:scheduled (when interview scheduled)
- offer:received (when offer arrives)
- skill:verified (when skill endorsement received)

// Polling fallback for non-WebSocket clients
- Poll every 30 seconds for application updates
- Poll every 5 minutes for new job matches
```

---

## 📈 Monitoring & Analytics

```javascript
// Key metrics to track
- User DAU/MAU
- Resume editor usage (sessions, edits)
- Learning path completion rate
- Mock interview completion rate
- Application tracking adoption
- Premium conversion funnel
- API response times
- Error rates
- Database query times
- File storage usage

// Tools
- Datadog for monitoring
- Segment for analytics
- Sentry for error tracking
- New Relic for APM
```

---

## 🚀 Performance Targets

```
Page Load Times:
- Resume Editor: < 1.5s
- Job Applications: < 1s
- Learning Dashboard: < 2s
- Interview Prep: < 1.5s

API Response Times:
- GET requests: < 200ms
- POST requests: < 500ms
- Search queries: < 1s
- File uploads: < 2s

Database:
- Query execution: < 100ms (95th percentile)
- Connection pool: 20-50 connections
- Read replica lag: < 1s

Storage:
- File upload: < 5MB/second
- Maximum file size: 25MB per resume
- Video storage: 100GB per user cap
```

---

**This technical reference is your development blueprint. Use it with the Master Prompt for complete implementation guidance.**
