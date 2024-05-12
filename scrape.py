import undetected_chromedriver as uc
import selenium
from selenium.webdriver.chrome.service import Service
import os
from PyPDF2 import PdfMerger

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pyautogui as pag
import pdfkit

import json
import time

all_links = list()


def merge_pdfs(folder_path, output_file):
    merger = PdfMerger()

    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_file_directory, 'data')
    print("Directory of the current file:", folder_path)

    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            merger.append(file_path)

    merger.write(output_file)
    merger.close()


def save_website_as_pdf(link):
    global all_links

    def save_pdf(all_srh_links):
        config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        for each in all_srh_links:
            file_name = each.split('/')[-2]
            try:
                pdfkit.from_url(each, f'./RAG/data/{file_name}.pdf', configuration=config)
            except Exception as e:
                print(e)

    chrome_options = selenium.webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    driver = uc.Chrome(options=chrome_options)
    time.sleep(5)
    driver.get(link)
    all_links = [each.get_attribute('href') for each in driver.find_elements(By.TAG_NAME, 'a')]
    all_links = list(set(all_links))
    for _ in range(3):
        for each_link in list(set(all_links)):
            if str(each_link).startswith('https://www.srh'):
                try:
                    time.sleep(3)
                    driver.get(each_link)
                    new_links = [each.get_attribute('href') for each in driver.find_elements(By.TAG_NAME, 'a')]
                    save_pdf(new_links)
                    all_links.extend(new_links)
                except Exception as e:
                    pass

    all_unique_links = list(set(all_links))
    driver.quit()

    return all_unique_links


url = 'https://www.srh-hochschule-heidelberg.de/en/'

all_unique_links = save_website_as_pdf(url)

folder_name = "data"
output_file_name = "merged_pdf.pdf"

merge_pdfs(folder_name, output_file_name)
