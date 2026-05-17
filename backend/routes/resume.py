from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from app import db
from models import Resume, MatchResult, JobDescription
from utils.parser import ResumeParser
from utils.skills import SkillsExtractor
from utils.scorer import ResumeScorer

resume_bp = Blueprint('resume', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@resume_bp.route('/upload', methods=['POST'])
def upload_resume():
    """Upload and parse a resume"""
    try:
        if 'file' not in request.files:
            return {'error': 'No file provided'}, 400
        
        file = request.files['file']
        
        if file.filename == '':
            return {'error': 'No file selected'}, 400
        
        if not allowed_file(file.filename):
            return {'error': 'File type not allowed'}, 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)
        
        # Parse resume
        raw_text = ResumeParser.parse_file(filepath)
        contact_info = ResumeParser.extract_contact_info(raw_text)
        skills_data = SkillsExtractor.extract_skills(raw_text)
        years_exp = SkillsExtractor.extract_years_of_experience(raw_text)
        
        # Score resume
        resume_data = {
            'raw_text': raw_text,
            'contact_info': contact_info,
            'skills': skills_data['all_skills'],
            'years_of_experience': years_exp,
            'education': []
        }
        score_data = ResumeScorer.calculate_score(resume_data)
        
        # Save to database
        resume = Resume(
            filename=filename,
            file_path=filepath,
            raw_text=raw_text,
            full_name=contact_info.get('name'),
            email=contact_info.get('email'),
            phone=contact_info.get('phone'),
            skills=skills_data['all_skills'],
            technical_skills=skills_data['technical_skills'],
            soft_skills=skills_data['soft_skills'],
            years_of_experience=years_exp,
            score=score_data['overall_score'],
            score_breakdown=score_data['breakdown']
        )
        db.session.add(resume)
        db.session.commit()
        
        return {
            'id': resume.id,
            'filename': resume.filename,
            'contact_info': contact_info,
            'skills': skills_data,
            'years_of_experience': years_exp,
            'score': score_data
        }, 201
    
    except Exception as e:
        return {'error': str(e)}, 500

@resume_bp.route('/<int:resume_id>', methods=['GET'])
def get_resume(resume_id):
    """Get resume analysis"""
    try:
        resume = Resume.query.get(resume_id)
        
        if not resume:
            return {'error': 'Resume not found'}, 404
        
        return {
            'id': resume.id,
            'filename': resume.filename,
            'full_name': resume.full_name,
            'email': resume.email,
            'phone': resume.phone,
            'skills': resume.skills,
            'technical_skills': resume.technical_skills,
            'soft_skills': resume.soft_skills,
            'years_of_experience': resume.years_of_experience,
            'score': resume.score,
            'score_breakdown': resume.score_breakdown,
            'created_at': resume.created_at.isoformat()
        }, 200
    
    except Exception as e:
        return {'error': str(e)}, 500

@resume_bp.route('/match', methods=['POST'])
def match_job():
    """Match resume against job description"""
    try:
        data = request.get_json()
        resume_id = data.get('resume_id')
        job_id = data.get('job_id')
        
        resume = Resume.query.get(resume_id)
        job = JobDescription.query.get(job_id)
        
        if not resume or not job:
            return {'error': 'Resume or job not found'}, 404
        
        # Calculate match score
        resume_skills = set(resume.skills or [])
        job_skills = set(job.required_skills or [])
        preferred_skills = set(job.preferred_skills or [])
        
        matched_required = resume_skills & job_skills
        matched_preferred = resume_skills & preferred_skills
        missing_skills = job_skills - resume_skills
        
        skills_match = (len(matched_required) / len(job_skills) * 100) if job_skills else 100
        
        experience_match = min(100, (resume.years_of_experience / max(job.years_required or 1, 1)) * 100)
        
        match_score = (skills_match * 0.6 + experience_match * 0.4)
        
        result = MatchResult(
            resume_id=resume_id,
            job_id=job_id,
            match_score=round(match_score, 2),
            skills_match=round(skills_match, 2),
            experience_match=round(experience_match, 2),
            matched_skills=list(matched_required),
            missing_skills=list(missing_skills),
            recommendations=[]
        )
        
        db.session.add(result)
        db.session.commit()
        
        return {
            'match_result': {
                'id': result.id,
                'match_score': result.match_score,
                'skills_match': result.skills_match,
                'experience_match': result.experience_match,
                'matched_skills': result.matched_skills,
                'missing_skills': result.missing_skills
            }
        }, 201
    
    except Exception as e:
        return {'error': str(e)}, 500