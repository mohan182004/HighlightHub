"""
Streamlit app for extracting impactful video moments using VideoDB
"""
import streamlit as st
import os
from dotenv import load_dotenv
from video_processor import VideoProcessor
from utils.helpers import (
    save_uploaded_file, 
    format_time_range, 
    validate_video_url,
    get_impact_badge
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Viral Moment Extractor",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .clip-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header">
        <h1>🎬 AI Viral Moment Extractor</h1>
        <p>Powered by VideoDB AI | Extract 3 Most Impactful Moments with Auto-Subtitles</p>
    </div>
""", unsafe_allow_html=True)

# Initialize session state
if 'video_processor' not in st.session_state:
    api_key = os.getenv('API_KEY')
    if not api_key:
        st.error("⚠️ API_KEY not found! Please set it in your .env file")
        st.stop()
    st.session_state.video_processor = VideoProcessor(api_key)

if 'video' not in st.session_state:
    st.session_state.video = None
if 'viral_moments' not in st.session_state:
    st.session_state.viral_moments = None
if 'generated_clips' not in st.session_state:
    st.session_state.generated_clips = []

# Main app
def main():
    processor = st.session_state.video_processor
    
    # Step 1: Video Input
    st.header("📤 Step 1: Upload Your Video")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Video File")
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=['mp4', 'avi', 'mov', 'mkv'],
            help="Upload a video file from your device"
        )
        
        if uploaded_file and st.button("🚀 Process Uploaded Video", key="upload_btn"):
            with st.spinner("Uploading video and adding subtitles..."):
                try:
                    temp_path = save_uploaded_file(uploaded_file)
                    video = processor.upload_video(temp_path, is_url=False)
                    st.session_state.video = video
                    st.success(f"✅ Video uploaded with subtitles! ID: {video.id}")
                    os.remove(temp_path)  # Clean up temp file
                except Exception as e:
                    st.error(f"❌ Error uploading video: {str(e)}")
    
    with col2:
        st.subheader("Or Use Video URL")
        video_url = st.text_input(
            "Enter video URL",
            placeholder="https://example.com/video.mp4 or YouTube URL",
            help="Provide a direct link to a video file or YouTube URL"
        )
        
        if video_url and st.button("🚀 Process Video URL", key="url_btn"):
            if not validate_video_url(video_url):
                st.warning("⚠️ URL might not be accessible. Trying anyway...")
            
            with st.spinner("Uploading video from URL and adding subtitles..."):
                try:
                    video = processor.upload_video(video_url, is_url=True)
                    st.session_state.video = video
                    st.success(f"✅ Video uploaded with subtitles! ID: {video.id}")
                except Exception as e:
                    st.error(f"❌ Error uploading video: {str(e)}")
    
    # Step 2: AI Analysis and Extraction
    if st.session_state.video:
        st.divider()
        st.header("🤖 Step 2: AI-Powered Moment Extraction")
        
        video = st.session_state.video
        video_info = processor.get_video_info(video)
        
        # Display video info
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.metric("Video Name", video_info['name'] or "Untitled")
        with col2:
            st.metric("Duration", f"{int(video_info['length'])}s")
        with col3:
            st.metric("Video ID", video_info['id'][:12] + "...")
        
        # Extract moments button
        if st.button("✨ Extract Viral Moments with AI", type="primary", use_container_width=True):
            with st.spinner("🔍 Analyzing video with AI... This may take a few minutes..."):
                try:
                    # Extract viral moments
                    viral_moments = processor.extract_viral_moments(video, clip_duration=30)
                    st.session_state.viral_moments = viral_moments
                    
                    st.balloons()
                    st.success("🎉 AI Analysis Complete! Found impactful moments with auto-subtitles!")
                    
                except Exception as e:
                    st.error(f"❌ Error during extraction: {str(e)}")
    
    # Step 3: Display and Generate Clips
    if st.session_state.viral_moments:
        st.divider()
        st.header("🎬 Step 3: Your Viral Moments")
        
        viral_moments = st.session_state.viral_moments
        
        # Display each moment
        for idx, moment in enumerate(viral_moments, 1):
            with st.container():
                st.markdown(f"<div class='clip-card'>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader(f"Moment #{idx}")
                    st.write(f"**Scene:** {moment['query']}")
                    st.write(f"**Time Range:** {format_time_range(moment['start'], moment['end'])}")
                    st.write(f"**Impact Score:** {get_impact_badge(moment['score'])} ({moment['score']:.2f})")
                
                with col2:
                    if st.button(f"🎥 Generate Clip #{idx}", key=f"gen_{idx}"):
                        with st.spinner(f"Generating clip #{idx} with subtitles..."):
                            try:
                                stream_url = processor.generate_clip(
                                    video=st.session_state.video,
                                    start_time=moment['start'],
                                    end_time=moment['end'],
                                    clip_name=f"viral_moment_{idx}"
                                )
                                
                                # Store generated clip
                                clip_info = {
                                    'idx': idx,
                                    'stream_url': stream_url,
                                    'moment': moment
                                }
                                
                                if clip_info not in st.session_state.generated_clips:
                                    st.session_state.generated_clips.append(clip_info)
                                
                                st.success(f"✅ Clip #{idx} generated with subtitles!")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error generating clip: {str(e)}")
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    # Step 4: Preview and Download Clips
    if st.session_state.generated_clips:
        st.divider()
        st.header("📥 Step 4: Preview & Download")
        
        for clip in st.session_state.generated_clips:
            with st.expander(f"🎬 Clip #{clip['idx']} - {clip['moment']['query'][:30]}...", expanded=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.video(clip['stream_url'])
                
                with col2:
                    st.markdown(f"""
                    **Clip Details:**
                    - Time: {format_time_range(clip['moment']['start'], clip['moment']['end'])}
                    - Impact: {get_impact_badge(clip['moment']['score'])}
                    - Duration: 30 seconds
                    - Auto-Captions: ✅ Enabled
                    - Style: Yellow text, black outline
                    """)
                    
                    st.link_button(
                        "📥 Download Clip",
                        clip['stream_url'],
                        use_container_width=True
                    )
        
        # Export all button
        st.divider()
        st.success("🎉 All clips ready with auto-subtitles! Download them individually or share directly to social media.")

# Footer
st.divider()
st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>Made with ❤️ using VideoDB AI | Perfect for creating viral social media content</p>
    </div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()