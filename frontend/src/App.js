import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import UploadForm from './components/UploadForm';
import DocumentList from './components/DocumentList';
import Login from './components/Login';
import EditProfile from './components/EditProfile';
import { getAllDocuments, getUpcomingReminders, getHealthSummary } from './api';

const CATEGORIES = ['All', 'Education', 'Finance', 'Medical', 'Legal', 'Identity', 'Insurance', 'Other'];

function App() {
  const [user, setUser] = useState(null);
  const [darkMode, setDarkMode] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [showEditProfile, setShowEditProfile] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');
  const [documents, setDocuments] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [health, setHealth] = useState(null);
  const [activeCategory, setActiveCategory] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    document.body.classList.toggle('dark-body', darkMode);
  }, [darkMode]);

  const loadDocuments = useCallback(async () => {
    setLoading(true);
    const category = activeCategory === 'All' ? null : activeCategory;
    const data = await getAllDocuments(category);
    setDocuments(data);
    setLoading(false);
  }, [activeCategory]);

  const loadReminders = useCallback(async () => {
    const data = await getUpcomingReminders();
    setReminders(data);
  }, []);

  const loadHealth = useCallback(async () => {
    const data = await getHealthSummary();
    setHealth(data);
  }, []);

  useEffect(() => {
    if (user) {
      loadDocuments();
      loadReminders();
      loadHealth();
    }
  }, [loadDocuments, loadReminders, loadHealth, user]);

  if (!user) {
    return <Login onLoginSuccess={setUser} />;
  }

  function daysUntil(dueDateStr) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(dueDateStr + 'T00:00:00');
  return Math.round((due - today) / (1000 * 60 * 60 * 24));
}

const soonReminders = reminders.filter(function (r) {
  const daysLeft = daysUntil(r.due_date);
  return daysLeft >= 0 && daysLeft <= 30;
});

const expiredReminders = reminders.filter(function (r) {
  const daysLeft = daysUntil(r.due_date);
  return daysLeft < 0;
});

  const expiredDocIds = new Set(expiredReminders.map(function (r) { return r.document_id; }));
  const expiringDocIds = new Set(soonReminders.map(function (r) { return r.document_id; }));

  const filteredDocuments = documents.filter(function (doc) {
    const term = searchTerm.toLowerCase();
    const matchesSearch =
      doc.filename.toLowerCase().includes(term) ||
      (doc.summary && doc.summary.toLowerCase().includes(term));

    if (!matchesSearch) return false;

    if (statusFilter === 'expired') {
      return expiredDocIds.has(doc.id);
    }
    if (statusFilter === 'expiring') {
      return expiringDocIds.has(doc.id);
    }
    if (statusFilter === 'valid') {
      return !expiredDocIds.has(doc.id) && !expiringDocIds.has(doc.id);
    }
    return true;
  });

  function refreshAll() {
    loadDocuments();
    loadReminders();
    loadHealth();
  }

  function renderReminderLink(r) {
    const fileUrl = 'http://127.0.0.1:5000/api/documents/' + r.document_id + '/file';
    return React.createElement(
      'a',
      {
        key: r.id,
        href: fileUrl,
        target: '_blank',
        rel: 'noopener noreferrer',
        className: 'banner-item'
      },
      r.document_name + ' - ' + r.label + ': ' + r.due_date
    );
  }

  return (
    <div className={'app ' + (darkMode ? 'dark' : '')}>
      <header className="app-header">
        <div className="header-top">
          <div>
            <h1>📄 AI Document Life Companion</h1>
            <p>Upload, organize, and never miss a deadline</p>
          </div>
          <div className="header-buttons">
            <button className="theme-toggle-btn" onClick={() => setDarkMode(!darkMode)}>
              {darkMode ? '☀️' : '🌙'}
            </button>
            <div className="profile-wrapper">
              <button className="profile-icon-btn" onClick={() => setShowProfile(!showProfile)}>
                👤
              </button>
              {showProfile && (
                <div className="profile-dropdown">
                  <div className="profile-avatar-large">👤</div>
                  <p className="profile-name">{user.full_name}</p>
                  <p className="profile-email">{user.email}</p>
                  <span className="profile-username-badge">@{user.username}</span>
                  <div className="profile-stats">
                    <div className="profile-stat-item">
                      <strong>{health ? health.total_documents : 0}</strong>
                      <span>Documents</span>
                    </div>
                    <div className="profile-stat-item">
                      <strong>{soonReminders.length}</strong>
                      <span>Expiring Soon</span>
                    </div>
                  </div>
                  <button
                    className="edit-profile-btn full-width"
                    onClick={() => { setShowEditProfile(true); setShowProfile(false); }}
                  >
                    ✏️ Edit Profile
                  </button>
                  <button className="logout-btn full-width" onClick={() => setUser(null)}>
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {showEditProfile && (
        <EditProfile
          user={user}
          onClose={() => setShowEditProfile(false)}
          onUpdated={(updatedUser) => setUser(updatedUser)}
        />
      )}

      {health && (
        <div className="health-dashboard">
          <div
            className={'health-stat total clickable ' + (statusFilter === 'all' ? 'stat-active' : '')}
            onClick={() => setStatusFilter('all')}
          >
            <span className="health-icon">📄</span>
            <span className="health-number">{health.total_documents}</span>
            <span className="health-label">Total</span>
          </div>
          <div
            className={'health-stat valid clickable ' + (statusFilter === 'valid' ? 'stat-active' : '')}
            onClick={() => setStatusFilter('valid')}
          >
            <span className="health-icon">✅</span>
            <span className="health-number">{health.valid}</span>
            <span className="health-label">Valid</span>
          </div>
          <div
            className={'health-stat expiring clickable ' + (statusFilter === 'expiring' ? 'stat-active' : '')}
            onClick={() => setStatusFilter('expiring')}
          >
            <span className="health-icon">⏰</span>
            <span className="health-number">{health.expiring_soon}</span>
            <span className="health-label">Expiring Soon</span>
          </div>
          <div
            className={'health-stat expired clickable ' + (statusFilter === 'expired' ? 'stat-active' : '')}
            onClick={() => setStatusFilter('expired')}
          >
            <span className="health-icon">❌</span>
            <span className="health-number">{health.expired}</span>
            <span className="health-label">Expired</span>
          </div>
        </div>
      )}

      {soonReminders.length > 0 && (
        <div className="reminders-banner">
          <span className="banner-icon">⏰</span>
          <div className="banner-text">
            <strong>{soonReminders.length} item(s) expiring soon</strong>
            <div className="banner-list">
              {soonReminders.slice(0, 3).map(renderReminderLink)}
            </div>
          </div>
        </div>
      )}

      <UploadForm onUploadSuccess={refreshAll} />

      <div className="search-bar-container">
        <input
          type="text"
          className="search-bar"
          placeholder="🔍 Search documents by name or summary..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="category-filters">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            className={'filter-btn ' + (activeCategory === cat ? 'active' : '')}
            onClick={() => setActiveCategory(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      {statusFilter !== 'all' && (
        <div className="filter-active-banner">
          Showing {statusFilter} documents only
          <button onClick={() => setStatusFilter('all')}>Clear filter</button>
        </div>
      )}

      {loading ? (
        <p className="loading-text">Loading documents...</p>
      ) : (
        <DocumentList documents={filteredDocuments} onDelete={refreshAll} />
      )}
    </div>
  );
}

export default App;