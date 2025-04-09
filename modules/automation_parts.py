import json
import time
from selenium import webdriver
# import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import *
import pyautogui
import pygetwindow as gw
import traceback

from modules.utils import *
from modules.notifier import notify

import ctypes

ctypes.windll.user32.AllowSetForegroundWindow(-1)




# Allow the current process to set the foreground window
def waitForLoginToComplete(driver:webdriver.Chrome):
    # Wait for the login to complete by checking for the presence of the "New Project" button
    try:
        print("Waiting atmost 2mins for login to complete...")
        WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'New Project')]/parent::span/parent::button")))
        print("Login successful!")
    except TimeoutException:
        print("Login failed or timed out.")
        notify("Descritpt Login", "Login failed or timed out.")
        driver.quit()
        exit()


def click_element(driver:webdriver.Chrome, web_element):
    driver.execute_script("arguments[0].click();", web_element)


def loginToDescript(driver:webdriver.Chrome):
    config = None
    # Load the config file
    with open('config.json', 'r') as f:
        config = json.load(f)

    # Load the credentials
    email = config['email']
    password = config['password']

    try:
        # Wait for the email field to be present and fill it in
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='email']"))).send_keys(email)
        # Wait for the password field to be present and fill it in
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))).send_keys(password)

        # Wait for the login button to be present and click it
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))).click()

        waitForLoginToComplete(driver)
        # Wait for the "New Project" button to be present
    except TimeoutException:
        print("Login failed please check you internet connection.")
        notify("Descript Login", "Login failed please check you internet connection.")
        driver.quit()
        exit()

def setUpProject(driver:webdriver.Chrome):
    # Wait for the "New Project" button to be present and click it
    with open('config.json', 'r') as f:
        config = json.load(f)
    maxWaitTimeForOpeningProject = config['maxWaitTimeForOpeningProject']
    try:
        print(f"Waiting {maxWaitTimeForOpeningProject/60} mins for project setup...")

        app_menu_button = WebDriverWait(driver, maxWaitTimeForOpeningProject).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Open app menu"]')))
        app_menu_button.click()

        time.sleep(1)
        # Wait for the "Create a new project" button to be present and click it

        setteings_div = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Settings")]/parent::div/parent::div')))
        click_element(driver, setteings_div)

        
        time.sleep(2)
        transcribeButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Always ask before transcribing")]/following-sibling::div/button')))
        if transcribeButton.get_attribute("aria-checked") == "false":
            # transcribeButton.click()
            click_element(driver, transcribeButton)
            time.sleep(1)
        
        close_dialog = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Close dialog"]')))
        click_element(driver, close_dialog)


        print("Project setup completed!")
    except TimeoutException:
        logging.error(traceback.format_exc())
        print("Failed to set up project.")
        driver.quit()
        exit()

def rename_composition(driver:webdriver.Chrome, composition_name:str):
    
    actionChains = ActionChains(driver)

    composition_popup = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='composition-popover-trigger']")))
    # composition_popup.click()
    actionChains.move_to_element(composition_popup).click().perform()

    last_composition = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//ul[@id="composition-folder-tree"]/li/div[1]')))[-1]
    actionChains.context_click(last_composition).perform()
    time.sleep(1)
    rename_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Rename')]/parent::div/parent::div")))
    # rename_button.click()
    actionChains.move_to_element(rename_button).click().perform()

    time.sleep(1)

    actionChains.send_keys(composition_name).perform()
    actionChains.send_keys(Keys.RETURN).perform()
    time.sleep(1)
    actionChains.send_keys(Keys.ESCAPE).perform()

def delete_last_composition(driver:webdriver.Chrome):
    print("Deleting last composition...")
    actionChains = ActionChains(driver)

    composition_popup = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='composition-popover-trigger']")))
    # composition_popup.click()
    actionChains.move_to_element(composition_popup).click().perform()

    last_composition = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//ul[@id="composition-folder-tree"]/li/div[1]')))[-1]
    actionChains.context_click(last_composition).perform()
    time.sleep(1)
    delete_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Delete')]/parent::div/parent::div")))
    click_element(driver, delete_button)

    time.sleep(1)
    actionChains.send_keys(Keys.ESCAPE).perform()
    actionChains.send_keys(Keys.ESCAPE).perform()
    actionChains.send_keys(Keys.ESCAPE).perform()
    print("Last composition deleted!")

def createNewComposition(driver:webdriver.Chrome, composition_name:str = None):
    # //button[@data-testid="composition-popover-trigger"]
    actionChains = ActionChains(driver)
    retry = 3
    try:
        driver.find_element(By.XPATH, '//div[@data-testid="composition-popover-content"]')
    except NoSuchElementException:
        while retry > 0:
            try:
                composition_popup = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='composition-popover-trigger']")))
                # composition_popup.click()
                click_element(driver, composition_popup)
                print("Composition popup clicked")
                break
            except Exception as e:
                logging.info(f"Error in try block on line 124: {e}")
                print("Error occurred, retrying...")
                actionChains.send_keys(Keys.ESCAPE).perform()
                actionChains.send_keys(Keys.ESCAPE).perform()
                actionChains.send_keys(Keys.ESCAPE).perform()
                actionChains.send_keys(Keys.ESCAPE).perform()
                time.sleep(1)
                retry -= 1

        if retry == 0:
            print("Failed to click the composition popup after 3 attempts.")
            raise Exception("Failed to click the composition popup after 3 attempts.")
        
    time.sleep(1)
    new_composition_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'New composition')]/parent::span/parent::button")))
    # new_composition_button.click()
    click_element(driver, new_composition_button)
    print("New composition button clicked")
    if composition_name is not None:
        rename_composition(driver, composition_name)

def createUploadComposition(driver:webdriver.Chrome, base_folder:str='inputFiles'):
    # //button[@data-testid="composition-popover-trigger"]
    #//div[contains(@class,'Spinner-module')]
    config = None
    # Load the config file
    with open('config.json', 'r') as f:
        config = json.load(f)

    uploadTimePerFile = config['uploadTimeoutPerFile']
    createNewComposition(driver, "Upload")
    time.sleep(2)
    audioFiles = os.listdir(base_folder)
    audioFiles = [f for f in audioFiles if f.endswith('.mp3')]
    copy_files_to_clipboard([get_absolute_path(os.path.join(base_folder, f)) for f in audioFiles]) 
    print("File path copied to clipboard successfully.")
    ActionChains(driver)\
        .key_down(Keys.CONTROL)\
        .send_keys("v")\
        .key_up(Keys.CONTROL)\
        .perform()
    print("Waiting for upload to start..")
    try:
        WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'Spinner-module')]")))
        print("Upload started!")
    except TimeoutException:
        print("Upload failed or timed out.")
        driver.quit()
        exit()
    print("Waiting for all activities to complete..")

    start_time = time.time()
    printOnce = True
    while (time.time() - start_time) < (uploadTimePerFile * len(audioFiles)):
        time.sleep(1)
        # Check if the upload is complete
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'Spinner-module')]")))
            print("Activities in progress...") if printOnce else None
            printOnce = False
        except TimeoutException:
            print("Upload completed!")
            break
    
    if time.time() - start_time >= uploadTimePerFile * len(audioFiles):
        print("Upload timed out.")
        driver.quit()
        exit()
    
    clear_clipboard()

def gotoProjectTab(driver:webdriver.Chrome):
    project_tab = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Project')]/parent::button")))
    click_element(driver, project_tab)

def srearchAndSelectFile(driver:webdriver.Chrome, audioFile:str):
    # Wait for the search input field to be present and fill it in
    try:
        clear_search_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Clear search"]')))
        click_element(driver, clear_search_button)
        print("Cleared previous search.")
        time.sleep(.5)
    except TimeoutException:
        pass
    searchField = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//input[@type="search"]')))
    searchField.send_keys(audioFile.split(".")[0])
    time.sleep(1)
    try:
        last_file = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//ul[@id="project-files-tree"]/li/div[3]')))[-1]
        ActionChains(driver).context_click(last_file).perform()
    except TimeoutException:
        print("Failed to find the file button.")
        raise Exception("Failed to find the file button.")
    try:
        time.sleep(1)
        insert_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(),"Insert into script")]/parent::div/parent::div')))
        # insert_button.click()
        click_element(driver, insert_button)
    except TimeoutException:
        print("Failed to find the insert button.")
        raise Exception("Failed to find the insert button.")

    time.sleep(2)
    closeTranscribeButton = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close dialog']")))
    # closeTranscribeButton.click()
    click_element(driver, closeTranscribeButton)
    time.sleep(1)
    

def applyStudioSound(driver:webdriver.Chrome):
    underlord_tab = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Underlord')]/parent::button")))
    # underlord_tab.click()
    click_element(driver, underlord_tab)

    studioSoundButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@data-action-id="studioSound"]')))
    # studioSoundButton.click()
    click_element(driver, studioSoundButton)
    time.sleep(1)

    # studioSoundEffectsButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@data-key="studio-sound"]/.//button[@aria-label="Effect settings"]')))
    # # studioSoundEffectsButton.click()
    # click_element(driver, studioSoundEffectsButton)
    # time.sleep(1)
    #//span[contains(text(),"Intensity")]/parent::div/following-sibling::div/input
    # studioSoundIntensity = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(),"Intensity")]/parent::div/parent::label/parent::div')))
    # studioSoundIntensity.click()
    # time.sleep(1)
    # ActionChains(driver)\
    #     .send_keys("80")\
    #     .send_keys(Keys.RETURN)\
    #     .perform()
    # time.sleep(1)
    # close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="close-button"]')))
    # close_button.click()
    print("Waiting for studio sound application to start..")
    while True:
        try:
            WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'Spinner-module')]")))
            print("studio sound application started!")
            break
        except TimeoutException:
            # print("studio sound application failed or timed out.")
            pass
            # # driver.quit()
            # exit()
    
    print("waiting for studio sound to apply...")
    exportOnce = True
    while True:
        try:
            driver.find_element(By.XPATH, "//div[contains(@class,'Spinner-module')]")
            print("Studio Sound application in progress...") if exportOnce else None
            exportOnce = False
        except NoSuchElementException:
            print("Studio Sound application completed!")
            break
    time.sleep(.4)
    time.sleep(1)

def useAudioFile(driver:webdriver.Chrome, audioFile:str):
    gotoProjectTab(driver)
    srearchAndSelectFile(driver, audioFile)
    applyStudioSound(driver)


def exportComposition(driver:webdriver.Chrome, destination:str = "local", audioFilename:str = None) -> bool:

    exportSuccess = True

    exportButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="publish-popover-trigger"]')))
    if exportButton.get_attribute("data-state") == "closed":
        # exportButton.click()
        click_element(driver, exportButton)
    
    destinationDropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-labelledby="published-composition-name"]')))
    # destinationDropdown.click()
    click_element(driver, destinationDropdown)
    time.sleep(1)

    if destination == "web":
        try:
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(),"Published")]')))
        except TimeoutException:
            webOption = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="export-destination-select-option-Web link"]')))
            # webOption.click()
            click_element(driver, webOption)
            time.sleep(1)
            final_exportButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="publish-button"]')))
            # final_exportButton.click()
            click_element(driver, final_exportButton)

    
    if destination == "web":
        # Wait for published text
        webExportComplete = False
        try:
            print(f"Waiting {200/60} mins for web export to complete...")
            WebDriverWait(driver, 200).until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(),"Published")]')))
            print("Web Export completed!")
            webExportComplete = True
        except TimeoutException:
            webExportComplete = False
            exportSuccess = False
            print("Web export failed or timed out.")
        time.sleep(2)
        if webExportComplete:
            copy_successful = False
            while not copy_successful:
                copyLinkButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Copy published page link"]')))
                # location = copyLinkButton.location
                # size = copyLinkButton.size
                # panel_height = driver.execute_script('return window.outerHeight - window.innerHeight;')
                # center_x = location['x'] + size['width'] // 2
                # center_y = location['y'] + panel_height + (size['height'] // 2)
                
                # pyautogui.moveTo(center_x, center_y)
                # pyautogui.click()
                actionChains = ActionChains(driver)
                actionChains.move_to_element(copyLinkButton).click().perform()
                time.sleep(2)
                copy_successful = save_clipboard_link()
                clear_clipboard()
    
    elif destination == "local":
        localOption = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="export-destination-select-option-Local export"]')))
        # localOption.click()
        click_element(driver, localOption)
        time.sleep(1)
        config = None
        # Load the config file
        with open('config.json', 'r') as f:
            config = json.load(f)

        exportFomat = config['exportFomat']
        exportFomat = exportFomat.lower()

        if exportFomat not in ["mp3", "wav", "m4a"]:
            print("Invalid export format. Deafulting to mp3.")
            exportFomat = "mp3"
        
        formatDropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Format')]/following-sibling::div/button")))
        # formatDropdown.click()
        click_element(driver, formatDropdown)

        time.sleep(.5)
        
        mp3Option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//span[contains(text(),"{exportFomat}")]/parent::div/parent::div')))
        # wavOption.click()
        click_element(driver, mp3Option)

        time.sleep(.5)

        final_exportButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="export-button"]')))
        # final_exportButton.click()
        click_element(driver, final_exportButton)

        file_path = os.path.join(os.getcwd(), "downloadedAudio", f"{audioFilename.split('.')[0]}.{exportFomat}")
        # pyperclip.copy(file_path)
        for _ in range(3):
            time.sleep(10)
            try:
                gw.getWindowsWithTitle("Warning:")[0].activate()
                print("Download window brought to front.")
            except Exception as e:
                logging.info(e)
                continue
            break
        pyautogui.write(file_path, interval=0.05)
        time.sleep(.5)
        pyautogui.press('enter')
    
    elif destination == "local":
        #wait for a .mp3 in the download folder
        print("Waiting for file to be downloaded...")
        time.sleep(5)
        downloadTimeoutPerComposition = config['downloadTimeoutPerComposition']
        start_time = time.time()
        exportOnce = True
        print(f"Waiting for {downloadTimeoutPerComposition/60} mins for file to be downloaded...")
        while True:
            try:
                driver.find_element(By.XPATH, "//div[contains(@class,'Spinner-module')]")
                print("Local Export in progress...") if exportOnce else None
                exportOnce = False
            except NoSuchElementException:
                print("Local Export completed!")
                break
            if time.time() - start_time > downloadTimeoutPerComposition:
                exportSuccess = False
                print("File download timed out.")
                break
        time.sleep(.4)
    
    try:
        close_export_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Close"]')))
        # close_export_button.click()
        click_element(driver, close_export_button)
    except TimeoutException:
        pass
    actionChains = ActionChains(driver)
    actionChains.send_keys(Keys.ESCAPE).perform()
    actionChains.send_keys(Keys.ESCAPE).perform()
    actionChains.send_keys(Keys.ESCAPE).perform()
    time.sleep(1)
    return exportSuccess


