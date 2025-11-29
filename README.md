# Night Owl - PDF Dark Mode Converter

A professional-grade tool to convert PDF documents to dark mode for comfortable reading at night.

## Features

- **Smart Conversion**: Converts background to black and text to white.
- **Image Preservation**: Detects and preserves images, diagrams, and charts.
- **Layout Integrity**: Maintains exact character positioning to prevent text overflow.
- **Privacy Focused**: Files are processed locally/on-server and deleted after download.

## Tech Stack

- **Backend**: FastAPI (Python)
- **PDF Processing**: PyMuPDF (fitz)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JS

## Local Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\Activate.ps1 # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   python main.py
   ```
5. Open `http://localhost:8000`

## Deployment

Ready for deployment on Render, Railway, or Heroku.
Includes `Procfile` for production.
