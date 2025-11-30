from fastapi import FastAPI, File, UploadFile, HTTPException
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
async def convert_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    output_filename = f"dark_{file.filename}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        converter.convert(input_path, output_path)
        
        return FileResponse(
            output_path, 
            media_type="application/pdf", 
            filename=output_filename
        )
    except Exception as e:
        # Clean up if possible
        if os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
