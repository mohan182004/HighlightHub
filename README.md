# 🎬 AI Viral Moment Extractor

An intelligent Streamlit application that automatically extracts the 3 most impactful moments from any video using VideoDB's AI-powered scene analysis and generates clips with auto-subtitles.

## ✨ Features

- 🎬 **Scene-Based Extraction**: Automatically detects and analyzes video scenes using shot-based detection
- 🎯 **Smart Ranking**: Scores scenes based on duration, position, and content quality
- 📱 **Social Media Ready**: Generates 30-second clips optimized for Reels/TikTok/Shorts
- 💬 **Auto-Subtitles**: Adds yellow subtitles with black outline (added during upload)
- 🎨 **Impact Scoring**: Ranks moments by viral potential (duration, diversity, content richness)
- 📥 **Easy Export**: Preview and download clips individually

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- VideoDB API key ([Get one here](https://videodb.io))

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd streamlit-video-moments
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Add your VideoDB API key to `.env`:
```
API_KEY=your_actual_api_key_here
```

### Run the App

```bash
streamlit run src/app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 How It Works

### Workflow

1. **Upload Video**
   - Upload a video file (mp4, avi, mov, mkv) or provide a URL
   - Video is uploaded to VideoDB cloud
   - **Spoken words are indexed** for transcript generation
   - **Subtitles are automatically added** to the entire video (yellow text, black outline)

2. **Scene Extraction**
   - Video scenes are extracted using shot-based detection (threshold: 27)
   - Each scene is analyzed by AI
   - Scene boundaries are identified based on visual changes

3. **Scene Ranking**
   - Each scene is scored based on multiple factors:
     - **Duration Score** (0.3): Prefers 10-60 second scenes
     - **Position Score** (0.2): Favors middle 60% of video
     - **Content Score** (0.3): Scenes with AI descriptions get higher scores
     - **Description Quality** (0.1-0.2): Longer descriptions indicate richer content
     - **Diversity Bonus** (0.1): Base score for all scenes

4. **Smart Selection**
   - Top-scored scenes are selected
   - **30-second minimum gap** enforced between clips (prevents clustering)
   - Up to 3 diverse moments chosen chronologically
   - Each moment includes AI-generated scene description

5. **Generate Clips**
   - 30-second clips created from selected moments
   - **Subtitles automatically included** (from video upload step)
   - Clips inherit subtitle styling from parent video
   - Stream URLs generated for playback and download

6. **Preview & Download**
   - Watch clips directly in browser
   - View impact scores and time ranges
   - Download clips individually
   - Ready for immediate social media posting

## 🛠️ Technical Stack

- **Frontend**: Streamlit (Python web framework)
- **Video Processing**: VideoDB Python SDK
- **Scene Detection**: Shot-based extraction (threshold: 27)
- **Subtitles**: Auto-generated from indexed transcripts
- **AI Analysis**: VideoDB's scene indexing and description generation
- **Storage**: VideoDB cloud (no local storage needed)

## 🔧 Configuration

### Environment Variables

```bash
API_KEY=your_videodb_api_key
```