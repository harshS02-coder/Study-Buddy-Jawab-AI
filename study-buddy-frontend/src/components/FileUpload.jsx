// src/components/FileUpload.jsx
import React, { useState } from 'react';
import axios from 'axios';

function FileUpload({ onUploadSuccess , activeMode }) {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [isUploading, setIsUploading] = useState(false);


  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setMessage('Please select a file first.');
      return;
    }

    setIsUploading(true);
    setMessage('Uploading and processing file...');
    const formData = new FormData();
    formData.append('file', file);
    formData.append('use_case', activeMode);

    try {
      const response = await axios.post(`${import.meta.env.VITE_BASE_URL}/upload`, formData);

      const {document_id} = response.data;
      console.log('Upload response:', response.data);
      console.log('Document ID:', document_id);

      setMessage(response.data?.message || 'Upload successful');
      onUploadSuccess(document_id); // Notify the parent component
    } catch (error) {
      console.error('Upload error:', error);
      const serverMsg = error.response?.data?.error || error.response?.data?.message;
      setMessage(serverMsg ? `Error: ${serverMsg}` : 'An error occurred during upload.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <form onSubmit={handleSubmit}>
        <div className="file-upload-area">
          <input 
            type="file" 
            accept=".pdf" 
            onChange={handleFileChange}
            id="file-input"
            className="file-input-hidden"
          />
          <label htmlFor="file-input" className="file-upload-label">
            <div className="upload-icon-wrapper">
              <svg className="upload-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M7 18C4.23858 18 2 15.7614 2 13C2 10.2386 4.23858 8 7 8C7.16351 8 7.32529 8.00773 7.48508 8.02281C8.08344 5.64163 10.2844 4 12.9167 4C15.549 4 17.75 5.64163 18.3483 8.02281C18.5081 8.00773 18.6699 8 18.8333 8C21.595 8 23.8333 10.2386 23.8333 13C23.8333 15.7614 21.595 18 18.8333 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M12 21V12M12 12L9 15M12 12L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <div className="upload-text">
              <h3 className="upload-title">
                {file ? file.name : 'Choose a file or drag it here'}
              </h3>
              <p className="upload-subtitle">
                {file ? 'Click to change file' : `${activeMode === 'study' ? 'Study Material' : 'Invoice'} • PDF format only`}
              </p>
            </div>
          </label>
        </div>
        
        <button 
          type="submit" 
          disabled={isUploading || !file}
          className="upload-submit-btn"
        >
          {isUploading ? (
            <>
              <span className="spinner"></span>
              Processing...
            </>
          ) : (
            <>
              <svg className="btn-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 16L8.586 11.414C9.367 10.633 10.633 10.633 11.414 11.414L16 16M14 14L15.586 12.414C16.367 11.633 17.633 11.633 18.414 12.414L20 14M14 8H14.01M6 20H18C19.105 20 20 19.105 20 18V6C20 4.895 19.105 4 18 4H6C4.895 4 4 4.895 4 6V18C4 19.105 4.895 20 6 20Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Upload & Process
            </>
          )}
        </button>
      </form>
      {message && <p className="upload-message">{message}</p>}
    </div>
  );
}

export default FileUpload;