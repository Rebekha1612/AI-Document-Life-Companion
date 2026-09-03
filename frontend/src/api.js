const API_BASE = 'http://127.0.0.1:5000/api/documents';
const AUTH_BASE = 'http://127.0.0.1:5000/api/auth';

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Upload failed');
  }

  return data;
}


export async function getAllDocuments(category = null) {
  const url = category ? `${API_BASE}/?category=${category}` : `${API_BASE}/`;
  const response = await fetch(url);
  return response.json();
}

export async function deleteDocument(id) {
  const response = await fetch(`${API_BASE}/${id}`, {
    method: 'DELETE',
  });
  return response.json();
}

export async function registerUser(fullName, email, username, password) {
  const response = await fetch(`${AUTH_BASE}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ full_name: fullName, email, username, password }),
  });

  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Registration failed');
  return data;
}

export async function loginUser(username, password) {
  const response = await fetch(`${AUTH_BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Login failed');
  return data;
}
export async function getUpcomingReminders() {
  const response = await fetch(`${API_BASE}/reminders/upcoming`);
  return response.json();
}
export async function getHealthSummary() {
  const response = await fetch(`${API_BASE}/health-summary`);
  return response.json();
}
export async function updateProfile(userId, fullName, email) {
  const response = await fetch(`${AUTH_BASE}/update-profile`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, full_name: fullName, email }),
  });

  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Update failed');
  return data;
}