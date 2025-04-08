import time
import logging
import os
# import ctypes
# # Allow the current process to set the foreground window
# ctypes.windll.user32.AllowSetForegroundWindow(-1)
# gw.getWindowsWithTitle("Warning:")[0].activate()
# time.sleep(5)

logging.basicConfig(filename='file.log',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
audioFilename = "test.mp3"  # Replace with your audio filename
exportFomat = "mp3"  # Replace with your desired export format
file_path = os.path.join(os.getcwd(), "downloadedAudio", f"{audioFilename.split('.')[0]}.{exportFomat}")
logging.info(f"File path: {file_path}")

