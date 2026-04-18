from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    sheet_url = db.Column(db.Text)
    jd = db.Column(db.Text)
    name_column = db.Column(db.String(100))
    resume_column = db.Column(db.String(100))
    email_column = db.Column(db.String(100))
    phone_column = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    score = db.Column(db.Float)
    resume_file = db.Column(db.String(200))
    resume_link = db.Column(db.String(500)) 
    resume_text = db.Column(db.Text)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))