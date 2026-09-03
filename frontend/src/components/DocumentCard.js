import React, { useState } from 'react';
import { deleteDocument } from '../api';
import ConfirmDialog from './ConfirmDialog';
const API_BASE = 'http://127.0.0.1:5000/api/documents';

function DocumentCard({ doc, onDelete }) {
  const [showConfirm, setShowConfirm] = useState(false);

  const handleDeleteClick = () => {
    setShowConfirm(true);
  };

  const handleConfirmDelete = async () => {
    await deleteDocument(doc.id);
    setShowConfirm(false);
    onDelete();
  };

  const hasReminders = doc.reminders && doc.reminders.length > 0;
  const isImage = /\.(png|jpg|jpeg)$/i.test(doc.filename);
  const fileUrl = `${API_BASE}/${doc.id}/file`;

  let details = {};
  try {
    details = doc.key_details ? JSON.parse(doc.key_details) : {};
  } catch (e) {
    details = {};
  }

  const hasDetails = Object.keys(details).length > 0;

  return (
    <div className="document-card">
      <div className="card-header">
        <span className={`category-badge category-${doc.category?.toLowerCase()}`}>
          {doc.category || 'Uncategorized'}
        </span>
        <button className="delete-btn" onClick={handleDeleteClick}>×</button>
      </div>

      {isImage && (
        <a href={fileUrl} target="_blank" rel="noopener noreferrer">
          <img src={fileUrl} alt={doc.filename} className="doc-thumbnail" />
        </a>
      )}

      <p className="doc-filename">{doc.filename}</p>

      <p className="doc-summary">
        {doc.summary || 'No summary available for this document.'}
      </p>

      {hasDetails && (
        <div className="key-details-section">
          {details.id_numbers && (
            <div className="detail-row">
              <span className="detail-label">ID/Ref:</span> {details.id_numbers.join(', ')}
            </div>
          )}
          {details.amounts && (
            <div className="detail-row">
              <span className="detail-label">Amount:</span> {details.amounts.join(', ')}
            </div>
          )}
          {details.possible_names && (
            <div className="detail-row">
              <span className="detail-label">Name:</span> {details.possible_names.join(', ')}
            </div>
          )}
          {details.dates_mentioned && (
            <div className="detail-row">
              <span className="detail-label">Dates:</span> {details.dates_mentioned.join(', ')}
            </div>
          )}
        </div>
      )}

      {hasReminders && (
        <div className="reminders-section">
          {doc.reminders.map((r) => {
            const isExpired = new Date(r.due_date) < new Date().setHours(0, 0, 0, 0);
            return (
              <div key={r.id} className={isExpired ? 'reminder-tag expired' : 'reminder-tag'}>
                {isExpired ? '❌' : '⏰'} {r.label}: {r.due_date}
              </div>
            );
          })}
        </div>
      )}

      <div className="card-footer">
        <p className="doc-date">
          Uploaded: {new Date(doc.uploaded_at).toLocaleDateString()}
        </p>
        <a href={fileUrl} target="_blank" rel="noopener noreferrer" className="view-link">
          View Original
        </a>
      </div>

      {showConfirm && (
        <ConfirmDialog
          title="Delete Document"
          message={`Are you sure you want to delete "${doc.filename}"? This cannot be undone.`}
          onConfirm={handleConfirmDelete}
          onCancel={() => setShowConfirm(false)}
        />
      )}
    </div>
  );
}

export default DocumentCard;