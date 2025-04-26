from modules.utils import *
from modules.automation_parts import *
from modules.descriptLinkDownload import downloadFromDescript

import threading
import multiprocessing
import sys
import json
import time
import os
import math
from selenium import webdriver
from selenium_stealth import stealth

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

# Create necessary directories
os.makedirs("downloadedAudio", exist_ok=True)
os.makedirs("inputFiles", exist_ok=True)

# Browser setup function
def get_chrome_driver():
    current_directory = os.getcwd()
    download_dir = os.path.join(current_directory, "downloadedAudio")
    prefs = {
        "download.default_directory": download_dir,
        'profile.default_content_setting_values.automatic_downloads': 1,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }

    options = webdriver.ChromeOptions()
    options.add_argument("--mute-audio")
    options.add_experimental_option("prefs", prefs)
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('log-level=3')
    options.add_experimental_option("detach", True)
    
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
    return driver

# Process a group of files in a single browser instance
def process_file_group(file_group, thread_id, results_dict):
    logging.info(f"Thread {thread_id} starting with {len(file_group)} files")
    print(f"Thread {thread_id} processing files: {file_group}")
    
    # Initialize browser
    driver = get_chrome_driver()
    download_links = []
    
    # Create thread-specific links file
    thread_links_file = f'downloadLinks_thread_{thread_id}.txt'
    
    # Clear thread-specific links file
    with open(thread_links_file, 'w') as f:
        f.write('')
    
    try:
        # Login and setup
        driver.get("https://web.descript.com/")
        loginToDescript(driver)
        driver.get(config['defaultProject'])
        setUpProject(driver)
        
        # Create upload composition if files exist
        if file_group:
            # Create a temporary folder for this thread
            thread_folder = f"inputFiles_thread_{thread_id}"
            os.makedirs(thread_folder, exist_ok=True)
            
            # Copy files to thread folder
            for file in file_group:
                src_path = os.path.join("inputFiles", file)
                dst_path = os.path.join(thread_folder, file)
                with open(src_path, 'rb') as src, open(dst_path, 'wb') as dst:
                    dst.write(src.read())
            
            # Upload files for this thread
            createUploadComposition(driver=driver, base_folder=thread_folder)
            time.sleep(2)
        
            # Process each file
            for audioFile in file_group:
                try:
                    logging.info(f"Thread {thread_id} processing file: {audioFile}")
                    retries = 3
                    success = False
                    link = None
                    
                    while retries > 0:
                        print(f"Thread {thread_id} - Creating new composition for {audioFile}")
                        createNewComposition(driver)
                        useAudioFile(driver, audioFile)
                        
                        # Save links to thread-specific file
                        success = exportComposition(driver, destination="web", audioFilename=audioFile, links_file=thread_links_file)
                        
                        if success:
                            # Get the latest link from the clipboard
                            link_content = pyperclip.paste().strip()
                            # if "https://" in link_content and "descript" in link_content:
                            link = link_content
                            download_links.append((audioFile, link))
                            # Save link to thread-specific file
                            with open(thread_links_file, 'a') as f:
                                f.write(f"{audioFile}|{link}\n")
                            logging.info(f"Thread {thread_id} - Export successful for {audioFile}: {link}")
                            break
                        
                        print(f"Thread {thread_id} - Export failed for {audioFile}, retrying... ({retries} attempts left)")
                        retries -= 1
                    
                    if retries == 0:
                        print(f"Thread {thread_id} - Failed to export {audioFile} after 3 attempts, skipping.")
                
                except Exception as e:
                    print(f"Thread {thread_id} - Error processing {audioFile}: {e}")
                    logging.error(f"Thread {thread_id} - Error: {traceback.format_exc()}")
            
            # Clean up thread folder
            for file in os.listdir(thread_folder):
                os.remove(os.path.join(thread_folder, file))
            os.rmdir(thread_folder)
        
        # Download all files processed by this thread using thread-specific links file
        for audioFile, link in download_links:
            if link:
                # Pass the thread-specific links file to downloadFromDescript
                downloadFromDescript(driver, link, audioFile, thread_links_file)
        
        # Store results
        results_dict[thread_id] = download_links
        
    except Exception as e:
        logging.error(f"Thread {thread_id} encountered error: {str(e)}\n{traceback.format_exc()}")
        print(f"Thread {thread_id} failed: {str(e)}")
    finally:
        # Clean up thread-specific links file
        if os.path.exists(thread_links_file):
            try:
                os.remove(thread_links_file)
                logging.info(f"Thread {thread_id} - Removed thread-specific links file")
            except Exception as e:
                logging.error(f"Thread {thread_id} - Failed to remove links file: {str(e)}")
        
        driver.quit()
        logging.info(f"Thread {thread_id} completed")

if __name__ == "__main__":
    # Clear download links file
    with open('downloadLinks.txt', 'w') as f:
        f.write('')
    
    input_files_folder = "inputFiles"
    merge_process = None
    
    # Start merging process if needed
    if '--no-merge' not in sys.argv:
        merge_process = multiprocessing.Process(target=merge_all, args=(input_files_folder,))
        merge_process.start()
    else:
        print("Skipping merging of files.")
        print("Using just the .mp3 files present in the inputFiles folder and not any subfolders.")
    
    # Wait for merge to complete if it was started
    if merge_process:
        merge_process.join()
    
    # Get all audio files
    audioFiles = [f for f in os.listdir(input_files_folder) if f.endswith('.mp3')]
    logging.info(f"Found {len(audioFiles)} audio files to process")
    
    if not audioFiles:
        print("No audio files found. Exiting.")
        sys.exit(0)
    
    # Get number of concurrent browsers from config
    num_browsers = config.get('no_of_concurrent_browsers', 1)
    # Limit to the number of available files
    num_browsers = min(num_browsers, len(audioFiles))
    
    print(f"Starting {num_browsers} concurrent browser instances to process {len(audioFiles)} files")
    
    # Split files into groups
    file_groups = []
    files_per_group = math.ceil(len(audioFiles) / num_browsers)
    
    for i in range(0, len(audioFiles), files_per_group):
        group = audioFiles[i:i + files_per_group]
        file_groups.append(group)

    logging.info(f"File groups for processing: {file_groups}")
    
    # Create and start threads
    threads = []
    manager = multiprocessing.Manager()
    results_dict = manager.dict()
    
    for i, file_group in enumerate(file_groups):
        thread = threading.Thread(
            target=process_file_group,
            args=(file_group, i, results_dict)
        )
        threads.append(thread)
        thread.start()
        # Slight delay to prevent login collisions
        time.sleep(5)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Consolidate download links for reference
    all_links = []
    for thread_id in sorted(results_dict.keys()):
        all_links.extend(results_dict[thread_id])
    
    # Write all links to the download links file
    with open('downloadLinks.txt', 'w') as f:
        for audioFile, link in all_links:
            f.write(f"{link}\n")
    
    print("All processing completed!")
