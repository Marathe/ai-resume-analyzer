import React, { useState } from 'react';
import axios from 'axios';
import './JobMatcher.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function JobMatcher({ resume }) {
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [matchResult, setMatchResult] = useState(null);
  const [error, setError] = useState(null);

  const handleMatch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // For demo purposes, calculate match locally
      const resumeSkills = new Set(resume.skills?.all_skills || []);
      const jobKeywords = jobDescription.toLowerCase().split(/\s+/);
      
      let matchedKeywords = 0;
      jobKeywords.forEach(keyword => {
        if (resumeSkills.has(keyword.charAt(0).toUpperCase() + keyword.slice(1))) {
          matchedKeywords++;
        }
      });

      const matchPercentage = Math.min(100, (matchedKeywords / Math.max(1, jobKeywords.length)) * 100);

      setMatchResult({
        jobTitle,
        matchScore: matchPercentage.toFixed(1),
        matchedSkills: Array.from(resumeSkills).filter(skill => 
          jobDescription.toLowerCase().includes(skill.toLowerCase())
        ),
        recommendation: matchPercentage >= 80 ? 'Great fit!' : matchPercentage >= 60 ? 'Good match' : 'Consider upskilling'
      });
    } catch (err) {
      setError('Error calculating match');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="matcher-container">
      <div className="matcher-card">
        <h2>Match Resume to Job</h2>
        
        <form onSubmit={handleMatch}>
          <div className="form-group">
            <label>Job Title *</label>
            <input
              type="text"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="e.g., Senior Software Engineer"
              required
            />
          </div>

          <div className="form-group">
            <label>Job Description *</label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description here..."
              rows="8"
              required
            />
          </div>

          {error && <div className="error-message">❌ {error}</div>}

          <button type="submit" className="match-button" disabled={loading}>
            {loading ? '⏳ Analyzing...' : '🔍 Calculate Match'}
          </button>
        </form>

        {matchResult && (
          <div className="match-result">
            <h3>Match Results for: {matchResult.jobTitle}</h3>
            
            <div className="match-score-display">
              <div className="match-score-circle">
                <span className="match-percentage">{matchResult.matchScore}%</span>
              </div>
              <p className="match-recommendation">{matchResult.recommendation}</p>
            </div>

            {matchResult.matchedSkills.length > 0 && (
              <div className="matched-skills">
                <h4>Matched Skills</h4>
                <div className="skills-list">
                  {matchResult.matchedSkills.map((skill, idx) => (
                    <span key={idx} className="skill-badge matched">✓ {skill}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default JobMatcher;