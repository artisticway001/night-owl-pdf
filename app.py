from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from converter import PDFDarkThemeConverter

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="PDF Dark Mode Converter")

# Allow CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

converter = PDFDarkThemeConverter()

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    output_filename = f"dark_{file.filename}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    try:
        # Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Convert PDF
        converter.convert(input_path, output_path)
        
        # Clean up files after response is sent
        # This prevents disk space issues on Render.com
        def cleanup():
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
            except:
                pass
        
        # Schedule cleanup after response
        if background_tasks:
            background_tasks.add_task(cleanup)
        
        # Return the converted file
        return FileResponse(
            output_path, 
            media_type="application/pdf", 
            filename=output_filename
        )
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "PDF Dark Mode Converter API is running"}

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
