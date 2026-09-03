# AI Document Life Companion

A full-stack AI-powered document management application that helps users upload, organize, understand, and keep track of important documents.

## 🚀 Features

- 📄 **Document Upload** – Upload PDF and image-based documents.
- 🔍 **OCR Text Extraction** – Automatically extract text from scanned documents using Tesseract OCR.
- 🤖 **AI Classification** – Identify and categorize documents using machine learning.
- 📝 **AI Summarization** – Generate concise summaries of document content using Hugging Face models.
- 🧠 **Important Information Extraction** – Identify useful information such as dates and key details.
- ⏰ **Smart Reminders** – Detect expiry-related information and generate reminders.
- 🕒 **AI Memory Timeline** – Organize important document events chronologically.
- 🔗 **Relationship Finder** – Discover connections between uploaded documents.
- 📊 **Document Dashboard** – View and manage documents through an interactive interface.

## 🛠️ Tech Stack

### Frontend
- React.js
- Vite
- JavaScript
- HTML
- CSS

### Backend
- Python
- Flask
- SQLite
- SQLAlchemy

### AI & Machine Learning
- Hugging Face Transformers
- Scikit-learn
- Tesseract OCR

## 🏗️ Architecture

```text
User
  │
  ▼
React.js Frontend
  │
  │ HTTP Requests
  ▼
Flask Backend
  │
  ├── OCR Service
  ├── AI Service
  ├── Reminder Service
  └── Document Management
          │
          ▼
      SQLite Database
