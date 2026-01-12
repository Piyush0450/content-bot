import os
import subprocess
import math
import logging
import json

def get_video_info(file_path):
    """
    Get video duration and size using ffprobe.
    """
    try:
        cmd = [
            'ffprobe', 
            '-v', 'quiet', 
            '-print_format', 'json', 
            '-show_format', 
            '-show_streams', 
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        format_info = data.get('format', {})
        duration = float(format_info.get('duration', 0))
        size = float(format_info.get('size', 0))
        return duration, size
    except Exception as e:
        logging.error(f"Error getting video info: {e}")
        return 0, 0

def split_video(file_path, max_size_mb=45):
    """
    Splits video into chunks less than max_size_mb.
    Returns a list of file paths.
    """
    if not os.path.exists(file_path):
        return []

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb <= max_size_mb:
        return [file_path]

    duration, _ = get_video_info(file_path)
    if duration == 0:
        logging.error("Could not determine video duration.")
        return [file_path] # Return original if we can't split

    num_parts = math.ceil(file_size_mb / max_size_mb)
    part_duration = duration / num_parts
    
    base_name, ext = os.path.splitext(file_path)
    output_files = []

    for i in range(num_parts):
        start_time = i * part_duration
        output_file = f"{base_name}_part{i+1}{ext}"
        
        # ffmpeg command to split
        # -ss before -i is faster seeking
        # -c copy avoids re-encoding (fast) but might be slightly inaccurate on cut points
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(start_time),
            '-i', file_path,
            '-t', str(part_duration),
            '-c', 'copy',
            output_file
        ]
        
        try:
            print(f"Creating part {i+1}/{num_parts}: {output_file}")
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            output_files.append(output_file)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error splitting part {i+1}: {e}")
    
    return output_files
