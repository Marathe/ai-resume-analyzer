import re

class SkillsExtractor:
    """Extract technical and soft skills from resume text"""
    
    # Comprehensive skills database
    TECHNICAL_SKILLS = {
        # Programming Languages
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
        'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'SQL', 'HTML', 'CSS', 'Bash', 'Shell',
        
        # Web Frameworks
        'React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'ASP.NET', 'Express', 'Node.js',
        'Next.js', 'Nuxt', 'FastAPI', 'Rails', 'Laravel', 'Symfony',
        
        # Databases
        'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Cassandra', 'DynamoDB',
        'Firebase', 'Oracle', 'SQL Server', 'MariaDB', 'SQLite', 'Hadoop',
        
        # Cloud & DevOps
        'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'CI/CD', 'Jenkins', 'GitLab CI',
        'GitHub Actions', 'Terraform', 'Ansible', 'CloudFormation', 'Heroku',
        
        # Data & AI/ML
        'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'Keras', 'OpenCV',
        'NLP', 'Machine Learning', 'Deep Learning', 'Data Analysis', 'Big Data',
        
        # Tools & Technologies
        'Git', 'GitHub', 'GitLab', 'Jira', 'Confluence', 'Linux', 'Windows', 'macOS',
        'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum', 'Webpack', 'Nginx',
        'Apache', 'Linux', 'Unix', 'AWS Lambda', 'Serverless'
    }
    
    SOFT_SKILLS = {
        'Communication', 'Leadership', 'Teamwork', 'Problem Solving', 'Critical Thinking',
        'Collaboration', 'Project Management', 'Time Management', 'Creativity', 'Adaptability',
        'Initiative', 'Attention to Detail', 'Organization', 'Decision Making', 'Negotiation',
        'Presentation', 'Research', 'Analysis', 'Planning', 'Strategy', 'Mentoring',
        'Training', 'Coaching', 'Conflict Resolution', 'Customer Service', 'Sales',
        'Marketing', 'Business Development', 'Strategic Planning', 'Innovation'
    }
    
    @staticmethod
    def extract_skills(text):
        """Extract technical and soft skills from text"""
        text_lower = text.lower()
        
        technical_skills = []
        soft_skills = []
        
        # Extract technical skills
        for skill in SkillsExtractor.TECHNICAL_SKILLS:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                technical_skills.append(skill)
        
        # Extract soft skills
        for skill in SkillsExtractor.SOFT_SKILLS:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                soft_skills.append(skill)
        
        return {
            'technical_skills': list(set(technical_skills)),
            'soft_skills': list(set(soft_skills)),
            'all_skills': list(set(technical_skills + soft_skills))
        }
    
    @staticmethod
    def extract_years_of_experience(text):
        """Extract years of experience from text"""
        patterns = [
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?experience',
            r'experience:?\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*years?\s*experience',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return 0.0