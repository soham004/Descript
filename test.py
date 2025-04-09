import time
import logging
import os
import sys
import re
import pyperclip
# import ctypes
# # Allow the current process to set the foreground window
# ctypes.windll.user32.AllowSetForegroundWindow(-1)
# gw.getWindowsWithTitle("Warning:")[0].activate()
# time.sleep(5)
print(sys.argv)
logging.basicConfig(filename='file.log',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# audioFilename = "test.mp3"  # Replace with your audio filename
# exportFomat = "mp3"  # Replace with your desired export format
# file_path = os.path.join(os.getcwd(), "downloadedAudio", f"{audioFilename.split('.')[0]}.{exportFomat}")
# logging.info(f"File path: {file_path}")

# mergebase_folder = "inputFiles"
# # merge_all(mergebase_folder)
# audioFiles = os.listdir(mergebase_folder)
# audioFiles = [f for f in audioFiles if f.endswith('.mp3')]

# print(f"Audio files to be uploaded: {audioFiles}")

# with open('downloadLinks.txt', 'w') as f: # Clear the file content
#     f.write('')

# def save_clipboard_link(file_path="downloadLinks.txt"):
#     # Read clipboard content
#     clipboard_content = pyperclip.paste().strip()

#     # Regex to check for a URL
#     url_pattern = re.compile(
#         r'^(https?://|www\.)[^\s/$.?#].[^\s]*$', re.IGNORECASE
#     )

#     if url_pattern.match(clipboard_content):
#         with open(file_path, 'w', encoding='utf-8') as f:
#             f.write(clipboard_content + '\n')
#         logging.info(f"Saved link: {clipboard_content} to {file_path}")
#         print(f"Link saved: {clipboard_content}")
#     else:
#         logging.info("Clipboard content is not a valid link.")
#         print("Clipboard content is not a valid link.")

# save_clipboard_link()
