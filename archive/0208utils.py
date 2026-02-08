import os
import glob

def find_latest_data_file(directory_path=None):
    """Find the most recent gaze data file"""
    if directory_path is None:
        # Default to a common data directory if not specified
        # This assumes a structure where 'src' is sibling to 'data'
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..'))
        directory_path = os.path.join(project_root, 'data')

    # Look for files matching the pattern gaze_data_*.txt
    pattern = os.path.join(directory_path, "gaze_data_*.txt")
    data_files = glob.glob(pattern)
    
    if not data_files:
        # Fallback to old filename format
        old_file = os.path.join(directory_path, "gaze_data.txt")
        if os.path.exists(old_file):
            return old_file
        return None
    
    # Return the most recently modified file
    latest_file = max(data_files, key=os.path.getmtime)
    return latest_file