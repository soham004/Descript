from modules.utils import *
from modules.automation_parts import *
from modules.descriptLinkDownload import downloadFromDescriptUsingReq

import json
import sys
import json
import time
import os
from selenium import webdriver
from selenium_stealth import stealth

config = None
# Load the config file
with open('config.json', 'r') as f:
    config = json.load(f)


os.makedirs("downloadedAudio", exist_ok=True)
os.makedirs("inputFiles", exist_ok=True)
# os.makedirs("runtime_files", exist_ok=True)


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
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

options.add_experimental_option("detach", True)


def process_browser_logs_for_network_events(logs):
    """
    Return only logs which have a method that start with "Network.response", "Network.request", or "Network.webSocket"
    and contain an Authorization header with a Bearer token.
    """
    bearer_token = None

    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if (
            "Network.response" in log["method"]
            or "Network.request" in log["method"]
            or "Network.webSocket" in log["method"]
        ):
            # Check if headers exist and contain an Authorization header
            headers = log.get("params", {}).get("request", {}).get("headers", {})
            authorization = headers.get("Authorization") or headers.get("authorization")
            if authorization and authorization.startswith("Bearer ") and not authorization.startswith("Bearer tokenNotNeeded"):
                bearer_token = authorization.split(" ")[1]

    return bearer_token # Returns the last Bearer token found

if __name__ == "__main__":

    with open('downloadLinks.txt', 'w') as f: # Clear the file content
        f.write('')
    
    mergebase_folder = "inputFiles"
    if '--no-merge' not in sys.argv:
        merge_all(mergebase_folder)
    else:
        print("Skipping merging of files.")
        print("Using just the .mp3 files present in the inputFiles folder and not any subfolders.")
    
    audioFiles = os.listdir(mergebase_folder)
    audioFiles = [f for f in audioFiles if f.endswith('.mp3')]
    logging.info(f"Audio files to be uploaded: {audioFiles}")
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
    driver.get(config['defaultProject'])
    setUpProject(driver)

    createUploadComposition(driver=driver, base_folder=mergebase_folder)

    time.sleep(2)

    # Generate all the files
    composition_names = []
    for audioFile in audioFiles:
        try:
            retries = 3
            success = False
            while retries > 0:
                print("")
                createNewComposition(driver)
                composition_name = useAudioFile(driver, audioFile)
                if composition_name is not None:
                    logging.info(f"Composition name: {composition_name}")
                    composition_names.append(composition_name)
                success = exportComposition(driver, destination="web", audioFilename=audioFile)
                if not success:
                    print("Export failed, retrying...")
                    retries -= 1
                    continue
                break
            if retries == 0:
                print("Failed to export after 3 attempts, skipping this file.")
        except Exception as e:
            print(f"Error processing {audioFile}: {e}")
            logging.error(f"{traceback.format_exc()}")
            continue
    
    logging.info(f"Composition names: {composition_names}")

    logs = driver.get_log("performance")

    bearer_token = process_browser_logs_for_network_events(logs)
    logging.info(f"Bearer token: {bearer_token}")

    downloadFromDescriptUsingReq(driver, audioFiles, composition_names, bearer_token)

    driver.quit()
