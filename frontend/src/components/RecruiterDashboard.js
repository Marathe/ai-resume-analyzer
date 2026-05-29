import React, { useState } from 'react';
import axios from 'axios';
import './RecruiterDashboard.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function RecruiterDashboard() {
  const [files, setFiles] = useState([]);
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [company, setCompany] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleFiles = (event) => {
    const selected = Array.from(event.target.files || []);
    setFiles(selected);
  };

  const runBatchAnalysis = async (e) => {
    e.preventDefault();
    if (!files.length) {
      setError('Please upload at least one resume');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      files.forEach((file) => formData.append('files', file));
      formData.append('job_title', jobTitle);
      formData.append('job_description', jobDescription);
      formData.append('company', company);

      const response = await axios.post(`${API_URL}/api/resume/batch-analyze`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Batch analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const exportShortlisted = () => {
    const shortlisted = result?.ai_shortlist || [];
    if (!shortlisted.length) return;
    const headers = ['Rank', 'Candidate', 'Email', 'Match Score', 'ATS Score', 'Experience Years'];
    const rows = shortlisted.map((c) => [
      c.rank, c.candidate_name, c.email || '', c.match_score, c.ats_score, c.years_of_experience
    ]);
    const csv = [headers, ...rows].map((row) => row.map((v) => `"${v}"`).join(',')).join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'shortlisted-candidates.csv');
    link.click();
    window.URL.revokeObjectURL(url);
  };

  const leaderboard = result?.candidate_leaderboard || [];

  return (
    <div className="recruiter-container">
      <div className="recruiter-card">
        <h2>Recruitment Intelligence Platform</h2>
        <p className="subtitle">Single and bulk resume analysis with smart ranking and shortlisting.</p>

        <form onSubmit={runBatchAnalysis} className="batch-form">
          <div className="form-grid">
            <div className="form-group">
              <label>Job Title *</label>
              <input value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} required placeholder="Team Lead" />
            </div>
            <div className="form-group">
              <label>Company</label>
              <input value={company} onChange={(e) => setCompany(e.target.value)} placeholder="Company name" />
            </div>
          </div>
          <div className="form-group">
            <label>Job Description *</label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows="6"
              required
              placeholder="Paste the job description"
            />
          </div>
          <div className="form-group">
            <label>Bulk Resume Upload *</label>
            <input type="file" multiple accept=".pdf,.doc,.docx" onChange={handleFiles} />
            <p className="meta">{files.length} resumes selected</p>
          </div>
          {error && <div className="error-message">❌ {error}</div>}
          <button type="submit" className="match-button" disabled={loading}>
            {loading ? '⏳ Running Batch AI Analysis...' : '🚀 Analyze Candidate Batch'}
          </button>
        </form>

        {result && (
          <div className="dashboard-section">
            <div className="kpi-grid">
              <div className="kpi-card"><h4>Total Candidates</h4><div className="kpi-value">{result.batch_summary?.total_candidates}</div></div>
              <div className="kpi-card"><h4>Shortlisted</h4><div className="kpi-value">{result.batch_summary?.shortlisted_count}</div></div>
              <div className="kpi-card"><h4>Avg Match</h4><div className="kpi-value">{result.batch_summary?.average_match_score}%</div></div>
              <div className="kpi-card"><h4>Avg ATS</h4><div className="kpi-value">{result.batch_summary?.average_ats_score}%</div></div>
            </div>

            <div className="top-recommendation">
              <h3>Top Candidate Recommendation</h3>
              <p><strong>{result.top_candidate_recommendation?.candidate_name}</strong> - Rank #{result.top_candidate_recommendation?.rank}</p>
              <p>Match: {result.top_candidate_recommendation?.match_score}% | ATS: {result.top_candidate_recommendation?.ats_score}%</p>
            </div>

            <div className="report-actions">
              <button type="button" onClick={exportShortlisted}>Export Shortlisted Candidates (CSV)</button>
            </div>

            <div className="cards-grid">
              {leaderboard.map((candidate) => (
                <div key={candidate.resume_id} className="candidate-card">
                  <div className="card-top">
                    <div>
                      <h4>{candidate.candidate_name}</h4>
                      <p className="muted">Experience: {candidate.years_of_experience} years</p>
                    </div>
                    <div className={`status-pill ${candidate.shortlisted ? 'ok' : 'hold'}`}>
                      #{candidate.rank} {candidate.shortlisting_status || (candidate.shortlisted ? 'Shortlisted' : 'Not Shortlisted')}
                    </div>
                  </div>

                  <div className="metrics-row">
                    <span>Match %: <strong>{candidate.match_score}</strong></span>
                    <span>ATS Score: <strong>{candidate.ats_score}</strong></span>
                    <span>Interview: <strong>{candidate.interview_recommendation_status}</strong></span>
                  </div>

                  <div className="info-block">
                    <p><strong>Missing Skills:</strong> {(candidate.missing_skills || []).slice(0, 5).join(', ') || 'None'}</p>
                    <p><strong>Critical Missing Skills:</strong> {(candidate.critical_missing_skills || []).join(', ') || 'None'}</p>
                    <p><strong>Recommended Technologies:</strong> {(candidate.recommended_technologies || []).join(', ') || 'None'}</p>
                    <p><strong>Resume Strength:</strong> {candidate.resume_strength || 'Balanced profile'}</p>
                    <p><strong>Improvement Suggestions:</strong> {(candidate.improvement_suggestions || []).slice(0, 2).join(' | ') || 'No major suggestions'}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default RecruiterDashboard;
