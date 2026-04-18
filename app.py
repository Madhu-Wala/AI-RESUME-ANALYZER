from flask import Flask, render_template, request, redirect, session
import os

from services.google.google_fetch import fetch_resumes,get_file_id
from services.nlp.parser import extract_text
from services.nlp.extractor import extract_skills
from services.nlp.scorer import compute_score

from services.llm.summarizer import summarize_resume
from services.llm.explanation import generate_explanation
from services.llm.chatbot import ask_candidate_question

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from models import db, User, Job, Candidate
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

# DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ats.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# OAuth
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/userinfo.email"
]

# ================= AUTH =================

@app.route("/login")
def login():
    flow = Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=SCOPES,
        redirect_uri="http://127.0.0.1:5000/callback"
    )

    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    session["state"] = state
    session["code_verifier"] = flow.code_verifier

    return redirect(auth_url)


@app.route("/callback")
def callback():
    flow = Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=SCOPES,
        state=session["state"],
        redirect_uri="http://127.0.0.1:5000/callback"
    )

    flow.code_verifier = session["code_verifier"]
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    session["credentials"] = credentials_to_dict(credentials)

    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()

    email = user_info["email"]
    session["user_email"] = email

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id

    return redirect("/dashboard")

@app.route("/refresh/<int:job_id>")
def refresh(job_id):
    if "user_id" not in session:
        return redirect("/login")

    job = Job.query.get(job_id)
    if not job:
        return "Job not found"

    rows = fetch_resumes(job.sheet_url, session.get("credentials")) or []

    # ✅ prevent duplicates using resume_link
    existing_links = [
        c.resume_link for c in Candidate.query.filter_by(job_id=job_id).all()
    ]

    jd_skills = extract_skills(job.jd)

    for row in rows:
        name = row.get(job.name_column, "Unknown")
        email = row.get(job.email_column, "N/A")
        phone = row.get(job.phone_column, "N/A")

        raw_link = row.get(job.resume_column, "")
        resume_link = ""

        if raw_link:
            try:
                file_id = get_file_id(raw_link)
                resume_link = f"https://drive.google.com/file/d/{file_id}/view"
            except:
                resume_link = raw_link

        # 🚫 skip duplicates
        if resume_link in existing_links:
            continue

        # match resume file
        file_name = None
        for f in os.listdir("resumes"):
            if name.lower().split()[0] in f.lower():
                file_name = f
                break

        if not file_name:
            continue

        path = os.path.join("resumes", file_name)

        try:
            text = extract_text(path)
        except:
            continue

        skills = extract_skills(text)
        score = compute_score(text, job.jd, skills, jd_skills)

        candidate = Candidate(
            name=name,
            email=email,
            phone=phone,
            score=score,
            resume_file=file_name,
            resume_link=resume_link,
            resume_text=text,
            job_id=job_id
        )

        db.session.add(candidate)

    db.session.commit()

    return redirect(f"/job/{job_id}")
def credentials_to_dict(creds):
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

# ================= NLP =================

def process_resumes(jd_text):
    jd_skills = extract_skills(jd_text)
    results = []

    files = os.listdir("resumes")

    for file in files:
        path = os.path.join("resumes", file)

        try:
            text = extract_text(path)
        except:
            continue  # skip broken files

        skills = extract_skills(text)

        score = compute_score(text, jd_text, skills, jd_skills)
        missing = list(set(jd_skills) - set(skills))

        results.append({
            "file": file,
            "score": score,
            "skills": skills,
            "missing": missing
        })

    # ✅ always sorted
    return sorted(results, key=lambda x: x["score"], reverse=True)
# ================= ROUTES =================

@app.route("/", methods=["GET", "POST"])
def index():
    user_id = session.get("user_id")

    if not user_id:
        return render_template("landing.html")

    if request.method == "POST":
        job_title = request.form["job_title"]
        sheet_url = request.form["sheet_url"]
        jd_text = request.form["jd"]

        name_col = request.form["name_column"]
        email_col = request.form["email_column"]
        phone_col = request.form["phone_column"]
        resume_col = request.form["resume_column"]

        rows = fetch_resumes(sheet_url, session.get("credentials")) or []

        # create job
        job = Job(
            title=job_title,
            sheet_url=sheet_url,
            jd=jd_text,
            name_column=name_col,
            email_column=email_col,
            phone_column=phone_col,
            resume_column=resume_col,
            user_id=session["user_id"]
        )
        db.session.add(job)
        db.session.commit()

        jd_skills = extract_skills(jd_text)

        for row in rows:
            name = row.get(name_col, "Unknown Candidate")
            email = row.get(email_col, "Not Provided")
            phone = row.get(phone_col, "Not Provided")

            raw_link = row.get(resume_col, "")
            resume_link = ""

            if raw_link:
                try:
                    file_id = get_file_id(raw_link)
                    resume_link = f"https://drive.google.com/file/d/{file_id}/view"
                except:
                    resume_link = raw_link

            # match resume file (fuzzy)
            file_name = None
            for f in os.listdir("resumes"):
                if name.lower().split()[0] in f.lower():
                    file_name = f
                    break

            if not file_name:
                continue

            path = os.path.join("resumes", file_name)

            try:
                text = extract_text(path)
            except:
                continue

            skills = extract_skills(text)
            score = compute_score(text, jd_text, skills, jd_skills)

            candidate = Candidate(
                name=name,
                email=email,
                phone=phone,
                score=score,
                resume_file=file_name,
                resume_link=resume_link,
                resume_text=text,
                job_id=job.id
            )

            db.session.add(candidate)

        db.session.commit()

        return redirect(f"/job/{job.id}")

    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    jobs = Job.query.filter_by(user_id=session["user_id"]).all()
    return render_template("dashboard.html", jobs=jobs)


@app.route("/job/<int:id>")
def job(id):
    job = Job.query.get(id)
    if not job:
        return "Job not found"

    candidates = Candidate.query.filter_by(job_id=id)\
        .order_by(Candidate.score.desc())\
        .all()

    return render_template("job.html", candidates=candidates, job=job)

@app.route("/candidate/<int:id>")
def candidate(id):
    candidate = Candidate.query.get(id)
    return render_template("candidate.html", candidate=candidate)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/delete_job/<int:job_id>")
def delete_job(job_id):
    if "user_id" not in session:
        return redirect("/login")

    job = Job.query.get(job_id)

    if job and job.user_id == session["user_id"]:
        Candidate.query.filter_by(job_id=job.id).delete()
        db.session.delete(job)
        db.session.commit()

    return redirect("/dashboard")

#llm routes
@app.route("/summary/<int:id>")
def summary(id):
    if "user_id" not in session:
        return "Unauthorized"

    candidate = Candidate.query.get(id)
    if not candidate:
        return "Candidate not found"

    try:
       
        if candidate.resume_text:
            resume_text = candidate.resume_text
        else:
            resume_path = os.path.join("resumes", candidate.resume_file)

            if not os.path.exists(resume_path):
                return "Resume file not found"

            resume_text = extract_text(resume_path)
            candidate.resume_text = resume_text
            db.session.commit()

        result = summarize_resume(resume_text)

        return result

    except Exception as e:
        return f"Error generating summary: {str(e)}"
    
@app.route("/explain/<int:id>")
def explain(id):
    if "user_id" not in session:
        return "Unauthorized"

    candidate = Candidate.query.get(id)
    if not candidate:
        return "Candidate not found"

    job = Job.query.get(candidate.job_id)
    if not job:
        return "Job not found"

    try:
        
        if candidate.resume_text:
            resume_text = candidate.resume_text
        else:
            resume_path = os.path.join("resumes", candidate.resume_file)

            if not os.path.exists(resume_path):
                return "Resume file not found"

            resume_text = extract_text(resume_path)
            candidate.resume_text = resume_text
            db.session.commit()
        
        jd_text = job.jd
        score = candidate.score

        result = generate_explanation(resume_text, jd_text, score)

        return result

    except Exception as e:
        return f"Error generating explanation: {str(e)}"
    
@app.route("/ask/<int:id>", methods=["POST"])
def ask(id):
    if "user_id" not in session:
        return "Unauthorized"

    candidate = Candidate.query.get(id)
    if not candidate:
        return "Candidate not found"

    job = Job.query.get(candidate.job_id)
    if not job:
        return "Job not found"

    question = request.form.get("question")

    if not question or question.strip() == "":
        return "Please enter a question"

    try:
        

        if candidate.resume_text:
            resume_text = candidate.resume_text
        else:
            resume_path = os.path.join("resumes", candidate.resume_file)

            if not os.path.exists(resume_path):
                return "Resume file not found"

            resume_text = extract_text(resume_path)

            # 🔥 SAVE it so next time it's fast
            candidate.resume_text = resume_text
            db.session.commit()

        jd_text = job.jd
        score = candidate.score

        result = ask_candidate_question(
            resume_text,
            jd_text,
            score,
            question
        )

        return result

    except Exception as e:
        return f"Error getting response: {str(e)}"
    

if __name__ == "__main__":
    app.run(debug=True)