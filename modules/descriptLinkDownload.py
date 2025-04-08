import json
import time
from selenium import webdriver
# import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import requests

from modules.utils import *
from modules.notifier import *

def downloadFromDescript(driver:webdriver.Chrome, link:str, filename:str):
    # //div[contains(text(),"Preparing to render")]
    link = link.strip()
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    downloadTimeoutPerComposition = config["downloadTimeoutPerComposition"]
    print(f"Downloading from {link}...")
    logging.info(f"Downloading from {link}...")
    driver.get(link)
    time.sleep(5)
    for _ in range(3):
        try:
            downloadButton = WebDriverWait(driver, downloadTimeoutPerComposition).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Download"]')))
            downloadButton.click()
            break
        except TimeoutException:
            try:
                driver.get(link)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[contains(text(),"Preparing to render")]')))
                print("Render is still going on waiting...")
            except TimeoutException:
                logging.info("Download button not found or not clickable.")
                print("Download button not found or not clickable.")
                return False
        if _ == 2:
            logging.info("Download button not found or not clickable.")
            print("Download button not found or not clickable.")
            return False
        time.sleep(5)
    
    tabs = driver.window_handles
    for tab in tabs:
        driver.switch_to.window(tab)
        time.sleep(0.5)
        if "descriptusercontent" in driver.current_url:
            r = requests.get(driver.current_url)
            filename = filename.split(".")[0] + driver.current_url.split(".")[-1]
            path = os.path.join(os.getcwd(), "downloadedAudio", filename)
            logging.info(f"Downloading file: {filename} to {path}")
            with open(path, "wb") as f:
                f.write(r.content)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    time.sleep(5)


    

