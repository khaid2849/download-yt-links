# YouTube Video Downloader

A simple, fast, and elegant web app to download YouTube videos. Built with Flask (Python) for the backend and Vue.js (Vite + Tailwind CSS) for the frontend.

---

## Features

- Paste one or more YouTube links to fetch video info
- Preview video details (title, thumbnail, duration, etc.)
- Select download quality (best, high, medium, low)
- Download videos directly or as a zip (for multiple files)
- Clean, responsive, and professional UI

---

## Tech Stack

- **Backend:** Flask (Python), yt-dlp
- **Frontend:** Vue 3, Vite, Tailwind CSS

---

## Project Structure

```
download-yt-links/
  app.py                # Entry point (run Flask app)
  /backend/             # Backend modules (Flask, logic, API)
  /frontend/            # Vue.js frontend source
  /static/              # Built frontend assets (served by Flask)
  /downloads/           # Downloaded files (auto-created)
  /temp/                # Temporary files (auto-created)
  requirements.txt      # Python dependencies
  README.md             # This file
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repo-url>
cd download-yt-links
```

### 2. Backend Setup (Flask)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Frontend Setup (Vue)

```bash
cd frontend
npm install
```

### 4. Build Frontend

```bash
npm run build
```

This outputs the production-ready frontend to `/static/`.

### 5. Run the App

```bash
cd ..
python app.py
```

Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## Usage

- Paste YouTube URLs (one per line)
- Click "Fetch Info" to preview
- Select quality and click "Download"
- Wait for progress and download your file(s)

---

## Contributing

Pull requests and issues are welcome! Please keep the codebase simple, clean, and well-documented.

---

## License

MIT
