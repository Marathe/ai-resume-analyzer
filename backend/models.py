from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Resume(db.Model):
    """Resume model for storing parsed resume data"""
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    raw_text = db.Column(db.Text, nullable=False)
    
    # Extracted information
    full_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(255))
    summary = db.Column(db.Text)
    
    # Skills
    skills = db.Column(db.JSON)
    technical_skills = db.Column(db.JSON)
    soft_skills = db.Column(db.JSON)
    
    # Experience
    years_of_experience = db.Column(db.Float)
    experiences = db.Column(db.JSON)
    education = db.Column(db.JSON)
    
    # Score
    score = db.Column(db.Float, default=0.0)
    score_breakdown = db.Column(db.JSON)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Resume {self.id}: {self.filename}>'

class JobDescription(db.Model):
    """Job description model for job matching"""
    __tablename__ = 'job_descriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255))
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.JSON)
    preferred_skills = db.Column(db.JSON)
    years_required = db.Column(db.Float)
    location = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<JobDescription {self.id}: {self.title}>'

class MatchResult(db.Model):
    """Resume-Job match result model"""
    __tablename__ = 'match_results'
    
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_descriptions.id'), nullable=False)
    
    match_score = db.Column(db.Float, nullable=False)
    skills_match = db.Column(db.Float)
    experience_match = db.Column(db.Float)
    education_match = db.Column(db.Float)
    
    matched_skills = db.Column(db.JSON)
    missing_skills = db.Column(db.JSON)
    recommendations = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    resume = db.relationship('Resume', backref='matches')
    job = db.relationship('JobDescription', backref='matches')
    
    def __repr__(self):
        return f'<MatchResult {self.id}: Resume {self.resume_id} - Job {self.job_id}>'