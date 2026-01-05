// src/components/FileUpload.jsx
import React, { useState } from 'react';
import axios from 'axios';

function FileUpload({ onUploadSuccess, activeMode }) {
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

      setMessage(response.data?.message || 'Upload successful');
      onUploadSuccess(); // Notify the parent component
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
      <h2>Upload Your 
        {activeMode === 'study' ? ' Study Material' : ' Invoice'}
      </h2>
      <form onSubmit={handleSubmit}>
        <input type="file" accept=".pdf" onChange={handleFileChange} />
        <button type="submit" disabled={isUploading}>
          {isUploading ? 'Processing...' : 'Upload'}
        </button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

export default FileUpload;