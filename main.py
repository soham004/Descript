from modules.utils import *
from modules.automation_parts import *
from modules.descriptLinkDownload import downloadFromDescript

import threading
import sys
import json
import time
import os
# import undetected_chromedriver as uc
from selenium import webdriver
from selenium_stealth import stealth

config = None
# Load the config file
with open('config.json', 'r') as f:
    config = json.load(f)

time_to_wait_before_export_in_mins = config.get("time_to_wait_before_export_in_mins", 5)


os.makedirs("downloadedAudio", exist_ok=True)
os.makedirs("inputFiles", exist_ok=True)

current_directory = os.getcwd()
download_dir = os.path.join(current_directory, "downloadedAudio")
prefs = {"download.default_directory" : download_dir,
         'profile.default_content_setting_values.automatic_downloads': 1,
         "download.prompt_for_download" : False,
         "download.directory_upgrade": True,
         "plugins.always_open_pdf_externally": True,
         "safebrowsing.enabled": True,
         "safebrowsing.disable_download_protection": True,
         "credentials_enable_service": False,
         "profile.password_manager_enabled": False,
        }

options = webdriver.ChromeOptions()
options.add_argument("--mute-audio"); #// Mute audio
options.add_experimental_option("prefs",prefs)
options.add_argument("start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled") 
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False) 

options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_experimental_option("prefs", prefs) 
options.add_argument('log-level=3')

options.add_experimental_option("detach", True)

def chunk_list(input_list, chunk_size=9):

    result = []
    for i in range(0, len(input_list), chunk_size):
        result.append(input_list[i:i + chunk_size])
    return result

if __name__ == "__main__":

    with open('downloadLinks.txt', 'w') as f: # Clear the file content
        f.write('')
    
    input_files_folder = "inputFiles"
    process = None
    if '--no-merge' not in sys.argv:
        process = threading.Thread(target=merge_all, args=(input_files_folder,))
        process.start()
        process.join()
        # merge_all(mergebase_folder)
    else:
        print("Skipping merging of files.")
        print("Using just the .mp3 files present in the inputFiles folder and not any subfolders.")
    
    
    driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(30)
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Google Inc. (Intel)",
        renderer="ANGLE (Intel, Intel(R) Iris(R) Xe Graphics (0x000046A8) Direct3D11 vs_5_0 ps_5_0, D3D11)",
        fix_hairline=True,
    )

    driver.get("https://web.descript.com/")

    loginToDescript(driver)
    # input("EEEEE")
    driver.get("https://web.descript.com/projects?filter=recent-projects")
    change_settings(driver)
        
    audioFiles = os.listdir(input_files_folder)
    audioFiles = [f for f in audioFiles if f.endswith('.mp3')]

    chunked_audio_files = chunk_list(audioFiles, 6)

    print(f"No of chunks: {len(chunked_audio_files)}")
    logging.info(f"Chunks: {chunked_audio_files}")

    for audio_files in chunked_audio_files:

        remove_all_previous_projects(driver)

        time.sleep(2)

        for audioFile in audio_files:
            try:
                print("")
                print(f"Processing {audioFile}...")
                create_new_project(driver, audioFile)
                upload_audio_file(driver, os.path.abspath(os.path.join(input_files_folder, audioFile)))
                createNewComposition(driver)
                useAudioFile(driver, audioFile)
            except Exception as e:
                print(f"Error processing {audioFile}: {e}")
                logging.error(f"{traceback.format_exc()}")
                
        
        print(f"Waiting {time_to_wait_before_export_in_mins} minutes before export...")
        time.sleep(time_to_wait_before_export_in_mins * 60)

        export_files = export_all_projects(driver)

        logging.info(f"Exported files: {export_files}")
        
        # Download all the files
        with open('downloadLinks.txt', 'r') as f:
            links = f.readlines()
        
        for i, link in enumerate(links):
            link = link.strip()
            if link:
                downloadFromDescript(driver, link, export_files[i]+".mp3")

    driver.quit()
