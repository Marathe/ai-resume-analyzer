import React, { useState } from 'react';
import './App.css';
import ResumeUploader from './components/ResumeUploader';
import ResumeAnalysis from './components/ResumeAnalysis';
import JobMatcher from './components/JobMatcher';

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
        <h1>AI Resume Analyzer</h1>
        <p>Intelligent Resume Analysis & Job Matching</p>
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
          Job Matcher
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
      </main>
    </div>
  );
}

export default App;