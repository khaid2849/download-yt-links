#!/usr/bin/env python3
"""
YouTube Video Downloader Script
Downloads a list of YouTube videos to a specified folder.
"""

import os
import sys
from pathlib import Path
import yt_dlp
from urllib.parse import urlparse

def is_valid_youtube_url(url):
    """Check if the URL is a valid YouTube URL."""
    parsed = urlparse(url)
    return parsed.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be', 'm.youtube.com']

def download_youtube_videos(video_urls, output_folder):
    """
    Download YouTube videos from a list of URLs to the specified folder.
    
    Args:
        video_urls (list): List of YouTube video URLs
        output_folder (str): Path to the output folder
    """
    
    # Create output folder if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Configure yt-dlp options for best quality
    ydl_opts = {
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Best quality, prefer mp4
        'noplaylist': True,  # Only download single video, not playlist
        'ignoreerrors': True,  # Continue on download errors
        'no_warnings': False,
        'merge_output_format': 'mp4',  # Merge video and audio into mp4
        'embed_subs': True,  # Embed subtitles if available
        'writesubtitles': False,
        'writeautomaticsub': False,
    }
    
    successful_downloads = 0
    failed_downloads = 0
    
    print(f"Starting download of {len(video_urls)} videos to folder: {output_folder}")
    print("-" * 60)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(video_urls, 1):
            url = url.strip()
            
            # Skip empty lines
            if not url:
                continue
                
            # Validate YouTube URL
            if not is_valid_youtube_url(url):
                print(f"[{i}] ❌ Invalid YouTube URL: {url}")
                failed_downloads += 1
                continue
            
            try:
                print(f"[{i}] 📥 Downloading: {url}")
                
                # Extract video info first
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Unknown Title')
                duration = info.get('duration', 0)
                resolution = info.get('height', 'Unknown')
                fps = info.get('fps', 'Unknown')
                
                # Format duration
                if duration:
                    minutes = duration // 60
                    seconds = duration % 60
                    duration_str = f"{minutes}:{seconds:02d}"
                else:
                    duration_str = "Unknown"
                
                print(f"    Title: {video_title}")
                print(f"    Duration: {duration_str}")
                print(f"    Resolution: {resolution}p @ {fps}fps" if resolution != 'Unknown' else "    Resolution: Unknown")
                
                # Download the video
                ydl.download([url])
                print(f"    ✅ Successfully downloaded!")
                successful_downloads += 1
                
            except Exception as e:
                print(f"    ❌ Failed to download: {str(e)}")
                failed_downloads += 1
            
            print("-" * 60)
    
    # Print summary
    print(f"\n📊 Download Summary:")
    print(f"   ✅ Successful: {successful_downloads}")
    print(f"   ❌ Failed: {failed_downloads}")
    print(f"   📁 Output folder: {os.path.abspath(output_folder)}")

def read_urls_from_file(file_path):
    """Read URLs from a text file, one URL per line."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f.readlines() if line.strip()]
        return urls
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return []
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return []

def main():
    """Main function to handle command line arguments and execute downloads."""
    
    print("🎬 YouTube Video Downloader")
    print("=" * 40)
    
    # Method 1: Command line arguments
    if len(sys.argv) >= 3:
        if sys.argv[1] == '--file':
            # Read URLs from file
            urls_file = sys.argv[2]
            output_folder = sys.argv[3] if len(sys.argv) > 3 else 'downloads'
            
            print(f"📄 Reading URLs from file: {urls_file}")
            video_urls = read_urls_from_file(urls_file)
            
            if not video_urls:
                print("❌ No valid URLs found in file.")
                return
                
        else:
            # URLs provided as command line arguments
            video_urls = sys.argv[1:-1]  # All arguments except the last one
            output_folder = sys.argv[-1]  # Last argument is the folder name
    
    # Method 2: Interactive input
    else:
        print("Enter YouTube video URLs (one per line, press Enter twice to finish):")
        video_urls = []
        while True:
            url = input().strip()
            if not url:
                break
            video_urls.append(url)
        
        if not video_urls:
            print("❌ No URLs provided.")
            return
        
        output_folder = input("Enter output folder name: ").strip()
        if not output_folder:
            output_folder = 'downloads'
    
    # Start downloading
    if video_urls:
        download_youtube_videos(video_urls, output_folder)
    else:
        print("❌ No URLs to download.")

if __name__ == "__main__":
    # Check if yt-dlp is installed
    try:
        import yt_dlp
    except ImportError:
        print("❌ yt-dlp is not installed. Please install it using:")
        print("   pip install yt-dlp")
        sys.exit(1)
    
    main()