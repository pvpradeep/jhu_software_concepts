
import urllib3
from bs4 import BeautifulSoup
import json
import time
from clean import clean_data
import sys
from query_data import print_records

import os
from config import DSN, JSON_DATA_FILEPATH, JSON_DATA_FILENAME

surveys = "https://www.thegradcafe.com/survey/index.php?page={}"
http = urllib3.PoolManager()
applicant_data_file = 'applicant_data_new.json'
records = []

def _isStartOfNewRecord(row):
    # this seems to be the only way to identify start of new record
    div = row.find('div', class_='tw-font-medium tw-text-gray-900 tw-text-sm') 
    #there should be some text in the div
    if div and div.get_text(strip=True):
        return True
    return False

def _is_existing_record(record, latest_records_in_db):
    if not record or not latest_records_in_db:
        return False    
    for latest_r in latest_records_in_db:
        # Date time comparison did not work since format might be different
        #record.get('date_added') == latest_r.get('date_added') and
        #print(f"comparing\n NEW : {record.get('url')} \nvs \nDB : {latest_r.get('url')}\n")
        if (record.get('url')        == latest_r.get('url')):
            print(f"Found record in DB(stop scraping) : {latest_r.get('url')}\n")
            return True
    return False


def _scrape_one_page(page_number, latest_records_in_db):
    url = surveys.format(page_number)
    print("Scraping ", url)
    found_old_record = False

    response = http.request('GET', url)
    if (response.status != 200):
        print("Error: Unable to fetch {url}, errno = {response.status}")
        return
    
    i = 0
    
    page = urllib3.PoolManager().request('GET', url)
    soup = BeautifulSoup(page.data, 'html.parser')

    #Find the first table on the page (adjust if needed)
    table = soup.find('table')

    # Get all rows (tr elements) in the table
    rows = table.find_all('tr')[1:] # 1: Skip header row
    
    while i < len(rows):
        row = rows[i]
        commentRow = False
        if (_isStartOfNewRecord(row)):
            record, commentRow = clean_data(rows, i)
            if record:
                if (_is_existing_record(record, latest_records_in_db)):
                    found_old_record = True
                    print(f"Found existing record, break: {record}")
                    break
                else:
                    records.append(record)
            i += 2 # move to next record (2 rows ahead)
            if commentRow:
                i += 1
        else:
            i += 1 # move to next row
        

    return found_old_record


def save_data(records, filename):
    try:
        file_path = os.path.join(JSON_DATA_FILEPATH, f"{filename}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # File doesn't exist or empty, start with empty list
        data = []

    # Append new records
    data.extend(records)

    # Rewrite entire file with updated data
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Saved {len(records)} records to {file_path}")

def scrape_new(nPage=1, max_records=400):
    from load_data import get_grad_records_latest
    start_time = time.time()
    print(f"Starting from page {nPage}")
    nRecords = 0
    latest_records_in_db = get_grad_records_latest()
    print(f"Latest in db, stop at \n: {latest_records_in_db}")
    while nRecords < max_records:
        found_old_record = _scrape_one_page(nPage, latest_records_in_db)
        nPage += 1
        nRecords += len(records)       

        #Append each page data to the file
        print(f"Got {len(records)} records to {applicant_data_file}, total records: {nRecords}, nPage: {nPage}")
        if len(records) != 0:
            save_data(records, applicant_data_file)
            records.clear()
        if found_old_record:
            break
        time.sleep(0.25) # Be polite and avoid overwhelming the server

    end_time = time.time()
    print(f"Scraping completed in {end_time - start_time} seconds.")

  

