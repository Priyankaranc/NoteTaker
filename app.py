"""
FastAPI-based Note Taking Application
A local-only, self-hosted note-taking app with support for text, links, and file uploads.
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pathlib import Path
from contextlib import asynccontextmanager
import uuid
import mimetypes
from datetime import datetime
import os

import database

# Create necessary directories
UPLOAD_DIR = Path("uploads")
STATIC_DIR = Path("static")
UPLOAD_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    await database.init_db()
    print("✅ Database initialized")
    print(f"✅ Upload directory: {UPLOAD_DIR.absolute()}")
    print("🚀 Note-taking app is ready!")
    yield
    # Shutdown (if needed)
    print("👋 Shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Note Taking App",
    description="Local note-taking app with text, links, and file support",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for LAN access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local network access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML interface."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding='utf-8'), status_code=200)
    return HTMLResponse(content="<h1>Note Taking App</h1><p>Please create static/index.html</p>", status_code=200)


# Mount static files - must be last to avoid conflicts
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/api/notes")
async def create_note(
    content: Optional[str] = Form(None),
    link: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[])
):
    """
    Create a new note. Automatically detects note type:
    - If files are uploaded: creates file note(s)
    - If link is provided: creates link note
    - If content is provided: creates text note
    
    Supports multiple file uploads in a single request.
    """
    created_notes = []
    
    # Handle file uploads
    if files and len(files) > 0 and files[0].filename and files[0].filename != '':
        for file in files:
            if not file.filename:
                continue
                
            # Validate file size (50MB limit)
            file_content = await file.read()
            if len(file_content) > 50 * 1024 * 1024:  # 50MB
                raise HTTPException(status_code=413, detail=f"File {file.filename} is too large (max 50MB)")
            
            # Generate unique filename
            file_extension = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = UPLOAD_DIR / unique_filename
            
            # Save file to disk
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # Detect MIME type
            mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
            
            # Create database entry
            note_id = await database.create_note(
                note_type="file",
                content=content if content else None,
                file_name=file.filename,
                file_path=f"uploads/{unique_filename}",
                mime_type=mime_type,
                tags=tags
            )
            
            created_notes.append({
                "id": note_id,
                "note_type": "file",
                "file_name": file.filename,
                "message": "File uploaded successfully"
            })
    
    # Handle link note
    elif link:
        note_id = await database.create_note(
            note_type="link",
            content=link,
            tags=tags
        )
        created_notes.append({
            "id": note_id,
            "note_type": "link",
            "message": "Link saved successfully"
        })
    
    # Handle text note
    elif content:
        note_id = await database.create_note(
            note_type="text",
            content=content,
            tags=tags
        )
        created_notes.append({
            "id": note_id,
            "note_type": "text",
            "message": "Note saved successfully"
        })
    
    else:
        raise HTTPException(status_code=400, detail="No content, link, or files provided")
    
    return {
        "success": True,
        "notes": created_notes,
        "count": len(created_notes)
    }


@app.get("/api/notes")
async def get_notes(limit: int = 100, offset: int = 0, search: Optional[str] = None):
    """
    Retrieve all notes, newest first.
    
    Query parameters:
    - limit: Maximum number of notes to return (default: 100)
    - offset: Number of notes to skip for pagination (default: 0)
    - search: Optional search query to filter notes
    """
    if search:
        notes = await database.search_notes(search, limit)
    else:
        notes = await database.get_all_notes(limit, offset)
    
    total = await database.get_note_count()
    
    return {
        "success": True,
        "notes": notes,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@app.get("/api/notes/{note_id}")
async def get_note(note_id: int):
    """Retrieve a single note by ID."""
    note = await database.get_note_by_id(note_id)
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {
        "success": True,
        "note": note
    }


@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int):
    """Delete a note by ID. Also deletes associated file if it exists."""
    # Get note to check if it has an associated file
    note = await database.get_note_by_id(note_id)
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Delete file if it exists
    if note.get("file_path"):
        file_path = Path(note["file_path"])
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                print(f"⚠️ Could not delete file {file_path}: {e}")
    
    # Delete from database
    deleted = await database.delete_note(note_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {
        "success": True,
        "message": "Note deleted successfully"
    }


@app.get("/files/{filename}")
async def serve_file(filename: str):
    """Serve uploaded files with proper MIME types."""
    # Prevent directory traversal attacks
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Detect MIME type
    mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    
    return FileResponse(
        path=file_path,
        media_type=mime_type,
        filename=filename
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    note_count = await database.get_note_count()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "note_count": note_count
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Note-Taking App...")
    print("📝 Access the app at: http://0.0.0.0:8000")
    print("📱 From other devices: http://<your-pi-ip>:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
