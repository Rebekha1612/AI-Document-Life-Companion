import React from 'react';
import DocumentCard from './DocumentCard';

function DocumentList({ documents, onDelete }) {
  if (documents.length === 0) {
    return <p className="empty-state">No documents uploaded yet. Upload one to get started!</p>;
  }

  return (
    <div className="document-grid">
      {documents.map((doc) => (
        <DocumentCard key={doc.id} doc={doc} onDelete={onDelete} />
      ))}
    </div>
  );
}

export default DocumentList;