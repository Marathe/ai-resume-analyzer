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
        """Extract years of experience from text.

        Handles:
        - Month-year ranges: Jan 2018 - Mar 2021, January 2018 to Present
        - Year ranges: 2018 - 2021, 2018 - Present
        - 'since YYYY' patterns
        - Explicit totals: 'Total experience: 7 years'
        - Decimal years: 7.5 years, over 7 years, 7+ years
        """
        try:
            from datetime import datetime, date

            if not text:
                return 0.0

            # PRIORITY 1: Look for explicit total statements first
            total_patterns = [
                r'total\s+experience\s*:?\s*(\d+(?:\.\d+)?)',
                r'years\s+of\s+experience\s*:?\s*(\d+(?:\.\d+)?)',
            ]
            for pat in total_patterns:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    try:
                        return round(float(m.group(1)), 1)
                    except (ValueError, AttributeError):
                        pass

            # PRIORITY 2: Parse job date intervals
            now = datetime.now()
            intervals = []

            # A) Month-year ranges: Jan 2018 - Mar 2021 or January 2018 to Present
            month_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)'
            date_range_pattern = re.compile(
                rf'({month_pattern}\s+\d{{4}})\s*[\-–—to]+\s*({month_pattern}\s+\d{{4}}|[Pp]resent)',
                re.IGNORECASE
            )

            for m in date_range_pattern.finditer(text):
                try:
                    start_str = m.group(1).strip()
                    end_str = m.group(2).strip()

                    # Parse start date
                    try:
                        start_dt = datetime.strptime(start_str, '%b %Y')
                    except ValueError:
                        start_dt = datetime.strptime(start_str, '%B %Y')
                    start_date = date(start_dt.year, start_dt.month, 1)

                    # Parse end date
                    if end_str.lower() == 'present':
                        end_date = date(now.year, now.month, now.day)
                    else:
                        try:
                            end_dt = datetime.strptime(end_str, '%b %Y')
                        except ValueError:
                            end_dt = datetime.strptime(end_str, '%B %Y')
                        # Use day 28 for past dates to be safe
                        end_date = date(end_dt.year, end_dt.month, 28)

                    if end_date >= start_date:
                        intervals.append((start_date, end_date))
                except (ValueError, AttributeError):
                    continue

            # B) Year-only ranges: 2018-2021 or 2018-Present
            if not intervals:
                year_pattern = re.compile(r'(\d{4})\s*[\-–—to]+\s*(\d{4}|[Pp]resent)', re.IGNORECASE)
                for m in year_pattern.finditer(text):
                    try:
                        start_year = int(m.group(1))
                        end_str = m.group(2).strip()
                        end_year = now.year if end_str.lower() == 'present' else int(end_str)

                        start_date = date(start_year, 1, 1)
                        end_date = date(end_year, 12, 31)

                        if end_date >= start_date:
                            intervals.append((start_date, end_date))
                    except (ValueError, AttributeError):
                        continue

            # If we found intervals, merge them and calculate total
            if intervals:
                intervals.sort(key=lambda x: x[0])
                merged = []
                cur_start, cur_end = intervals[0]

                for next_start, next_end in intervals[1:]:
                    gap_days = (next_start - cur_end).days
                    # Merge if gap <= 15 days (standard job transition)
                    if gap_days <= 15:
                        cur_end = max(cur_end, next_end)
                    else:
                        merged.append((cur_start, cur_end))
                        cur_start, cur_end = next_start, next_end

                merged.append((cur_start, cur_end))

                # Calculate total months from merged intervals
                total_months = 0
                for s, e in merged:
                    months = (e.year - s.year) * 12 + (e.month - s.month) + (e.day - s.day) / 30.0
                    total_months += max(0, months)

                return round(total_months / 12.0, 1)

            # PRIORITY 3: Explicit year numbers as fallback
            candidates = []

            # Decimal or integer years: 7.5 years, over 7 years, 7+ years
            year_pattern = re.compile(r'(?:over\s+)?(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)', re.IGNORECASE)
            for m in year_pattern.finditer(text):
                try:
                    candidates.append(float(m.group(1)))
                except (ValueError, AttributeError):
                    continue

            # Months: 6 months -> 0.5 years
            month_pattern = re.compile(r'(\d+)\s*(?:months?|mos?)', re.IGNORECASE)
            for m in month_pattern.finditer(text):
                try:
                    months = int(m.group(1))
                    candidates.append(months / 12.0)
                except (ValueError, AttributeError):
                    continue

            if candidates:
                return round(max(candidates), 1)

            return 0.0

        except Exception:
            # If anything goes wrong, return 0.0 instead of failing
            return 0.0
