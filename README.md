# CourseGradePredictor (iGradeU)

## 📌 Overview
**CourseGradePredictor** (also called *iGradeU*) is an AI-powered academic foresight tool designed to reduce stress, uncertainty, and guesswork in education.  
Students often misjudge their abilities—some are overconfident and underprepare, while others struggle with imposter syndrome and underperform despite strong skills. Traditional feedback also comes too late, often only after exams or projects, leaving little room for improvement.  

Our solution provides **instant, personalized insights** by predicting a student’s likely grade in a course and identifying their strengths and growth areas.

---

## 🚀 How It Works
1. **Canvas API Integration**  
   - Securely pulls assignment weights, grades, and performance trends.  
   - Categorizes assignments into projects, exams, homework, and participation.  

2. **RateMyProfessor Insights**  
   - Adds external data on professor ratings, difficulty levels, and teaching style.  

3. **Syllabus Intelligence (NLP)**  
   - Uses OpenAI to parse syllabi and extract course expectations into standardized categories.  

4. **Predictive Modeling**  
   - Synthesizes Canvas data, RateMyProfessor ratings, and syllabus insights to forecast the student’s final grade.  

5. **Feedback Engine**  
   - Highlights individual strengths (e.g., strong exams) and weaknesses (e.g., project skills).  
   - Provides actionable recommendations to improve performance before it’s too late.  

---

## 🎯 Key Features
- **Instant Feedback**: Know where you stand right now, not weeks later.  
- **Reduced Uncertainty**: Eliminates “Am I good enough?” guesswork.  
- **Actionable Insights**: Breaks down performance across exams, projects, assignments, and participation.  
- **Personalized Coaching**: Feedback that reduces stress and boosts confidence.  

---

##  Team
- **Brian Jeong** – bjj46@pitt.edu  
- **Hannah Kim** – hak241@pitt.edu  
- **Steven Rodgers** - ser95@pitt.edu
- **Elizabeth O'Connell** - elo57@pitt.edu
- **Brett Dione** - brd149@pitt.edu
- **Arda Furtana** - arf112@pitt.edu

---

## 🛠️ Tech Stack
- **Backend**: Django + REST Framework  
- **Frontend**: React  
- **APIs**: Canvas API, RateMyProfessor API, OpenAI API  
- **Data Processing**: Python (pandas, requests, NLP via OpenAI)
- **DataBase** : Supabase

---

## 📈 Why It Matters
- **Confidence Gap**: Many students overestimate or underestimate their abilities, leading to poor preparation or unnecessary stress.  
- **Feedback Deficit**: Feedback often comes too late to make meaningful changes.  
- **Our Solution**: iGradeU bridges these gaps, turning raw academic data into clarity, confidence, and actionable strategies.

# 📌 CourseGradePredictor – Setup & Installation (Sprint 4)

## ✅ Requirements

| Component | Version |
|----------|----------|
| Python | 3.11+ recommended (3.9 works but throws OpenSSL warnings) |
| Node.js | 20.19+ (Vite will break on Node 18) |
| npm | 10+ |
| Django | 4.2.x |
| Supabase Python Client | latest |
| OpenAI | latest |
| Canvas API | active token |
| pip | 24+ |



---

## 🌎 Environment Variables

Create a `.env` file at the **root** (not in backend, not in frontend).

```env
# ==== BACKEND ====
OPENAI_API_KEY=sk-xxxxxxxxxxxx
CANVAS_API_URL=https://canvas.pitt.edu/api/v1
CANVAS_TOKEN=YOUR_CANVAS_PERSONAL_ACCESS_TOKEN

# ==== SUPABASE ====
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=YOUR_SUPABASE_SERVICE_ROLE_KEY   # DO NOT EXPOSE

# ==== DJANGO ====
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

```
---
## Backend setup
cd backend
python3 -m venv env
source env/bin/activate
pip install fastapi uvicorn openai pydantic numpy pandas scikit-learn
python3 manage.py migrate
python3 manage.py runserver
Runs at local host

---
## Frontend setup
cd frontend
nvm install 20
nvm use 20
npm install
npm run dev





