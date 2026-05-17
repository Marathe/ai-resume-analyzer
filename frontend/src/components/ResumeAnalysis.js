import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './ResumeAnalysis.css';

function ResumeAnalysis({ resume }) {
  if (!resume) return <div>Loading...</div>;

  const scoreData = resume.score?.breakdown || {};
  const chartData = Object.entries(scoreData).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    score: value
  }));

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe'];

  const getGrade = (score) => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  };

  return (
    <div className="analysis-container">
      <div className="analysis-grid">
        {/* Overall Score Card */}
        <div className="score-card">
          <div className="score-circle">
            <div className="score-value">
              <span className="score-number">{resume.score?.overall_score?.toFixed(1)}</span>
              <span className="score-grade">{getGrade(resume.score?.overall_score)}</span>
            </div>
          </div>
          <h3>Overall Score</h3>
          <p className="score-description">Overall resume quality and completeness</p>
        </div>

        {/* Contact Info Card */}
        <div className="info-card">
          <h3>👤 Contact Information</h3>
          <div className="info-content">
            {resume.contact_info?.name && <p><strong>Name:</strong> {resume.contact_info.name}</p>}
            {resume.contact_info?.email && <p><strong>Email:</strong> <a href={`mailto:${resume.contact_info.email}`}>{resume.contact_info.email}</a></p>}
            {resume.contact_info?.phone && <p><strong>Phone:</strong> {resume.contact_info.phone}</p>}
          </div>
        </div>

        {/* Experience Card */}
        <div className="info-card">
          <h3>💼 Experience</h3>
          <div className="info-content">
            <p><strong>Years of Experience:</strong> {resume.years_of_experience?.toFixed(1) || 0} years</p>
          </div>
        </div>
      </div>

      {/* Score Breakdown Chart */}
      <div className="chart-container">
        <h3>Score Breakdown</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="score" fill="#667eea" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Skills Section */}
      <div className="skills-section">
        <h3>🎯 Skills</h3>
        
        {resume.skills?.technical_skills && resume.skills.technical_skills.length > 0 && (
          <div className="skills-category">
            <h4>Technical Skills ({resume.skills.technical_skills.length})</h4>
            <div className="skills-list">
              {resume.skills.technical_skills.map((skill, idx) => (
                <span key={idx} className="skill-tag technical">{skill}</span>
              ))}
            </div>
          </div>
        )}

        {resume.skills?.soft_skills && resume.skills.soft_skills.length > 0 && (
          <div className="skills-category">
            <h4>Soft Skills ({resume.skills.soft_skills.length})</h4>
            <div className="skills-list">
              {resume.skills.soft_skills.map((skill, idx) => (
                <span key={idx} className="skill-tag soft">{skill}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ResumeAnalysis;