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

output_file = 'extracted_texts.xlsx'
df = pd.read_excel(output_file)

def extract_judge_name(html_path):
    global df
    data = []
    try:
        # Fetch the page content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(html_path, headers=headers, timeout=10)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')
        p_elements = soup.find_all('p')

        start_printing = False
        name_to_text = {}

        combined_names = ""
        combined_text = ""
        for p in p_elements:
            p_text = p.get_text().strip()
            if any(title in p_text for title in ['פסק-דין', 'החלטה']):
                start_printing = True
                continue  # Skip the current element containing "פסק-דין"

            if start_printing:
                combined_text += p_text + "\n"

            if p_text.startswith("כבוד"):
                combined_names += p_text + " "

        # Split combined_names by "כבוד" and filter out empty entries
        names_arr = [name.strip() for name in combined_names.split("כבוד") if name.strip()]

        for judgment_name in names_arr:
            new_df = pd.DataFrame({
                'Name': [judgment_name],  # Make sure values are in a list
                'Text': [combined_text.strip()]  # The text should also be a list
            })
            # Concatenate the new DataFrame to the existing DataFrame
            df = pd.concat([df, new_df], ignore_index=True)

        #return name_to_text
    except Exception as e:
        print(f"Error: {e}")
    return data
def fill_inputs():
    try:
        driver.get("https://supreme.court.gov.il/pages/fullsearch.aspx")
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        if iframes:
            driver.switch_to.frame(iframes[0])
            input_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.select2-choices input.select2-input')))
            input1 = input_elements[0]
            input1.click()


            li_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ui-select-choices-row-0-1')))
            #li_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ui-select-choices-row-0-6')))
            print(f"Selecting option: {li_element.text}")
            li_element.click()
            input_elements[0].send_keys(Keys.ESCAPE)

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
    max_links = 10
    limited_links = file_links[:max_links]
    all_name_to_text = {}
    all_data = []
    names = []
    for link in limited_links:
        print(f"File link: {link}")
        time.sleep(10)
        current_data = extract_judge_name(link)
        all_data.append(current_data)
        #for name, text in current_name_to_text.items():
         #   all_name_to_text[name] = text

    df.to_excel(output_file, index=False)

fill_inputs()
#search()
#files_iterator()

#extract_judge_name("https://supremedecisions.court.gov.il/Home/Download?path=NetVerdicts/2024/8/7/2024-0-5709-3-1&fileName=21fac27aa2144f10b6ca5ed84cbdf227&type=2")
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