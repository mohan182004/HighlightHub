"""
Helper utilities for the Streamlit app
"""

import os
import tempfile
from typing import Optional
import requests


def get_env_variable(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable with optional default"""
    value = os.getenv(key, default)
    return value if value else default


def validate_file_size(file_size_bytes: int, max_size_mb: int) -> bool:
    """
    Validate if file size is within limits

    Args:
        file_size_bytes: File size in bytes
        max_size_mb: Maximum allowed size in MB

    Returns:
        True if valid, False otherwise
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size_bytes <= max_size_bytes


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def create_iframe_html(stream_url: str, width: str = "100%", height: str = "400px") -> str:
    """
    Create HTML iframe code for embedding video

    Args:
        stream_url: Video stream URL
        width: iframe width
        height: iframe height

    Returns:
        HTML string
    """
    return f"""
    <iframe 
        src="{stream_url}" 
        width="{width}" 
        height="{height}" 
        frameborder="0" 
        allow="autoplay; fullscreen; picture-in-picture" 
        allowfullscreen
        style="border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
    </iframe>
    """


def validate_video_file(file):
    allowed_extensions = ['mp4', 'avi', 'mov', 'mkv']
    if not file.name.split('.')[-1] in allowed_extensions:
        raise ValueError("Invalid file type. Please upload a video file.")
    return True


def format_url(url):
    if not url.startswith("http"):
        return f"http://{url}"
    return url


def save_uploaded_file(uploaded_file) -> str:
    """
    Save Streamlit uploaded file to temporary location

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        Path to saved file
    """
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def format_timestamp(seconds: float) -> str:
    """
    Format seconds into MM:SS format

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def format_time_range(start: float, end: float) -> str:
    """
    Format time range as MM:SS - MM:SS

    Args:
        start: Start time in seconds
        end: End time in seconds

    Returns:
        Formatted time range string
    """
    return f"{format_timestamp(start)} - {format_timestamp(end)}"


def validate_video_url(url: str) -> bool:
    """
    Validate if URL is accessible

    Args:
        url: Video URL

    Returns:
        True if valid, False otherwise
    """
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_impact_badge(score: float) -> str:
    """
    Get impact level badge based on score

    Args:
        score: Relevance score (0-1)

    Returns:
        Badge string with emoji
    """
    if score >= 0.8:
        return "🔥 VIRAL"
    elif score >= 0.7:
        return "⭐ HIGH IMPACT"
    elif score >= 0.6:
        return "✨ NOTABLE"
    else:
        return "📌 GOOD"