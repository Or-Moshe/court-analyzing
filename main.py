from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import  ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import requests
import traceback
import re

options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 20)

output_file = 'extracted_texts_en.xlsx'
df = pd.read_excel(output_file)

def extract_judge_name(html_path):
    global df
    try:
        # Fetch the page content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(html_path, headers=headers, timeout=10)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'lxml')

        # Use regular expression to capture patterns that include optional whitespace characters
        pattern = re.compile(r'The\s+Honorable', re.IGNORECASE)

        # Extract paragraphs that contain the specified pattern
        names_mentions = [p.get_text().strip() for p in soup.find_all('p') if pattern.search(p.get_text())]

        # Print the extracted names
        print('names_mentions', names_mentions)

        titles = ['פסק-דין', 'החלטה', 'J U D G M E N T', 'JUDGMENT', 'Judgment' , 'Judgment and Decision', 'Interim Decision', 'Partial Judgment']
        capturing = False
        combined_text = ""
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            # Check if the current paragraph is a title
            if any(title in text for title in titles):
                capturing = True
                continue  # Skip the title itself
            # If capturing is enabled, save the text
            if capturing:
                if text:  # Ensure not to capture empty paragraphs
                    combined_text += text + "\n"

        if combined_text == "":
            print('NOT FOUND')
        local_df = pd.DataFrame({
            'Name': names_mentions,
            'Text': [combined_text] * len(names_mentions)
        })

        df = pd.concat([df, local_df], ignore_index=True)
        df.to_excel(output_file, index=False)

    except Exception as e:
        print(f"Error: {e}")
def fill_inputs():
    try:
        driver.get("https://supreme.court.gov.il/pages/fullsearch.aspx")
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        if iframes:
            time.sleep(5)
            driver.switch_to.frame(iframes[0])

            input_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.select2-choices input.select2-input')))
            input1 = input_elements[0]
            input1.click()


            #li_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ui-select-choices-row-0-1')))
            li_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ui-select-choices-row-0-6')))
            print(f"Selecting option: {li_element.text}")
            li_element.click()
            input_elements[0].send_keys(Keys.ESCAPE)


            time.sleep(5)
            driver.switch_to.default_content()
            time.sleep(5)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(5)

            driver.switch_to.frame(iframes[0])
            time.sleep(5)
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'][ng-click='Search()']"))
            )
            button.click()
            # driver.switch_to.default_content()
            # time.sleep(5)
            # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # time.sleep(5)
            # driver.switch_to.frame(iframes[0])

            """
            print(driver.page_source)


            # Wait for the element that needs to be clicked to open the dropdown
            input_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.select2-choices input.select2-input')))
            input1 = input_elements[0]
            input1.click()

            #li_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ui-select-choices-row-0-1')))
            li_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ui-select-choices-row-0-6')))
            print(f"Selecting option: {li_element.text}")
            li_element.click()


            input2 = input_elements[2]
            input2.click()

            # Wait for the dropdown to be visible and get the <ul> element
            #בגץ
            li_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ui-select-choices-row-2-1')))
            #פלילי
            #li_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ui-select-choices-row-2-3')))
            li_element.click()
            """
    except Exception as e:
        tb_str = traceback.format_exception(type(e), e, e.__traceback__)
        print("".join(tb_str))
    # finally:
    #   driver.quit()

def search():
    search_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'search-button')))
    driver.execute_script("arguments[0].click();", search_button)
    #search_button.click()
def files_iterator():
    link_elements = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.file-link.html-link')))

    # Extract href attributes from all found elements
    file_links = [element.get_attribute('href') for element in link_elements]

    # Slice the list to include only up to max_links elements
    max_links = 5000
    limited_links = file_links[:max_links]
    all_name_to_text = {}
    all_data = []
    names = []
    for link in limited_links:
        print(f"File link: {link}")
        time.sleep(10)
        extract_judge_name(link)
        """
        current_data = extract_judge_name(link)
        all_data.append(current_data)

    df.to_excel(output_file, index=False)
    """

fill_inputs()
search()
files_iterator()

#extract_judge_name("https://supremedecisions.court.gov.il/Home/Download?path=EnglishVerdicts/20/440/021/v26&fileName=20021440.V26&type=2")
#extract_judge_name("https://supremedecisions.court.gov.il/Home/Download?path=NetVerdicts/2024/8/6/2024-8-12457-1-2&fileName=1e10572b5db64ed38663f17d23e1bce4&type=2")
"""
try:
    driver.get("https://supreme.court.gov.il/Pages/SearchJudgments.aspx?&OpenYearDate=null&CaseNumber=null&DateType=1&SearchPeriod=8&COpenDate=null&CEndDate=2024&freeText=null&Importance=null&CaseMonth=null")
    #driver.get("https://supreme.court.gov.il/pages/fullsearch.aspx")
    html = driver.page_source
    time.sleep(5)
    # Close the browser

    #search_button = driver.find_element(By.CLASS_NAME, 'SearchMainForm')
    #print('search_button', search_button)
    ## Click the button using JavaScript
    #driver.execute_script("arguments[0].click();", search_button)

    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
    if iframes:
        driver.switch_to.frame(iframes[0])

        link_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.file-link.html-link'))
        )

        # Extract href attributes from all found elements
        file_links = [element.get_attribute('href') for element in link_elements]

        extract_judge_name(file_links[0])
        # Print out all the href links
        for link in file_links:
            print(f"File link: {link}")
            #extract_judge_name(link)
        # Switch back to the main content
        driver.switch_to.default_content()
except Exception as e:
    print(f"Error: {e}")
#finally:
 #   driver.quit()
"""