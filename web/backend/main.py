"""
FastAPI Backend for PDF Accessibility Web Application
Wraps the shared PDF engine for web use
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn
import tempfile
import os
import uuid
import sys
from datetime import datetime, timedelta
import asyncio

# Add the project root to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(backend_dir))
sys.path.append(project_root)

# Import your shared engine
from shared.pdf_engine import PDFAccessibilityEngine, FileManager


app = FastAPI(
    title="PDF Accessibility Service",
    description="Professional PDF accessibility enhancement service",
    version="1.0.0"
)

# Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://*.vercel.app",   # Vercel deployments
        "https://pdf-accessibility-pro.vercel.app",  # Your production domain
        "https://yourdomain.com"  # Custom domain when you get one
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo (use Redis/Database in production)
processing_jobs = {}
job_progress = {}


class ProcessingRequest(BaseModel):
    """PDF processing configuration"""
    metadata: Dict[str, Any] = {}
    modifications: Dict[str, Any] = {}
    options: Dict[str, Any] = {}


class JobStatus(BaseModel):
    """Job status response"""
    job_id: str
    status: str  # "processing", "completed", "failed"
    progress: int
    message: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "PDF Accessibility API",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload",
            "analyze": "/analyze/{job_id}",
            "process": "/process/{job_id}",
            "download": "/download/{job_id}",
            "view": "/view/{job_id}",
            "status": "/status/{job_id}"
        }
    }


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload PDF for processing"""
    
    # Validate file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    if file.size > 100 * 1024 * 1024:  # 100MB limit
        raise HTTPException(status_code=400, detail="File too large (max 100MB)")
    
    try:
        # Create temporary file
        temp_file = FileManager.create_temp_file(suffix=".pdf")
        
        # Save uploaded file
        with open(temp_file, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create job ID
        job_id = str(uuid.uuid4())
        
        # Store job info
        processing_jobs[job_id] = {
            "id": job_id,
            "filename": file.filename,
            "temp_path": temp_file,
            "status": "uploaded",
            "created": datetime.now(),
            "size": len(content)
        }
        
        job_progress[job_id] = {
            "progress": 0,
            "message": "File uploaded successfully",
            "step": "uploaded"
        }
        
        return {
            "job_id": job_id,
            "filename": file.filename,
            "size": len(content),
            "status": "uploaded",
            "message": "File uploaded successfully. Use /analyze/{job_id} to analyze the PDF."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/analyze/{job_id}")
async def analyze_pdf(job_id: str, background_tasks: BackgroundTasks):
    """Analyze uploaded PDF for accessibility issues"""
    
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = processing_jobs[job_id]
    
    if job["status"] != "uploaded":
        raise HTTPException(status_code=400, detail="PDF must be uploaded first")
    
    # Start background analysis
    background_tasks.add_task(run_analysis, job_id)
    
    # Update status
    job["status"] = "analyzing"
    job_progress[job_id] = {
        "progress": 10,
        "message": "Analysis started",
        "step": "analyzing"
    }
    
    return {
        "job_id": job_id,
        "status": "analyzing",
        "message": "PDF analysis started. Check /status/{job_id} for progress."
    }


@app.post("/process/{job_id}")
async def process_pdf(job_id: str, request: ProcessingRequest, background_tasks: BackgroundTasks):
    """Process PDF with accessibility improvements"""
    
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = processing_jobs[job_id]
    
    if job["status"] not in ["analyzed", "completed"]:
        raise HTTPException(status_code=400, detail="PDF must be analyzed first")
    
    # Start background processing
    background_tasks.add_task(run_processing, job_id, request.dict())
    
    # Update status
    job["status"] = "processing"
    job_progress[job_id] = {
        "progress": 10,
        "message": "Processing started",
        "step": "processing"
    }
    
    return {
        "job_id": job_id,
        "status": "processing", 
        "message": "PDF processing started. Check /status/{job_id} for progress."
    }


@app.get("/status/{job_id}")
async def get_job_status(job_id: str) -> JobStatus:
    """Get processing status for a job"""
    
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = processing_jobs[job_id]
    progress = job_progress.get(job_id, {})
    
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        progress=progress.get("progress", 0),
        message=progress.get("message", ""),
        result=job.get("result"),
        error=job.get("error")
    )


@app.get("/download/{job_id}")
async def download_result(job_id: str, inline: bool = False):
    """Download processed PDF or view original PDF inline"""
    
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = processing_jobs[job_id]
    
    # If requesting inline view, serve the original uploaded file
    if inline:
        if job["status"] not in ["uploaded", "analyzed", "processing", "completed"]:
            raise HTTPException(status_code=400, detail="PDF not available for viewing")
        
        temp_path = job["temp_path"]
        if not os.path.exists(temp_path):
            raise HTTPException(status_code=500, detail="Original file missing")
        
        return FileResponse(
            temp_path,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline",
                "Content-Type": "application/pdf"
            }
        )
    
    # Otherwise, serve the processed file for download
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Processing not completed")

    if "output_path" not in job:
        raise HTTPException(status_code=500, detail="Output file not found")

    output_path = job["output_path"]

    if not os.path.exists(output_path):
        raise HTTPException(status_code=500, detail="Output file missing")

    # Return file for download
    filename = f"accessible_{job['filename']}"
    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/view/{job_id}")
async def view_pdf(job_id: str):
    """View original uploaded PDF (for PDF viewer embedding)"""
    
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = processing_jobs[job_id]
    
    # Allow viewing after upload (don't require processing completion)
    if job["status"] not in ["uploaded", "analyzed", "processing", "completed"]:
        raise HTTPException(status_code=400, detail="PDF not available for viewing")
    
    temp_path = job["temp_path"]
    
    if not os.path.exists(temp_path):
        raise HTTPException(status_code=500, detail="Original file missing")
    
    # Return file for inline viewing (not download)
    return FileResponse(
        temp_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline",
            "Content-Type": "application/pdf"
        }
    )


async def run_analysis(job_id: str):
    """Background task for PDF analysis"""
    
    try:
        job = processing_jobs[job_id]
        engine = PDFAccessibilityEngine()
        
        # Set up progress callback
        def progress_callback(step: str, message: str, progress: int):
            job_progress[job_id] = {
                "progress": progress,
                "message": message,
                "step": step
            }
        
        engine.set_progress_callback(progress_callback)
        
        # Run analysis
        result = engine.analyze_pdf(job["temp_path"])
        
        # Update job
        job["status"] = "analyzed"
        job["analysis"] = result
        job_progress[job_id] = {
            "progress": 100,
            "message": "Analysis complete",
            "step": "analyzed"
        }
        
    except Exception as e:
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["error"] = str(e)
        job_progress[job_id] = {
            "progress": 0,
            "message": f"Analysis failed: {str(e)}",
            "step": "failed"
        }


async def run_processing(job_id: str, request_data: Dict[str, Any]):
    """Background task for PDF processing"""
    
    try:
        job = processing_jobs[job_id]
        engine = PDFAccessibilityEngine()
        
        # Set up progress callback
        def progress_callback(step: str, message: str, progress: int):
            job_progress[job_id] = {
                "progress": progress,
                "message": message,
                "step": step
            }
        
        engine.set_progress_callback(progress_callback)
        
        # Create output file
        output_path = FileManager.create_temp_file(suffix="_accessible.pdf")
        
        # Run processing
        result = engine.process_pdf(
            job["temp_path"],
            request_data,
            output_path
        )
        
        if result["status"] == "success":
            # Update job
            job["status"] = "completed"
            job["output_path"] = output_path
            job["result"] = result
            job_progress[job_id] = {
                "progress": 100,
                "message": "Processing complete",
                "step": "completed"
            }
        else:
            job["status"] = "failed"
            job["error"] = result.get("error", "Processing failed")
            job_progress[job_id] = {
                "progress": 0,
                "message": f"Processing failed: {result.get('error', 'Unknown error')}",
                "step": "failed"
            }
        
    except Exception as e:
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["error"] = str(e)
        job_progress[job_id] = {
            "progress": 0,
            "message": f"Processing failed: {str(e)}",
            "step": "failed"
        }


@app.on_event("startup")
async def startup_event():
    """Clean up old jobs on startup"""
    print("🚀 PDF Accessibility API starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up temporary files on shutdown"""
    print("🧹 Cleaning up temporary files...")
    temp_files = []
    for job in processing_jobs.values():
        if "temp_path" in job:
            temp_files.append(job["temp_path"])
        if "output_path" in job:
            temp_files.append(job["output_path"])
    
    FileManager.cleanup_temp_files(temp_files)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
