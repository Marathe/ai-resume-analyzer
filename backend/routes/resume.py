from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import io
import re
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from app import db
from models import Resume, MatchResult, JobDescription
from utils.parser import ResumeParser
from utils.skills import SkillsExtractor
from utils.scorer import ResumeScorer

resume_bp = Blueprint('resume', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
UPLOAD_FOLDER = 'uploads'

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@resume_bp.route('/upload', methods=['POST'])
def upload_resume():
    """Upload and parse a resume"""
    try:
        # Validate request
        if 'file' not in request.files:
            return {'error': 'No file provided'}, 400

        file = request.files['file']

        if file.filename == '':
            return {'error': 'No file selected'}, 400

        if not allowed_file(file.filename):
            return {'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}, 400

        # Create secure filename and full path
        filename = secure_filename(file.filename)
        # Add timestamp to avoid filename collisions
        import time
        filename = f"{int(time.time())}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)

        # Save file
        file.save(filepath)

        # Verify file was saved
        if not os.path.exists(filepath):
            return {'error': 'File upload failed - could not save file'}, 500

        # Parse resume
        raw_text = ResumeParser.parse_file(filepath)

        if not raw_text or len(raw_text.strip()) < 50:
            os.remove(filepath)  # Clean up empty file
            return {'error': 'Could not extract text from file. Ensure it is a valid resume.'}, 400

        # Extract information
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
            full_name=contact_info.get('name') or 'Unknown',
            email=contact_info.get('email'),
            phone=contact_info.get('phone'),
            skills=skills_data['all_skills'],
            technical_skills=skills_data['technical_skills'],
            soft_skills=skills_data['soft_skills'],
            years_of_experience=years_exp,
            score=score_data.get('overall_score', 0),
            score_breakdown=score_data.get('breakdown', {})
        )
        db.session.add(resume)
        db.session.commit()

        return {
            'success': True,
            'id': resume.id,
            'filename': resume.filename,
            'contact_info': contact_info,
            'skills': skills_data,
            'years_of_experience': years_exp,
            'score': score_data
        }, 201

    except FileNotFoundError as e:
        return {'error': f'File not found: {str(e)}'}, 400
    except ValueError as e:
        return {'error': f'Invalid file format: {str(e)}'}, 400
    except Exception as e:
        # Rollback database changes
        db.session.rollback()
        return {'error': f'Resume upload failed: {str(e)}'}, 500


@resume_bp.route('/batch-analyze', methods=['POST'])
def batch_analyze_resumes():
    """Bulk upload resumes and analyze against a job description."""
    try:
        files = request.files.getlist('files')
        job_title = request.form.get('job_title', 'Target Role')
        job_description = request.form.get('job_description', '')
        company = request.form.get('company', 'Unknown Company')

        if not files:
            return {'error': 'At least one resume file is required'}, 400
        if not job_description:
            return {'error': 'job_description is required'}, 400

        jd_skills = SkillsExtractor.extract_skills(job_description)
        required_skills, skills_source = build_required_skills(job_title, job_description, jd_skills)
        critical_skills = infer_critical_skills(job_description, required_skills)

        candidates = []
        for file in files:
            if not file or file.filename == '':
                continue
            if not allowed_file(file.filename):
                continue

            resume, payload = ingest_uploaded_resume(file)
            candidate = build_candidate_analysis(
                resume,
                required_skills,
                job_title,
                job_description,
                critical_skills
            )
            candidates.append(candidate)

        if not candidates:
            return {'error': 'No valid resume files were uploaded'}, 400

        candidates.sort(key=lambda x: x['ranking_score'], reverse=True)
        for idx, candidate in enumerate(candidates, start=1):
            candidate['rank'] = idx
            candidate['shortlisted'] = candidate.get('shortlisting_status') == 'Shortlisted'

        shortlisted = [c for c in candidates if c['shortlisted']]
        top_candidate = candidates[0]
        recruiter_analytics = build_recruiter_analytics(candidates)

        response = {
            'success': True,
            'job': {
                'title': normalize_job_title(job_title),
                'company': company,
                'required_skills': sorted(list(required_skills)),
                'critical_skills': sorted(list(critical_skills)),
                'skills_source': skills_source
            },
            'batch_summary': {
                'total_candidates': len(candidates),
                'shortlisted_count': len(shortlisted),
                'average_match_score': recruiter_analytics['average_match_score'],
                'average_ats_score': recruiter_analytics['average_ats_score']
            },
            'candidate_leaderboard': candidates,
            'ai_shortlist': shortlisted,
            'top_candidate_recommendation': top_candidate,
            'comparison': {
                'skill_gap_comparison': [
                    {'candidate': c['candidate_name'], 'missing_skills_count': len(c['missing_skills'])}
                    for c in candidates
                ],
                'ats_comparison': [
                    {'candidate': c['candidate_name'], 'ats_score': c['ats_score']}
                    for c in candidates
                ],
                'experience_comparison': [
                    {'candidate': c['candidate_name'], 'experience_years': c['years_of_experience']}
                    for c in candidates
                ],
                'multi_candidate_radar': [
                    {
                        'candidate': c['candidate_name'],
                        'Skill Match': c['match_score'],
                        'ATS': c['ats_score'],
                        'Experience': c['experience_score'],
                        'Interview': c['interview_readiness_score'],
                        'Project': c['project_quality_score']
                    } for c in candidates[:6]
                ]
            },
            'recruiter_analytics_dashboard': recruiter_analytics
        }
        return response, 200
    except Exception as e:
        db.session.rollback()
        return {'error': f'Batch resume analysis failed: {str(e)}'}, 500


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
            'created_at': resume.created_at.isoformat() if resume.created_at else None
        }, 200

    except Exception as e:
        return {'error': f'Error retrieving resume: {str(e)}'}, 500


@resume_bp.route('/match', methods=['POST'])
def match_job():
    """Match resume against job description"""
    try:
        data = request.get_json()
        resume_id = data.get('resume_id')
        job_id = data.get('job_id')

        if not resume_id or not job_id:
            return {'error': 'resume_id and job_id are required'}, 400

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

        # Skills match percentage
        skills_match = (len(matched_required) / len(job_skills) * 100) if job_skills else 100

        # Experience match percentage
        years_required = max(job.years_required or 1, 1)
        experience_match = min(100, (resume.years_of_experience / years_required) * 100)

        # Weighted match score
        match_score = (skills_match * 0.6 + experience_match * 0.4)

        # Create match result
        result = MatchResult(
            resume_id=resume_id,
            job_id=job_id,
            match_score=round(match_score, 2),
            skills_match=round(skills_match, 2),
            experience_match=round(experience_match, 2),
            matched_skills=list(matched_required),
            missing_skills=list(missing_skills),
            recommendations=generate_recommendations(missing_skills, resume.years_of_experience, years_required)
        )

        db.session.add(result)
        db.session.commit()

        return {
            'success': True,
            'match_result': {
                'id': result.id,
                'match_score': result.match_score,
                'skills_match': result.skills_match,
                'experience_match': result.experience_match,
                'matched_skills': result.matched_skills,
                'missing_skills': result.missing_skills,
                'recommendations': result.recommendations
            }
        }, 201

    except Exception as e:
        db.session.rollback()
        return {'error': f'Matching failed: {str(e)}'}, 500


@resume_bp.route('/analyze-job', methods=['POST'])
def analyze_job_intelligence():
    """Advanced AI-powered resume intelligence analysis"""
    try:
        data = request.get_json() or {}
        resume_id = data.get('resume_id')
        job_title = data.get('job_title', 'Target Role')
        company = data.get('company', 'Unknown Company')
        job_description = data.get('job_description', '')

        if not resume_id or not job_description:
            return {'error': 'resume_id and job_description are required'}, 400

        resume = Resume.query.get(resume_id)
        if not resume:
            return {'error': 'Resume not found'}, 404

        jd_skills = SkillsExtractor.extract_skills(job_description)
        required_skills, skills_source = build_required_skills(job_title, job_description, jd_skills)
        preferred_skills = set(jd_skills.get('soft_skills', []))
        resume_skills = set(resume.technical_skills or [])

        matched_required = sorted(list(resume_skills & required_skills))
        missing_skills = sorted(list(required_skills - resume_skills))
        match_score = round((len(matched_required) / max(1, len(required_skills))) * 100, 2)
        current_score = max(1.0, match_score)
        target_skills_for_full_match = missing_skills[:]

        learning_plan = build_learning_plan(missing_skills)
        career_insights = build_career_insights(resume, required_skills, missing_skills, match_score, job_title)
        visualization_data = build_visualization_data(resume, required_skills, missing_skills, career_insights)

        # Store normalized job + match result for traceability
        job = JobDescription(
            title=job_title,
            company=company,
            description=job_description,
            required_skills=sorted(list(required_skills)),
            preferred_skills=sorted(list(preferred_skills)),
            years_required=infer_years_required(job_description)
        )
        db.session.add(job)
        db.session.flush()

        result = MatchResult(
            resume_id=resume.id,
            job_id=job.id,
            match_score=match_score,
            skills_match=match_score,
            experience_match=career_insights['industry_readiness_score'],
            matched_skills=matched_required,
            missing_skills=missing_skills,
            recommendations=[item['learning_path'] for item in learning_plan[:5]]
        )
        db.session.add(result)
        db.session.commit()

        analysis = {
            'job': {
                'id': job.id,
                'title': job.title,
                'company': job.company
            },
            'match_result_id': result.id,
            'skills_gap_analysis': {
                'required_skills': sorted(list(required_skills)),
                'matched_skills': matched_required,
                'missing_skills': missing_skills,
                'match_score': current_score,
                'target_match_score': 100,
                'skills_needed_for_100_percent': target_skills_for_full_match,
                'skills_source': skills_source
            },
            'upskilling_engine': learning_plan,
            'career_insights': career_insights,
            'visualizations': visualization_data,
            'recommendations': generate_recommendations(set(missing_skills), resume.years_of_experience, job.years_required or 1)
        }

        return {'success': True, 'analysis': analysis}, 200
    except Exception as e:
        db.session.rollback()
        return {'error': f'Advanced analysis failed: {str(e)}'}, 500


@resume_bp.route('/report/<report_type>', methods=['POST'])
def generate_report(report_type):
    """Generate downloadable report as PDF"""
    try:
        data = request.get_json() or {}
        analysis = data.get('analysis')
        if not analysis:
            return {'error': 'analysis payload is required'}, 400

        valid_reports = {'resume-analysis', 'skill-gap', 'career-improvement'}
        if report_type not in valid_reports:
            return {'error': f'Invalid report_type. Use one of {", ".join(valid_reports)}'}, 400

        output = io.BytesIO()
        pdf = canvas.Canvas(output, pagesize=A4)
        width, height = A4
        y = height - 60

        lines = build_report_lines(report_type, analysis)
        for line in lines:
            if y < 60:
                pdf.showPage()
                y = height - 60
            pdf.setFont("Helvetica", 11)
            pdf.drawString(48, y, str(line)[:110])
            y -= 18

        pdf.save()
        output.seek(0)
        from flask import Response
        filename = f"{report_type}-report.pdf"
        return Response(
            output.read(),
            mimetype='application/pdf',
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    except Exception as e:
        return {'error': f'Report generation failed: {str(e)}'}, 500


def generate_recommendations(missing_skills, candidate_exp, required_exp):
    """Generate recommendations based on missing skills and experience"""
    recommendations = []

    if missing_skills:
        recommendations.append(f"Learn these skills: {', '.join(list(missing_skills)[:3])}")

    if candidate_exp < required_exp:
        gap = required_exp - candidate_exp
        recommendations.append(f"Gain {gap:.1f} more years of experience")

    return recommendations


def ingest_uploaded_resume(file):
    """Save uploaded file, parse, score and persist Resume."""
    filename = secure_filename(file.filename)
    import time
    filename = f"{int(time.time() * 1000)}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
    file.save(filepath)

    raw_text = ResumeParser.parse_file(filepath)
    if not raw_text or len(raw_text.strip()) < 50:
        if os.path.exists(filepath):
            os.remove(filepath)
        raise ValueError(f'Could not extract text from {filename}')

    contact_info = ResumeParser.extract_contact_info(raw_text)
    skills_data = SkillsExtractor.extract_skills(raw_text)
    years_exp = SkillsExtractor.extract_years_of_experience(raw_text)
    score_data = ResumeScorer.calculate_score({
        'raw_text': raw_text,
        'contact_info': contact_info,
        'skills': skills_data['all_skills'],
        'years_of_experience': years_exp,
        'education': []
    })

    resume = Resume(
        filename=filename,
        file_path=filepath,
        raw_text=raw_text,
        full_name=contact_info.get('name') or 'Unknown',
        email=contact_info.get('email'),
        phone=contact_info.get('phone'),
        skills=skills_data['all_skills'],
        technical_skills=skills_data['technical_skills'],
        soft_skills=skills_data['soft_skills'],
        years_of_experience=years_exp,
        score=score_data.get('overall_score', 0),
        score_breakdown=score_data.get('breakdown', {})
    )
    db.session.add(resume)
    db.session.flush()

    payload = {
        'contact_info': contact_info,
        'skills': skills_data,
        'years_of_experience': years_exp,
        'score': score_data
    }
    return resume, payload


def build_candidate_analysis(resume, required_skills, job_title, job_description, critical_skills=None):
    resume_skills = set(resume.technical_skills or [])
    required = set(required_skills or set())
    critical = set(critical_skills or set())
    matched_skills = sorted(list(resume_skills & required))
    missing_skills = sorted(list(required - resume_skills))
    match_score = round((len(matched_skills) / max(1, len(required))) * 100, 2)
    critical_missing = sorted(list(critical - resume_skills))

    years_required = infer_years_required(job_description)
    experience_score = round(min(100, (resume.years_of_experience or 0) / max(1.0, years_required) * 100), 2)
    career_insights = build_career_insights(resume, required, missing_skills, match_score, job_title)
    ats_score = career_insights.get('ats_compatibility_score', 0)
    ranking_score = round(match_score * 0.5 + ats_score * 0.25 + experience_score * 0.25, 2)
    learning_plan = build_learning_plan(missing_skills)
    recommended_technologies = [item.get('technology') for item in learning_plan[:5]]
    improvement_suggestions = career_insights.get('resume_weaknesses', [])[:]
    if missing_skills:
        improvement_suggestions.append(
            f"Focus on missing technologies: {', '.join(missing_skills[:3])}"
        )
    if match_score < 70:
        interview_status = 'Needs More Preparation'
    elif match_score < 85:
        interview_status = 'Recommended'
    else:
        interview_status = 'Strongly Recommended'

    shortlisting_status = get_shortlisting_status(match_score, critical_missing)

    return {
        'resume_id': resume.id,
        'candidate_name': resume.full_name or 'Unknown Candidate',
        'email': resume.email,
        'phone': resume.phone,
        'years_of_experience': round(resume.years_of_experience or 0, 1),
        'match_score': match_score,
        'ats_score': ats_score,
        'experience_score': experience_score,
        'ranking_score': ranking_score,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'critical_missing_skills': critical_missing,
        'recommended_technologies': recommended_technologies,
        'interview_readiness_score': career_insights.get('interview_readiness_score', 0),
        'interview_recommendation_status': interview_status,
        'shortlisting_status': shortlisting_status,
        'project_quality_score': career_insights.get('project_quality_score', 0),
        'strengths': career_insights.get('resume_strengths', []),
        'resume_strength': (career_insights.get('resume_strengths', ['Balanced profile'])[0]),
        'weaknesses': career_insights.get('resume_weaknesses', []),
        'improvement_suggestions': improvement_suggestions,
        'ai_upskilling_recommendations': learning_plan[:5]
    }


def build_recruiter_analytics(candidates):
    total = max(1, len(candidates))
    avg_match = round(sum(c['match_score'] for c in candidates) / total, 2)
    avg_ats = round(sum(c['ats_score'] for c in candidates) / total, 2)
    avg_exp = round(sum(c['years_of_experience'] for c in candidates) / total, 2)
    above_80 = len([c for c in candidates if c['match_score'] >= 80])

    skill_counter = {}
    for candidate in candidates:
        for skill in candidate.get('missing_skills', []):
            skill_counter[skill] = skill_counter.get(skill, 0) + 1

    common_gaps = sorted(
        [{'skill': skill, 'count': count} for skill, count in skill_counter.items()],
        key=lambda x: x['count'],
        reverse=True
    )[:8]

    return {
        'average_match_score': avg_match,
        'average_ats_score': avg_ats,
        'average_experience_years': avg_exp,
        'candidates_above_80_match': above_80,
        'common_skill_gaps': common_gaps
    }


def infer_critical_skills(job_description, required_skills):
    """Infer critical skills from must-have wording in JD."""
    if not job_description:
        return set(list(required_skills)[:3])

    text = job_description.lower()
    critical = set()
    critical_markers = ['must', 'mandatory', 'required', 'must-have', 'essential']
    for skill in required_skills:
        skill_lower = skill.lower()
        for marker in critical_markers:
            pattern = rf'{marker}[^.\n]{{0,80}}\b{re.escape(skill_lower)}\b|\b{re.escape(skill_lower)}\b[^.\n]{{0,80}}{marker}'
            if re.search(pattern, text):
                critical.add(skill)
                break

    if not critical:
        # fallback: treat top required skills as critical when JD is vague
        critical = set(list(sorted(required_skills))[:3])
    return critical


def get_shortlisting_status(match_score, critical_missing):
    """Mandatory skill filtering logic."""
    if critical_missing:
        return 'Not Shortlisted'
    if match_score >= 75:
        return 'Shortlisted'
    if match_score >= 45:
        return 'Needs Upskilling'
    return 'Not Shortlisted'


def infer_years_required(job_description):
    match = re.search(r'(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)', job_description or '', re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 2.0


def build_learning_plan(missing_skills):
    plan = []
    for idx, skill in enumerate(missing_skills):
        if idx < 3:
            priority, weeks, difficulty = 'High', 6 + idx, 'Advanced'
        elif idx < 7:
            priority, weeks, difficulty = 'Medium', 4 + (idx % 3), 'Intermediate'
        else:
            priority, weeks, difficulty = 'Low', 2 + (idx % 2), 'Beginner'

        plan.append({
            'technology': skill,
            'learning_priority': priority,
            'estimated_learning_time': f'{weeks} weeks',
            'difficulty_level': difficulty,
            'learning_path': f'Fundamentals -> Build 1 project using {skill} -> Mock interview prep'
        })
    return plan


def build_career_insights(resume, required_skills, missing_skills, match_score, job_title=''):
    years = resume.years_of_experience or 0
    ats_score = min(100, round((resume.score or 0) * 0.55 + match_score * 0.45, 2))
    industry_readiness = max(35, min(100, round(match_score * 0.5 + years * 6 + (resume.score or 0) * 0.2, 2)))
    interview_readiness = max(30, min(100, round((resume.score or 0) * 0.45 + (100 - len(missing_skills) * 5), 2)))
    project_quality = max(25, min(100, round((resume.score or 0) * 0.4 + len(resume.technical_skills or []) * 3.2, 2)))

    display_role = normalize_job_title(job_title) if job_title else infer_seniority_from_role_and_experience(job_title, years)

    salary_min = int(35000 + (years * 8500) + (match_score * 450))
    salary_max = salary_min + int(18000 + years * 2500)

    strengths = []
    weaknesses = []
    if len(resume.technical_skills or []) >= 10:
        strengths.append('Strong technical skill coverage across modern tools')
    else:
        weaknesses.append('Technical stack breadth can be improved')
    if years >= 3:
        strengths.append('Good professional experience depth for role progression')
    else:
        weaknesses.append('Hands-on experience depth appears limited for advanced roles')
    if match_score >= 70:
        strengths.append('Profile is well aligned with target job requirements')
    else:
        weaknesses.append('Noticeable job-skill mismatch against target role')
    if not strengths:
        strengths.append('Resume includes baseline skills and professional structure')
    if not weaknesses:
        weaknesses.append('Add role-specific achievements to improve competitiveness')

    return {
        'resume_strengths': strengths,
        'resume_weaknesses': weaknesses,
        'ats_compatibility_score': ats_score,
        'industry_readiness_score': industry_readiness,
        'seniority_detection': display_role,
        'experience_level': infer_seniority_from_role_and_experience(job_title, years),
        'salary_prediction': {
            'currency': 'USD',
            'min': salary_min,
            'max': salary_max,
            'confidence': 'Medium'
        },
        'interview_readiness_score': interview_readiness,
        'project_quality_score': project_quality
    }


def build_required_skills(job_title, job_description, jd_skills):
    """Build stronger required skills set from title + description."""
    required_skills = set(jd_skills.get('technical_skills', []))
    if required_skills:
        return required_skills, 'jd_extracted'

    text = f"{job_title or ''} {job_description or ''}".lower()
    title_lower = (job_title or '').lower()

    role_skill_map = {
        'team lead': {'Agile', 'Scrum', 'Jira', 'Git', 'REST API'},
        'tech lead': {'Architecture', 'Microservices', 'Git', 'CI/CD', 'REST API'},
        'frontend': {'JavaScript', 'TypeScript', 'React', 'HTML', 'CSS'},
        'backend': {'Python', 'SQL', 'REST API', 'Docker', 'PostgreSQL'},
        'full stack': {'JavaScript', 'React', 'Node.js', 'SQL', 'Git'},
        'data': {'Python', 'SQL', 'Pandas', 'NumPy'},
        'devops': {'Docker', 'Kubernetes', 'CI/CD', 'AWS', 'Terraform'},
    }

    for role_key, role_skills in role_skill_map.items():
        if role_key in title_lower:
            required_skills.update(role_skills)

    for skill in SkillsExtractor.TECHNICAL_SKILLS:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text):
            required_skills.add(skill)

    if required_skills:
        return required_skills, 'role_fallback'

    return {'Git', 'Agile', 'REST API'}, 'role_fallback'


def infer_seniority_from_role_and_experience(job_title, years):
    """Infer seniority with role/title weighting and experience guardrails."""
    title = (job_title or '').lower()
    senior_keywords = ['senior', 'lead', 'principal', 'architect', 'manager', 'head']
    mid_keywords = ['mid', 'intermediate', 'specialist']

    if any(word in title for word in senior_keywords):
        if years >= 6:
            return 'Senior'
        if years >= 3:
            return 'Mid'
        return 'Junior'

    if any(word in title for word in mid_keywords):
        if years >= 3:
            return 'Mid'
        return 'Junior'

    if years < 2:
        return 'Junior'
    if years < 6:
        return 'Mid'
    return 'Senior'


def normalize_job_title(job_title):
    """Return clean title-cased role text for dashboard display."""
    if not job_title:
        return 'Not Specified'
    title = re.sub(r'\s+', ' ', job_title).strip()
    return title.title()


def build_visualization_data(resume, required_skills, missing_skills, insights):
    match = max(1, 100 - (len(missing_skills) * 7))
    now = datetime.utcnow()
    trend = []
    for idx in range(6, 0, -1):
        point = max(35, min(98, match - (idx * 3) + (idx % 2) * 4))
        trend.append({
            'month': (now - timedelta(days=idx * 30)).strftime('%b'),
            'score': round(point, 1)
        })

    demand = []
    for skill in list(required_skills)[:8]:
        demand.append({
            'technology': skill,
            'demand_index': min(100, 60 + (len(skill) * 3) % 40)
        })

    progress = []
    for week in range(1, 9):
        progress.append({
            'week': f'W{week}',
            'completion': min(100, week * 12)
        })

    timeline = [
        {'stage': 'Profile Baseline', 'value': round((resume.score or 0), 1)},
        {'stage': 'ATS Upgrade', 'value': insights['ats_compatibility_score']},
        {'stage': 'Skill Completion', 'value': round(100 - len(missing_skills) * 5, 1)},
        {'stage': 'Interview Readiness', 'value': insights['interview_readiness_score']}
    ]

    heatmap = []
    for skill in list(required_skills)[:10]:
        heatmap.append({
            'skill': skill,
            'intensity': 90 if skill not in missing_skills else 35
        })

    radar = [
        {'metric': 'Skill Match', 'score': round(100 - len(missing_skills) * 8, 1)},
        {'metric': 'ATS Fit', 'score': insights['ats_compatibility_score']},
        {'metric': 'Industry Ready', 'score': insights['industry_readiness_score']},
        {'metric': 'Interview Ready', 'score': insights['interview_readiness_score']},
        {'metric': 'Project Quality', 'score': insights['project_quality_score']}
    ]

    return {
        'skill_match_radar': radar,
        'ats_score_doughnut': [
            {'name': 'ATS Score', 'value': insights['ats_compatibility_score']},
            {'name': 'Gap', 'value': max(0, 100 - insights['ats_compatibility_score'])}
        ],
        'resume_score_trend': trend,
        'technology_demand_graph': demand,
        'learning_progress_tracker': progress,
        'experience_timeline': timeline,
        'skill_heatmap': heatmap
    }


def build_report_lines(report_type, analysis):
    gap = analysis.get('skills_gap_analysis', {})
    insights = analysis.get('career_insights', {})
    upskill = analysis.get('upskilling_engine', [])

    header = {
        'resume-analysis': 'AI Resume Analysis Report',
        'skill-gap': 'Skill Gap Analysis Report',
        'career-improvement': 'Career Improvement Report'
    }.get(report_type, 'Resume Intelligence Report')

    lines = [
        header,
        'Enterprise Resume Intelligence Platform',
        f"Generated At: {datetime.utcnow().isoformat()} UTC",
        '',
        f"Resume Score: {round(insights.get('ats_compatibility_score', 0), 1)}",
        f"Skill Match Score: {round(gap.get('match_score', 0), 1)}",
        f"Industry Readiness: {round(insights.get('industry_readiness_score', 0), 1)}",
        '',
        'Missing Skills:',
    ]

    for skill in gap.get('missing_skills', [])[:12]:
        lines.append(f"- {skill}")
    lines.extend(['', 'AI Recommendations:'])

    for item in upskill[:8]:
        lines.append(
            f"- {item.get('technology')}: {item.get('learning_priority')} priority, "
            f"{item.get('estimated_learning_time')}, {item.get('difficulty_level')}"
        )

    lines.extend([
        '',
        'Learning Roadmap:',
    ])
    for item in upskill[:5]:
        lines.append(f"- {item.get('learning_path')}")
    return lines
