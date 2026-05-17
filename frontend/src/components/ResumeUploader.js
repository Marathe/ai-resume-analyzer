import React, { useState } from 'react';
import axios from 'axios';
import './ResumeUploader.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function ResumeUploader({ onResumeUploaded }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API_URL}/api/resume/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      onResumeUploaded(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Error uploading file');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="uploader-container">
      <div className="uploader-card">
        <h2>Upload Your Resume</h2>
        
        <form onSubmit={handleUpload}>
          <div
            className={`drop-zone ${dragActive ? 'active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="drop-content">
              <div className="drop-icon">📄</div>
              <h3>Drag and drop your resume here</h3>
              <p>or click to select a file</p>
              <input
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.docx,.doc"
                className="file-input"
              />
            </div>
          </div>

          {file && (
            <div className="file-info">
              <p>📦 Selected: <strong>{file.name}</strong></p>
              <p className="file-size">Size: {(file.size / 1024).toFixed(2)} KB</p>
            </div>
          )}

          {error && <div className="error-message">❌ {error}</div>}

          <button 
            type="submit" 
            className="upload-button"
            disabled={!file || loading}
          >
            {loading ? '⏳ Uploading...' : '🚀 Analyze Resume'}
          </button>
        </form>

        <div className="supported-formats">
          <h4>Supported Formats:</h4>
          <ul>
            <li>PDF (.pdf)</li>
            <li>Word (.docx, .doc)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default ResumeUploader;