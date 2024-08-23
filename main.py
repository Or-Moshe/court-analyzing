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
iframes = []
output_file = 'extracted_texts_en.xlsx'
df = pd.read_excel(output_file)
data_list = []
def extract_data(html_path):
    try:
        # Fetch the page content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(html_path, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        html_content = response.content
        soup = BeautifulSoup(html_content, 'lxml')
        all_p = soup.find_all('p')

        for p in all_p:
            text = p.get_text()
            if "Before" in text:
                print("printed")
                extracted_texts = [p.get_text() for p in all_p]
                data_list.append({'Text': '\n'.join(extracted_texts)})
                return
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        print("Traceback:")
        traceback.print_exc()
    except IndexError as e:
        print(f"Index error: {e}")
        print("Traceback:")
        traceback.print_exc()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Traceback:")
        traceback.print_exc()
def fill_inputs():
    try:
        driver.get("https://supreme.court.gov.il/pages/fullsearch.aspx")
        global iframes
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

            input2 = input_elements[2]
            input2.click()

            #פלילי
            li_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ui-select-choices-row-2-3')))
            li_element.click()

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
    """
    time.sleep(15)
    driver.switch_to.default_content()
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(5)
    driver.switch_to.frame(iframes[0])
    time.sleep(5)
    """
    link_elements = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.file-link.html-link')))
    results_list = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'results-listing')))

    # Slice the list to include only up to max_links elements

    if results_list:
        last_height = driver.execute_script("return arguments[0].scrollTop;", results_list[0])

        while True:
            # Scroll down by 100 pixels until no more scroll is possible
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 100;", results_list[0])
            new_height = driver.execute_script("return arguments[0].scrollTop;", results_list[0])
            link_elements = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.file-link.html-link')))
            results_list = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'results-listing')))
            file_links = [element.get_attribute('href') for element in link_elements]
            max_links = 3
            limited_links = file_links[:max_links]
            print(len(file_links))
            for link in limited_links:
                print(f"File link: {link}")
                time.sleep(10)
                extract_data(link)
            # Break the loop if no new scroll is possible
            if new_height == last_height:
                break
            last_height = new_height

    try:
        df_existing = pd.read_excel(output_file)
    except FileNotFoundError:
        # If file does not exist, create an empty DataFrame
        df_existing = pd.DataFrame()

    # Convert the new data list to a DataFrame
    df_new = pd.DataFrame(data_list)

    # Concatenate the existing DataFrame with the new DataFrame
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)

    # Save the combined DataFrame to the Excel file
    df_combined.to_excel(output_file, index=False)


fill_inputs()
search()
files_iterator()

#extract_data("https://supremedecisions.court.gov.il/Home/Download?path=EnglishVerdicts/09/410/101/n10&fileName=09101410_n10.txt&type=2")
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