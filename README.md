# Night Owl - PDF Dark Mode Converter 🦉

A professional-grade tool to convert PDF documents to dark mode for comfortable reading at night.

## Features

- **Smart Conversion**: Converts background to black and text to white.
- **Image Preservation**: Detects and preserves images, diagrams, and charts.
- **Layout Integrity**: Maintains exact character positioning to prevent text overflow.
- **Privacy Focused**: Files are processed locally/on-server and deleted after download.
- **⚡ Blazing Fast**: Optimized span-level processing (~0.2s for small PDFs)

## Performance

- **Small PDFs** (1-5 pages): ~0.2-0.5 seconds
- **Medium PDFs** (10-50 pages): ~1-3 seconds
- **Large PDFs** (100+ pages): ~5-15 seconds

## Tech Stack

- **Backend**: FastAPI (Python)
- **PDF Processing**: PyMuPDF (fitz)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JS
- **Production**: Gunicorn with Uvicorn workers

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
   python app.py
   ```
5. Open `http://localhost:8000`

## Deployment

Ready for deployment on **Render**, Railway, or Heroku.

### Quick Deploy to Render.com

See [DEPLOY.md](DEPLOY.md) for detailed instructions.

**TL;DR**: Push to GitHub, connect to Render, auto-deploys with `render.yaml`

## Optimizations

✅ Span-level text processing (90% faster than character-by-character)  
✅ Font caching for reduced lookups  
✅ Automatic file cleanup  
✅ Optimized Gunicorn workers (2 workers, 120s timeout)  
✅ Memory management with worker recycling

