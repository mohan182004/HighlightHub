"""
Video processing module using VideoDB SDK
"""
import videodb
from videodb import SubtitleStyle, SubtitleAlignment, SceneExtractionType
import os
from typing import List, Dict
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoProcessor:
    """Handles all VideoDB operations for viral moment extraction"""
    
    def __init__(self, api_key: str):
        """Initialize VideoDB connection"""
        logger.info("Initializing VideoProcessor...")
        self.conn = videodb.connect(api_key=api_key)
        self.collection = self.conn.get_collection()
        logger.info("VideoDB connection established successfully")
    
    def upload_video(self, source, is_url: bool = False):
        """
        Upload video to VideoDB, index spoken words, and add subtitles
        
        Args:
            source: File path or URL
            is_url: Whether source is a URL
            
        Returns:
            Video object with subtitles
        """
        try:
            if is_url:
                logger.info(f"Uploading video from URL: {source[:50]}...")
                video = self.collection.upload(url=source)
            else:
                logger.info(f"Uploading video from file: {source}")
                video = self.collection.upload(file_path=source)
            
            logger.info(f"Video uploaded successfully. Video ID: {video.id}")
            
            # Step 1: Index spoken words (required for subtitles)
            logger.info("Indexing spoken words in video...")
            video.index_spoken_words()
            logger.info("✅ Spoken words indexed successfully")
            
            # Step 2: Add subtitles after indexing
            logger.info("Adding auto-generated subtitles to video...")
            subtitle_style = SubtitleStyle(
                font_size=24,
                primary_colour="&H00FFFF00",  # Yellow
                outline_colour="&H00000000",  # Black outline
                back_colour="&H00000000",     # Transparent background
                bold=True,
                alignment=SubtitleAlignment.bottom_center,  # Fixed: bottom_center instead of bottom_mid
                margin_v=50
            )
            
            video.add_subtitle(style=subtitle_style)
            logger.info("✅ Subtitles added to video successfully")
            
            return video
        except Exception as e:
            logger.error(f"Failed to upload video or add subtitles: {str(e)}")
            raise
    
    def extract_viral_moments(
        self, 
        video, 
        clip_duration: int = 30
    ) -> List[Dict]:
        """
        Extract 3 most impactful moments from video using direct scene analysis
        
        Args:
            video: VideoDB Video object
            clip_duration: Duration of each clip in seconds
            
        Returns:
            List of clip information dictionaries
        """
        # Step 1: Extract scenes using shot-based detection
        logger.info("🎬 Extracting scenes from video...")
        try:
            scene_collection = video.extract_scenes(
                extraction_type=SceneExtractionType.shot_based,
                extraction_config={"threshold": 27}
            )
            
            # Check if scene_collection is valid
            if scene_collection is None:
                logger.error("❌ Scene extraction returned None")
                raise ValueError("Scene extraction failed - returned None")
            
            # Check if scenes attribute exists and is not None
            if not hasattr(scene_collection, 'scenes') or scene_collection.scenes is None:
                logger.error("❌ Scene collection has no scenes attribute or it's None")
                raise ValueError("Scene collection is invalid - no scenes found")
            
            scenes = scene_collection.scenes
            scene_count = len(scenes) if scenes else 0
            
            logger.info(f"✅ Extracted {scene_count} scenes")
            
            # Check if we have any scenes
            if scene_count == 0:
                logger.error("❌ No scenes were extracted from the video")
                raise ValueError("No scenes found in video - try a different video or lower threshold")
            
        except Exception as e:
            logger.error(f"❌ Scene extraction failed: {str(e)}")
            raise
        
        # Step 2: Rank scenes by various criteria
        logger.info("🎯 Analyzing and ranking scenes...")
        scored_scenes = []
        
        for idx, scene in enumerate(scenes):
            try:
                # Calculate scene score based on multiple factors
                score = 0.0
                
                # Factor 1: Scene duration (prefer 10-60 second scenes)
                scene_duration = scene.end - scene.start
                if 10 <= scene_duration <= 60:
                    score += 0.3
                elif 5 <= scene_duration <= 90:
                    score += 0.1
                
                # Factor 2: Position in video (prefer middle sections)
                position_ratio = scene.start / video.length
                if 0.2 <= position_ratio <= 0.8:  # Middle 60% of video
                    score += 0.2
                
                # Factor 3: Scene has description (AI analyzed it)
                description = getattr(scene, 'description', None)
                if description and isinstance(description, str) and len(description) > 0:
                    score += 0.3
                    # Prefer scenes with longer descriptions (more content)
                    desc_length = len(description)
                    if desc_length > 50:
                        score += 0.1
                    if desc_length > 100:
                        score += 0.1
                
                # Factor 4: Scene diversity (not too close to other scenes)
                score += 0.1  # Base diversity score
                
                # Use safe description
                safe_description = description if description else f'Scene at {scene.start:.1f}s'
                
                scored_scenes.append({
                    'scene': scene,
                    'start': scene.start,
                    'end': min(scene.start + clip_duration, video.length),
                    'duration': scene_duration,
                    'score': score,
                    'description': safe_description,
                    'position_ratio': position_ratio
                })
                
            except Exception as e:
                logger.warning(f"⚠️ Skipping scene at {scene.start:.1f}s due to error: {str(e)}")
                continue
        
        logger.info(f"✅ Successfully scored {len(scored_scenes)} out of {len(scenes)} scenes")
        
        # Step 3: Sort by score and select diverse moments
        scored_scenes.sort(key=lambda x: x['score'], reverse=True)
        
        # Select 3 diverse moments (not too close together)
        selected_moments = []
        min_time_gap = 30  # Minimum 30 seconds between clips
        
        for scene_data in scored_scenes:
            # Check if this scene is far enough from already selected scenes
            is_diverse = True
            for selected in selected_moments:
                time_diff = abs(scene_data['start'] - selected['start'])
                if time_diff < min_time_gap:
                    is_diverse = False
                    break
            
            if is_diverse:
                selected_moments.append({
                    'query': scene_data['description'][:50] + '...' if len(scene_data['description']) > 50 else scene_data['description'],
                    'start': scene_data['start'],
                    'end': scene_data['end'],
                    'score': scene_data['score'],
                    'search_result': None
                })
                logger.info(f"✅ Selected scene at {scene_data['start']:.1f}s - Score: {scene_data['score']:.3f}")
            
            if len(selected_moments) >= 3:
                break
        
        # Step 4: Check if we have enough moments
        if len(selected_moments) == 0:
            logger.error("❌ No diverse moments could be selected")
            raise ValueError("Could not find any suitable moments in the video")
        
        if len(selected_moments) < 3:
            logger.warning(f"⚠️ Only found {len(selected_moments)} diverse moments (expected 3)")
        
        # Step 5: Sort final moments chronologically
        selected_moments.sort(key=lambda x: x['start'])
        
        logger.info(f"✅ Selected {len(selected_moments)} viral moments:")
        for idx, moment in enumerate(selected_moments, 1):
            logger.info(f"  {idx}. {moment['query']} - Score: {moment['score']:.3f}, Time: {moment['start']:.1f}s-{moment['end']:.1f}s")
        
        return selected_moments[:3]
    
    def generate_clip(
        self, 
        video, 
        start_time: float, 
        end_time: float,
        clip_name: str
    ) -> str:
        """
        Generate a clip with auto-captions (subtitles already added to video)
        
        Args:
            video: VideoDB Video object (with subtitles already added)
            start_time: Start time in seconds
            end_time: End time in seconds
            clip_name: Name for the clip
            
        Returns:
            Stream URL for the clip
        """
        try:
            logger.info(f"Generating clip '{clip_name}': {start_time:.1f}s - {end_time:.1f}s")
            
            # Generate clip from video (subtitles already added during upload)
            logger.info("Generating clip with timeline...")
            clip_stream = video.generate_stream(timeline=[(start_time, end_time)])
            
            logger.info(f"✅ Clip with subtitles generated: {clip_stream}")
            return clip_stream
        
        except Exception as e:
            logger.error(f"❌ Failed to generate clip '{clip_name}': {str(e)}")
            raise
    
    def get_video_info(self, video) -> Dict:
        """Get basic video information"""
        try:
            info = {
                'id': video.id,
                'name': video.name,
                'length': video.length,
                'stream_url': video.stream_url,
                'player_url': video.player_url,
                'thumbnail_url': video.thumbnail_url
            }
            logger.info(f"Retrieved video info for ID: {video.id}")
            logger.debug(f"Video details: name={video.name}, length={video.length}s")
            return info
        except Exception as e:
            logger.error(f"Failed to get video info: {str(e)}")
            raise