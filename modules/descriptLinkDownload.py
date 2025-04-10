import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import requests

from modules.utils import *
from modules.notifier import *

def downloadFromDescript(driver:webdriver.Chrome, link:str, filename:str):
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
            print(f"Waiting {downloadTimeoutPerComposition/60} mins for download button...")
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
            print(f"Downloading file from {driver.current_url}...")
            logging.info(f"Downloading file from {driver.current_url}...")
            r = requests.get(driver.current_url)
            filename = filename.split(".")[0] + "." + driver.current_url.split(".")[-1]
            path = os.path.join(os.getcwd(), "downloadedAudio", filename)
            logging.info(f"Writing file: {filename} to {path}")
            with open(path, "wb") as f:
                f.write(r.content)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    time.sleep(5)

def downloadFromDescriptUsingReq(driver:webdriver.Chrome, file_names, composition_names, bearer_token:str):
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    base_url = config["defaultProject"]
    project_id = base_url.split("/")[-2]
    url = f"https://web.descript.com/v2/projects/{project_id}/published_projects"
    logging.info(f"Fetching compositions from {url}...")
    payload = {}
    headers = {
                'sec-ch-ua-platform': '"Windows"',
                'Authorization': f'Bearer {bearer_token}',
                'x-descript-app-build-number': '20250409.25792',
                'x-descript-app-build-type': 'release',
                'sec-ch-ua': '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                'sec-ch-ua-mobile': '?0',
                'x-descript-app-name': 'web',
                'traceparent': '00-a99a97be74c0917ad01eab6423b27a43-4c02adb792f71e76-00',
                'x-descript-auth': 'auth0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-version': 'v1',
                'Content-Type': 'application/json',
                'x-descript-app-id': 'd4c17ff9-7f77-4dac-9d2f-97bb393871af',
                'x-descript-app-version': '112.0.1',
                'Sec-GPC': '1',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'host': 'web.descript.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
            }
    response = requests.request("GET", url, headers=headers, data=payload)
    logging.info(f"Response status code: {response.status_code}")
    if response.status_code != 200:
        logging.error(f"Failed to fetch compositions: {response.status_code}")
        logging.error(f"Response: {response.text}")
        print(f"Failed to fetch compositions: {response.status_code}")
        return
    response_json = json.loads(response.text)

    i = 0
    for composition in response_json:
        if(composition['name'] in composition_names):
            link = f"https://share.descript.com/view/{composition['url_slug']}"
            logging.info(f"Downloading file from {link}...")
            downloadFromDescript(driver, link=link, filename=file_names[i])
            i += 1
        else:
            logging.info(f"Composition {composition['name']} not found in the list {composition_names}.")

