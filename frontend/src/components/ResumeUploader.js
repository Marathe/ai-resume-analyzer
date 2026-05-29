import React, { useState, useRef } from 'react';
import axios from 'axios';
import './ResumeUploader.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function ResumeUploader({ onResumeUploaded }) {

  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const fileInputRef = useRef(null);

  const handleDrag = (e) => {

    e.preventDefault();
    e.stopPropagation();

    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    }

    if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {

    e.preventDefault();
    e.stopPropagation();

    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {

      const droppedFile = e.dataTransfer.files[0];

      validateAndSetFile(droppedFile);
    }
  };

  const validateAndSetFile = (selectedFile) => {

    if (!selectedFile) return;

    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];

    if (!allowedTypes.includes(selectedFile.type)) {

      setError('Only PDF and Word files are allowed');
      return;
    }

    setError(null);
    setFile(selectedFile);
  };

  const handleFileChange = (e) => {

    if (e.target.files && e.target.files[0]) {

      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleClick = () => {

    console.log('Opening file picker...');

    if (fileInputRef.current) {

      fileInputRef.current.value = null;
      fileInputRef.current.click();
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

      const response = await axios.post(
        `${API_URL}/api/resume/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      onResumeUploaded(response.data);

    } catch (err) {

      setError(
        err.response?.data?.error || 'Error uploading file'
      );

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
            onClick={handleClick}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >

            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={handleFileChange}
              className="file-input"
            />

            <div className="drop-content">

              <div className="drop-icon">📄</div>

              <h3>Drag and drop your resume here</h3>

              <p>or click to select a file</p>

            </div>

          </div>

          {file && (

            <div className="file-info">

              <p>
                📦 Selected:
                <strong> {file.name}</strong>
              </p>

              <p className="file-size">
                Size: {(file.size / 1024).toFixed(2)} KB
              </p>

            </div>
          )}

          {error && (

            <div className="error-message">
              ❌ {error}
            </div>
          )}

          <button
            type="submit"
            className="upload-button"
            disabled={!file || loading}
          >

            {loading
              ? '⏳ Uploading...'
              : '🚀 Analyze Resume'}

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