import React, { useState } from 'react';
import './App.css';
import ResumeUploader from './components/ResumeUploader';
import ResumeAnalysis from './components/ResumeAnalysis';
import JobMatcher from './components/JobMatcher';
import RecruiterDashboard from './components/RecruiterDashboard';

function App() {
  const [currentResume, setCurrentResume] = useState(null);
  const [activeTab, setActiveTab] = useState('upload');

  const handleResumeUploaded = (resumeData) => {
    setCurrentResume(resumeData);
    setActiveTab('analysis');
  };

  return (
    <div className="App">
      <header className="header">
        <h1>Resume Intelligence Platform</h1>
        <p>Enterprise-grade AI insights, upskilling, and premium career analytics</p>
      </header>

      <nav className="nav-tabs">
        <button 
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          Upload Resume
        </button>
        <button 
          className={`tab-button ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
          disabled={!currentResume}
        >
          Analysis
        </button>
        <button 
          className={`tab-button ${activeTab === 'matcher' ? 'active' : ''}`}
          onClick={() => setActiveTab('matcher')}
          disabled={!currentResume}
        >
          AI Intelligence Dashboard
        </button>
        <button
          className={`tab-button ${activeTab === 'recruiter' ? 'active' : ''}`}
          onClick={() => setActiveTab('recruiter')}
        >
          Recruiter Intelligence
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'upload' && (
          <ResumeUploader onResumeUploaded={handleResumeUploaded} />
        )}
        {activeTab === 'analysis' && currentResume && (
          <ResumeAnalysis resume={currentResume} />
        )}
        {activeTab === 'matcher' && currentResume && (
          <JobMatcher resume={currentResume} />
        )}
        {activeTab === 'recruiter' && (
          <RecruiterDashboard />
        )}
      </main>
    </div>
  );
}

export default App;