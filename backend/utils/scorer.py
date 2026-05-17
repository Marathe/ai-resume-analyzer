class ResumeScorer:
    """Score resume based on various criteria"""
    
    @staticmethod
    def calculate_score(resume_data):
        """Calculate overall resume score (0-100)"""
        weights = {
            'skills': 0.30,
            'experience': 0.25,
            'education': 0.20,
            'format': 0.15,
            'contact': 0.10
        }
        
        scores = {
            'skills': ResumeScorer._score_skills(resume_data.get('skills', [])),
            'experience': ResumeScorer._score_experience(resume_data.get('years_of_experience', 0)),
            'education': ResumeScorer._score_education(resume_data.get('education', [])),
            'format': ResumeScorer._score_format(resume_data.get('raw_text', '')),
            'contact': ResumeScorer._score_contact(resume_data.get('contact_info', {}))
        }
        
        overall_score = sum(scores[key] * weights[key] for key in scores)
        
        return {
            'overall_score': round(overall_score, 2),
            'breakdown': {key: round(scores[key], 2) for key in scores},
            'grade': ResumeScorer._get_grade(overall_score)
        }
    
    @staticmethod
    def _score_skills(skills):
        """Score based on number of skills (0-100)"""
        if not skills:
            return 0
        skill_count = len(skills)
        # 10+ skills = 100, 1 skill = 20, scale linearly
        return min(100, (skill_count * 10) + 10)
    
    @staticmethod
    def _score_experience(years):
        """Score based on years of experience (0-100)"""
        if years <= 0:
            return 10
        elif years < 1:
            return 20
        elif years < 2:
            return 40
        elif years < 5:
            return 60
        elif years < 10:
            return 80
        else:
            return 100
    
    @staticmethod
    def _score_education(education):
        """Score based on education credentials (0-100)"""
        if not education:
            return 20
        
        score = 20
        education_keywords = {
            'phd': 100,
            'master': 80,
            'bachelor': 60,
            'associate': 40,
            'certificate': 30,
            'diploma': 35
        }
        
        edu_text = str(education).lower()
        for keyword, value in education_keywords.items():
            if keyword in edu_text:
                score = max(score, value)
        
        return min(100, score)
    
    @staticmethod
    def _score_format(text):
        """Score based on resume format and structure (0-100)"""
        score = 50
        
        # Check for common section headers
        sections = ['experience', 'education', 'skills', 'summary', 'objective']
        section_count = sum(1 for section in sections if section.lower() in text.lower())
        score += (section_count * 10)
        
        # Check for bullet points
        if '•' in text or '-' in text or '*' in text:
            score += 10
        
        # Check for professional email
        if '@' in text and len(text.split('@')[0]) < 30:
            score += 5
        
        return min(100, score)
    
    @staticmethod
    def _score_contact(contact_info):
        """Score based on contact information (0-100)"""
        score = 0
        
        if contact_info.get('name'):
            score += 30
        if contact_info.get('email'):
            score += 35
        if contact_info.get('phone'):
            score += 35
        
        return score
    
    @staticmethod
    def _get_grade(score):
        """Get letter grade based on score"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'