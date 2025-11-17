"""
Database module for note-taking app using SQLite.
Handles all database operations with async support.
"""
import aiosqlite
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

DATABASE_PATH = "data/notes.db"


async def init_db():
    """Initialize the database and create tables if they don't exist."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_type TEXT NOT NULL,
                content TEXT,
                file_name TEXT,
                file_path TEXT,
                mime_type TEXT,
                tags TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await db.commit()


async def create_note(
    note_type: str,
    content: Optional[str] = None,
    file_name: Optional[str] = None,
    file_path: Optional[str] = None,
    mime_type: Optional[str] = None,
    tags: Optional[str] = None
) -> int:
    """
    Create a new note in the database.
    
    Args:
        note_type: Type of note ('text', 'link', or 'file')
        content: Text content or URL
        file_name: Original filename for uploaded files
        file_path: Relative path to stored file
        mime_type: MIME type of the file
        tags: Comma-separated tags
    
    Returns:
        ID of the created note
    """
    now = datetime.utcnow().isoformat()
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO notes (note_type, content, file_name, file_path, mime_type, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (note_type, content, file_name, file_path, mime_type, tags, now, now))
        await db.commit()
        return cursor.lastrowid


async def get_all_notes(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Retrieve all notes, newest first.
    
    Args:
        limit: Maximum number of notes to return
        offset: Number of notes to skip (for pagination)
    
    Returns:
        List of note dictionaries
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM notes
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_note_by_id(note_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single note by ID.
    
    Args:
        note_id: ID of the note
    
    Returns:
        Note dictionary or None if not found
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM notes WHERE id = ?
        """, (note_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def delete_note(note_id: int) -> bool:
    """
    Delete a note by ID.
    
    Args:
        note_id: ID of the note to delete
    
    Returns:
        True if deleted, False if not found
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        await db.commit()
        return cursor.rowcount > 0


async def search_notes(query: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Search notes by content or tags.
    
    Args:
        query: Search query string
        limit: Maximum number of results
    
    Returns:
        List of matching note dictionaries
    """
    search_pattern = f"%{query}%"
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM notes
            WHERE content LIKE ? OR tags LIKE ? OR file_name LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (search_pattern, search_pattern, search_pattern, limit)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_note_count() -> int:
    """Get total number of notes in the database."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM notes") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

