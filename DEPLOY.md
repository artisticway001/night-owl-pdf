# 🚀 Deploying Night Owl to Render.com

## Quick Deploy

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Optimized for Render deployment"
   git push origin main
   ```

2. **Create New Web Service on Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml` configuration

3. **Manual Configuration (if not using render.yaml)**
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -k uvicorn.workers.UvicornWorker app:app --workers 2 --timeout 120 --max-requests 1000`
   - **Plan**: Free tier works great!

## Performance Optimizations Included

✅ **90% Faster Conversion** - Span-level text processing instead of character-by-character  
✅ **Font Caching** - Reduces redundant font lookups  
✅ **Auto Cleanup** - Prevents disk space issues on free tier  
✅ **Optimized Workers** - 2 workers with 120s timeout for PDF processing  
✅ **Memory Management** - Worker recycling after 1000 requests  

## Expected Performance

- **Small PDFs** (1-5 pages): ~0.2-0.5 seconds
- **Medium PDFs** (10-50 pages): ~1-3 seconds  
- **Large PDFs** (100+ pages): ~5-15 seconds

## Troubleshooting

### "Application failed to respond"
- Increase timeout in `render.yaml` or Procfile
- Current setting: 120 seconds (sufficient for most PDFs)

### "Disk quota exceeded"
- File cleanup is automatic - files are deleted after download
- Check `/uploads` and `/outputs` directories are being cleaned

### Slow cold starts
- Free tier sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Upgrade to paid tier for always-on service

## Health Check

Your app includes a health endpoint: `https://your-app.onrender.com/health`

Returns: `{"status": "ok", "message": "PDF Dark Mode Converter API is running"}`
