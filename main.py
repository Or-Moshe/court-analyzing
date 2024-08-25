import pandas as pd
import time
from bs4 import BeautifulSoup
import requests
import traceback
import os

file_name = 'all_english_judgements.txt'
directory_path = './'  # Path where your files are stored

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
        html_path = html_path.replace('"', '').replace(",", "").strip()
        print('html_path', html_path)
        response = requests.get(html_path, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')
        all_p = soup.find_all('p')
        all_span = soup.find_all('span')

        elements_to_check = all_p + all_span
        # Extract relevant text
        for element in elements_to_check:
            text = element.get_text(strip=True)
            if "Before" in text:
                print("Found relevant section, extracting...")
                extracted_texts = [el.get_text(strip=True) for el in elements_to_check]
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

def read_and_process_files():
    file_path = os.path.join(directory_path, file_name)
    with open(file_path, 'r') as file:
        for line in file:
            link = line.strip()  # Remove any extra whitespace or newline characters
            if link:  # Ensure it's not an empty string
                extract_data(link)
                print('sleep')
                time.sleep(5)
                print('waked up')
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
    # Example to process each link

read_and_process_files()