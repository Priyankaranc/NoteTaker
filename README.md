# 📝 My Notes - Self-Hosted Note Taking App

A beautiful, mobile-friendly note-taking application that runs locally on your Raspberry Pi or any device. Access it from any device on your local network.

## ✨ Features

- **📝 Text Notes** - Write quick notes and thoughts
- **🔗 Link Storage** - Save URLs and links for later
- **📎 File Uploads** - Upload images, PDFs, videos, documents, and more
- **🕒 Timeline View** - All notes displayed in chronological order, newest first
- **🏷️ Tags** - Organize your notes with tags
- **🔍 Search** - Find notes quickly by content or tags
- **📱 Mobile-Friendly** - Beautiful responsive design that works on all devices
- **🖼️ Image Previews** - Automatic thumbnail display for images
- **⚡ Fast & Local** - All data stored locally using SQLite

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Access the app:**
   - On the same device: http://localhost:8000
   - From other devices on your network: http://YOUR_PI_IP:8000
   - Example: http://192.168.1.90:8000

### For Raspberry Pi Production Deployment

Run with Uvicorn for better performance:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

To run in the background:

```bash
nohup uvicorn app:app --host 0.0.0.0 --port 8000 &
```

## 📂 Project Structure

```
NoteTaking/
├── app.py              # FastAPI application
├── database.py         # SQLite database operations
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── static/
│   └── index.html     # Frontend UI
├── uploads/           # Uploaded files storage
└── notes.db          # SQLite database (created automatically)
```

## 🎯 Usage

### Creating Notes

1. **Text Note**: Write in the text area and click "Save Note"
2. **Link Note**: Paste a URL in the link field and save
3. **File Note**: Choose files to upload (supports multiple files)
4. **Tags**: Add comma-separated tags to organize your notes

### Searching

Use the search box to find notes by:
- Content text
- Tags
- Filenames

### Deleting Notes

Click the 🗑️ icon on any note card to delete it. Files will also be removed from storage.

## 🔧 Configuration

Edit `config.py` to customize:

- **MAX_UPLOAD_SIZE_MB**: Maximum file upload size (default: 50MB)
- **PORT**: Server port (default: 8000)
- **HOST**: Server host (default: 0.0.0.0 for LAN access)

## 📋 API Endpoints

The app exposes a REST API:

- `GET /` - Web interface
- `POST /api/notes` - Create a new note
- `GET /api/notes` - Get all notes (supports pagination and search)
- `GET /api/notes/{id}` - Get a specific note
- `DELETE /api/notes/{id}` - Delete a note
- `GET /files/{filename}` - Serve uploaded files
- `GET /api/health` - Health check

## 🗄️ Database Schema

SQLite database with a single `notes` table:

| Column      | Type    | Description                          |
|-------------|---------|--------------------------------------|
| id          | INTEGER | Primary key                          |
| note_type   | TEXT    | 'text', 'link', or 'file'           |
| content     | TEXT    | Note content or URL                  |
| file_name   | TEXT    | Original filename for uploads        |
| file_path   | TEXT    | Relative path to stored file         |
| mime_type   | TEXT    | MIME type of uploaded file           |
| tags        | TEXT    | Comma-separated tags                 |
| created_at  | TEXT    | ISO timestamp (UTC)                  |
| updated_at  | TEXT    | ISO timestamp (UTC)                  |

Files are stored on disk in the `uploads/` directory, not as blobs in the database.

## 🔒 Security Notes

- This app is designed for **local network use only**
- No authentication is implemented - only use on trusted networks
- Files are stored with unique UUIDs to prevent naming conflicts
- Directory traversal protection is implemented
- Maximum file size limits prevent abuse

## 🎨 Customization

### Changing Colors

Edit the CSS variables in `static/index.html`:

```css
:root {
    --primary: #6366f1;        /* Main color */
    --primary-dark: #4f46e5;   /* Darker shade */
    --success: #10b981;         /* Success messages */
    --danger: #ef4444;          /* Delete/error */
    /* ... more variables ... */
}
```

## 🐛 Troubleshooting

**Can't access from other devices?**
- Make sure your firewall allows connections on port 8000
- Use your Pi's local IP address, not localhost
- Check that devices are on the same network

**File uploads not working?**
- Check that the `uploads/` directory exists and is writable
- Verify file size is under the 50MB limit

**Database errors?**
- Delete `notes.db` to reset (you'll lose all notes)
- Check file permissions

## 📱 Mobile Usage

The app is fully responsive and works great on mobile:
- Add to home screen for app-like experience
- Touch-friendly buttons (minimum 48px)
- Smooth scrolling timeline
- Image zoom on tap

## 🔄 Backup

Your data consists of:
- `notes.db` - SQLite database
- `uploads/` - All uploaded files

Regularly backup these to preserve your notes.

## 📝 License

This is a personal project for local use. Feel free to modify and adapt to your needs.

## 🚀 Future Enhancements

Potential additions:
- Note editing capability
- Dark mode toggle
- Note categories/folders
- PWA support for offline access
- Export notes to markdown
- Rich text editor

---

Made with ❤️ for personal note-taking

