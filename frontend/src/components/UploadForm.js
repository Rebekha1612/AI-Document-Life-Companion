import React, { useState, useEffect } from 'react';
import { uploadDocument } from '../api';

function UploadForm({ onUploadSuccess }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(''), 4000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setError('');

    try {
      await uploadDocument(file);
      onUploadSuccess();
    } catch (err) {
      setError(err.message || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  return (
    <div className="upload-form">
      <label className="upload-button">
        {uploading ? 'Processing...' : '+ Upload Document'}
        <input
          type="file"
          accept=".png,.jpg,.jpeg,.pdf"
          onChange={handleFileChange}
          disabled={uploading}
          style={{ display: 'none' }}
        />
      </label>

      {error && (
        <div className="toast-notification">
          <span>⚠️</span> {error}
        </div>
      )}
    </div>
  );
}

export default UploadForm;