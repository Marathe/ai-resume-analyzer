import React, { useState } from 'react';
import axios from 'axios';
import {
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';
import './JobMatcher.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function JobMatcher({ resume }) {
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);

  const handleMatch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/api/resume/analyze-job`, {
        resume_id: resume.id,
        job_title: jobTitle,
        job_description: jobDescription
      });
      setAnalysis(response.data.analysis);
    } catch (err) {
      setError(err.response?.data?.error || 'Error calculating advanced match');
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async (reportType) => {
    if (!analysis) return;
    try {
      setReportLoading(true);
      const response = await axios.post(
        `${API_URL}/api/resume/report/${reportType}`,
        { analysis },
        { responseType: 'blob' }
      );
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportType}-report.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Unable to download report right now');
    } finally {
      setReportLoading(false);
    }
  };

  const chartColors = ['#8B5CF6', '#EC4899', '#3B82F6', '#14B8A6', '#F59E0B', '#EF4444'];
  const insights = analysis?.career_insights || {};
  const skillsGap = analysis?.skills_gap_analysis || {};
  const viz = analysis?.visualizations || {};

  return (
    <div className="matcher-container">
      <div className="matcher-card">
        <h2>Enterprise AI Resume Intelligence</h2>
        <p className="subtitle">Advanced upskilling engine, career insights, and premium analytics dashboard.</p>

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
            {loading ? '⏳ Running AI Analysis...' : '🔍 Analyze for Enterprise Fit'}
          </button>
        </form>

        {analysis && (
          <div className="match-result">
            <h3>{analysis?.job?.title} - Intelligence Dashboard</h3>

            <div className="kpi-grid">
              <div className="kpi-card">
                <h4>Match Score</h4>
                <div className="kpi-value">{skillsGap.match_score}%</div>
              </div>
              <div className="kpi-card">
                <h4>ATS Compatibility</h4>
                <div className="kpi-value">{insights.ats_compatibility_score}%</div>
              </div>
              <div className="kpi-card">
                <h4>Industry Readiness</h4>
                <div className="kpi-value">{insights.industry_readiness_score}%</div>
              </div>
              <div className="kpi-card">
                <h4>Target Role</h4>
                <div className="kpi-value">{insights.seniority_detection}</div>
                {insights.experience_level && (
                  <p className="kpi-subvalue">Experience level: {insights.experience_level}</p>
                )}
              </div>
            </div>

            <div className="insights-grid">
              <div className="insight-card">
                <h4>Resume Strengths</h4>
                {(insights.resume_strengths || []).map((item, idx) => (
                  <p key={idx}>✅ {item}</p>
                ))}
              </div>
              <div className="insight-card">
                <h4>Resume Weaknesses</h4>
                {(insights.resume_weaknesses || []).map((item, idx) => (
                  <p key={idx}>⚠️ {item}</p>
                ))}
              </div>
              <div className="insight-card">
                <h4>Performance Scores</h4>
                <p>Interview Readiness: {insights.interview_readiness_score}%</p>
                <p>Project Quality: {insights.project_quality_score}%</p>
                <p>
                  Salary Prediction: ${insights.salary_prediction?.min} - ${insights.salary_prediction?.max}
                </p>
              </div>
            </div>

            <div className="skills-columns">
              <div className="skill-panel">
                <h4>Matched Skills</h4>
                <div className="skills-list">
                  {(skillsGap.matched_skills || []).map((skill, idx) => (
                    <span key={idx} className="skill-badge matched">✓ {skill}</span>
                  ))}
                </div>
              </div>
              <div className="skill-panel">
                <h4>Missing Technologies</h4>
                {skillsGap.skills_source === 'role_fallback' && (
                  <div className="skills-source-note">
                    No clear technical stack detected in JD text; using role-based defaults.
                  </div>
                )}
                <div className="skills-list">
                  {(skillsGap.missing_skills || []).length > 0 ? (
                    (skillsGap.missing_skills || []).map((skill, idx) => (
                      <span key={idx} className="skill-badge missing">{skill}</span>
                    ))
                  ) : (
                    <span className="no-gap-text">No missing technologies for this role match.</span>
                  )}
                </div>
              </div>
            </div>

            <div className="chart-grid">
              <div className="chart-box">
                <h4>ATS Score Doughnut Chart</h4>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie data={viz.ats_score_doughnut || []} innerRadius={70} outerRadius={110} dataKey="value">
                      {(viz.ats_score_doughnut || []).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="chart-box">
                <h4>Resume Score Trend</h4>
                <ResponsiveContainer width="100%" height={280}>
                  <LineChart data={viz.resume_score_trend || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="score" stroke="#3B82F6" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="chart-box">
                <h4>Technology Demand Graph</h4>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={viz.technology_demand_graph || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="technology" interval={0} angle={-20} textAnchor="end" height={70} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="demand_index" fill="#14B8A6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="chart-box">
                <h4>Experience Timeline</h4>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={viz.experience_timeline || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="stage" interval={0} angle={-15} textAnchor="end" height={60} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#F59E0B" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="chart-box">
              <h4>Skill Heatmap</h4>
              <div className="heatmap-grid">
                {(viz.skill_heatmap || []).map((item, idx) => (
                  <div
                    key={idx}
                    className="heatmap-cell"
                    style={{ backgroundColor: `rgba(59, 130, 246, ${item.intensity / 100})` }}
                  >
                    {item.skill}
                    <span>{item.intensity}%</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="upskill-section">
              <h4>Advanced Upskilling Engine</h4>
              {(analysis.upskilling_engine || []).map((item, idx) => (
                <div key={idx} className="upskill-item">
                  <h5>{item.technology}</h5>
                  <p>Priority: {item.learning_priority}</p>
                  <p>Time: {item.estimated_learning_time}</p>
                  <p>Difficulty: {item.difficulty_level}</p>
                  <p>Path: {item.learning_path}</p>
                </div>
              ))}
            </div>

            <div className="report-actions">
              <button type="button" onClick={() => downloadReport('resume-analysis')} disabled={reportLoading}>
                Download Resume Analysis PDF
              </button>
              <button type="button" onClick={() => downloadReport('skill-gap')} disabled={reportLoading}>
                Download Skill Gap PDF
              </button>
              <button type="button" onClick={() => downloadReport('career-improvement')} disabled={reportLoading}>
                Download Career Improvement PDF
              </button>
            </div>

            <div className="enterprise-note">
              Enterprise AI-powered Resume Intelligence Platform output: upskilling roadmap, ATS intelligence,
              industry readiness metrics, and actionable career acceleration insights.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default JobMatcher;