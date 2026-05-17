# AI Resume Analyzer

An intelligent resume analysis tool that uses AI to parse, analyze, and score resumes. It extracts key information, identifies skills, and matches resumes against job descriptions.

## Features

- **Resume Parsing**: Extract text and structure from PDF and DOCX files
- **Skills Extraction**: Identify technical and soft skills from resumes
- **Resume Scoring**: Rate resumes based on various criteria
- **Job Matching**: Match resumes against job descriptions
- **Analytics Dashboard**: Visual insights into resume data
- **REST API**: Comprehensive API for integration

## Tech Stack

### Backend
- **Python 3.10+**
- **Flask** - Web framework
- **spaCy** - NLP for text processing
- **PyPDF2** & **python-docx** - Document parsing
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database

### Frontend
- **React 18** - UI framework
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Recharts** - Data visualization

## Project Structure

```
ai-resume-analyzer/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── config.py
│   ├── models.py
│   ├── utils/
│   │   ├── parser.py
│   │   ├── skills.py
│   │   └── scorer.py
│   └── routes/
│       └── resume.py
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── tailwind.config.js
├── docker-compose.yml
├── .gitignore
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- PostgreSQL 12+
- Docker (optional)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## API Endpoints

- `POST /api/resume/upload` - Upload and parse resume
- `POST /api/resume/analyze` - Analyze resume
- `POST /api/resume/score` - Score resume
- `POST /api/job/match` - Match resume to job description
- `GET /api/resume/<id>` - Get resume analysis results

## Usage

1. Upload a resume (PDF or DOCX)
2. View extracted information and skills
3. Get a resume score
4. Match against job descriptions
5. Export analysis report

## Development

```bash
# Run tests
pytest

# Format code
black .

# Lint
flake8
```

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for Docker and production deployment instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Author

Marathe