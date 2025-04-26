import ctypes
import win32clipboard as clipboard
import win32con
import os
from pydub import AudioSegment
import re  # Add this import for sorting by chapter numbers
import traceback  # Add this import for error handling
import pyperclip
import subprocess


import logging  # Add this import for logging
# Configure logging
logging.basicConfig(filename='runtime.log',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clear_clipboard():
    """
    Clears the clipboard.
    """
    clipboard.OpenClipboard()
    clipboard.EmptyClipboard()
    clipboard.CloseClipboard()

def copy_files_to_clipboard(file_paths):
    # Convert to double-null-terminated string (for multiple files)
    joined_paths = '\0'.join(file_paths) + '\0\0'
    encoded_paths = joined_paths.encode('utf-16le')

    # DROPFILES structure
    class DROPFILES(ctypes.Structure):
        _fields_ = [
            ('pFiles', ctypes.c_uint),
            ('pt', ctypes.c_long * 2),
            ('fNC', ctypes.c_int),
            ('fWide', ctypes.c_int),
        ]

    dropfiles = DROPFILES()
    dropfiles.pFiles = ctypes.sizeof(DROPFILES)
    dropfiles.pt = (0, 0)
    dropfiles.fNC = 0
    dropfiles.fWide = 1  # Unicode

    total_size = ctypes.sizeof(dropfiles) + len(encoded_paths)
    buffer = ctypes.create_string_buffer(total_size)

    # Copy the struct into buffer
    ctypes.memmove(buffer, ctypes.addressof(dropfiles), ctypes.sizeof(dropfiles))

    # Copy file paths after the struct
    ctypes.memmove(ctypes.addressof(buffer) + ctypes.sizeof(dropfiles), encoded_paths, len(encoded_paths))

    # Set clipboard data
    clipboard.OpenClipboard()
    clipboard.EmptyClipboard()
    clipboard.SetClipboardData(win32con.CF_HDROP, buffer)
    clipboard.CloseClipboard()

def get_absolute_path(file_path):
    """
    Returns the absolute path of the given file.
    """
    return os.path.abspath(file_path)

def merge_mp3_files_in_folder(folder_path, output_folder):
    """
    Merges all .mp3 files in the given folder into one file with the same name as the folder.
    The resulting file is saved in the specified output folder.
    """
    try:
        # Get all .mp3 files in the folder
        mp3_files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
        if not mp3_files:
            raise ValueError("No .mp3 files found in the folder.")

        # Sort files numerically based on the first number in the filename
        def extract_first_number(filename):
            # Extract all numbers from the filename
            numbers = re.findall(r'\d+', filename)
            
            # Convert all found numbers to integers
            # If no numbers found, use infinity for sorting
            if not numbers:
                return (float('inf'),)
            
            # Return tuple of all numbers found for multi-level sorting
            return tuple(int(num) for num in numbers)

        mp3_files.sort(key=extract_first_number)
        logging.info(f"Sorted .mp3 files: {mp3_files} in folder {folder_path}")
        combined_audio = AudioSegment.empty()
        for mp3_file in mp3_files:
            file_path = os.path.join(folder_path, mp3_file)
            audio = AudioSegment.from_file(file_path)
            combined_audio += audio
            logging.info(f"Added {mp3_file} to combined audio.")
        # Save the merged file in the output folder with the folder name
        output_file = os.path.join(output_folder, f"{os.path.basename(folder_path)}.mp3")
        combined_audio.export(output_file, format="mp3")
        print(f"Merged file saved as: {output_file}")
        logging.info(f"Merged file saved as: {output_file}")
    except Exception as e:
        print(f"Error merging .mp3 files: {e}")
        logging.error(f"Error merging .mp3 files: {traceback.format_exc()}")

def merge_all(base_folder):
    """
    Merges all .mp3 files in each subdirectory of the given base folder.
    Each merged file is moved to the base folder with the subdirectory name.
    """
    try:
        # Iterate through all subdirectories in the base folder
        for subdir in os.listdir(base_folder):
            subdir_path = os.path.join(base_folder, subdir)
            if os.path.isdir(subdir_path):  # Check if it's a directory
                mp3_files = [f for f in os.listdir(subdir_path) if f.endswith('.mp3')]
                if not mp3_files:
                    raise ValueError("No .mp3 files found in the folder.")

                # Sort files numerically based on the first number in the filename
                def extract_first_number(filename):
                    # Extract all numbers from the filename
                    numbers = re.findall(r'\d+', filename)
                    
                    # Convert all found numbers to integers
                    # If no numbers found, use infinity for sorting
                    if not numbers:
                        return (float('inf'),)
                    
                    # Return tuple of all numbers found for multi-level sorting
                    return tuple(int(num) for num in numbers)

                mp3_files.sort(key=extract_first_number)
                logging.info(f"Sorted .mp3 files: {mp3_files} in folder {subdir_path}")
                with open(os.path.join(subdir_path, "filelist.txt"), 'w') as f:
                    for mp3_file in mp3_files:
                        f.write(f"file '{mp3_file}'\n")
                print(f"Merging files in: {subdir_path}")
                cmd = fr'''cd "{subdir_path}" && ffmpeg -y -f concat -safe 0 -i filelist.txt -c copy "..\{subdir}.mp3" && cd ..\..'''
                subprocess.run(
                    cmd,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    # stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                print(f"Merged files in: {subdir_path} to {base_folder}\\{subdir}.mp3")
    except Exception as e:
        print(f"Error merging files in subdirectories: {e}")

# Example usage:

def save_clipboard_link(file_path="downloadLinks.txt"):
    # Read clipboard content
    clipboard_content = pyperclip.paste().strip()

    # Regex to check for a URL
    url_pattern = re.compile(
        r'^(https?://|www\.)[^\s/$.?#].[^\s]*$', re.IGNORECASE
    )

    if url_pattern.match(clipboard_content):
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(clipboard_content + '\n')
        logging.info(f"Saved link: {clipboard_content} to {file_path}")
        print(f"Link saved to {file_path}: {clipboard_content}")

        return True
    else:
        logging.info(f"Clipboard content {clipboard_content} is not a valid link.")
        print("Clipboard content is not a valid link.")

        return False

if __name__ == "__main__":
    try:
        # copy_files_to_clipboard(["D:\\FreelanceProjects\\Upwork\\JackyYu\\Descript\\modules\\utils.py"]) # Replace with your actual file path
        # print("File path copied to clipboard successfully.")
        # abs_path = get_absolute_path("utils.py")  # Replace with your actual file name
        # print(f"Absolute path: {abs_path}")
        base_folder = "inputFiles"  # Replace with your base folder path
        # merge_all(base_folder)
        audioFiles = os.listdir(base_folder)
        audioFiles = [f for f in audioFiles if f.endswith('.mp3')]
        copy_files_to_clipboard([get_absolute_path(os.path.join(base_folder, f)) for f in audioFiles])  # Copy merged files to clipboard
        print("File path copied to clipboard successfully.")
    except Exception as e:
        print(f"Error: {e}")
