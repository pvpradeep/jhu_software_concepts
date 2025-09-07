
import urllib3
from bs4 import BeautifulSoup
import json
import time
from clean import clean_data, print_record
import sys


surveys = "https://www.thegradcafe.com/survey/index.php?page={}"
http = urllib3.PoolManager()
applicant_data_file = 'applicant_data.json'
records = []

def isStartOfNewRecord(row):
    # this seems to be the only way to identify start of new record
    div = row.find('div', class_='tw-font-medium tw-text-gray-900 tw-text-sm') 
    #there should be some text in the div
    if div and div.get_text(strip=True):
        return True
    return False
   
def scrape_one_page(page_number):
    url = surveys.format(page_number)
    print("Scraping ", url)

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
        if (isStartOfNewRecord(row)):
            record, commentRow = clean_data(rows, i)
            if record:
                #print_record(record)
                records.append(record)
            i += 2 # move to next record (2 rows ahead)
            if commentRow:
                i += 1
        else:
            i += 1 # move to next row        

def save_data_once(records, filename):
    # Save records to a JSON file
    '''
    with open(filename, 'a', encoding='utf-8') as f:
        for record in records:
            json_line = json.dumps(record, ensure_ascii=False)
            f.write(json_line + '\n')
    '''
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

def save_data(records, filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # File doesn't exist or empty, start with empty list
        data = []

    # Append new records
    data.extend(records)

    # Rewrite entire file with updated data
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Saved {len(records)} records to {filename}")

def scrape_page(nPage, max_records):
    nRecords = 0
    
    while nRecords < max_records:
        scrape_one_page(nPage)
        nPage += 1
        nRecords += len(records)       

        #Append each page data to the file
        print(f"Got {len(records)} records to {applicant_data_file}, total records: {nRecords}, nPage: {nPage}")
        if len(records) != 0:
            save_data(records, applicant_data_file)
            records.clear()

        time.sleep(0.25) # Be polite and avoid overwhelming the server

def main(startPage, maxRecords):
    start_time = time.time()
    print(f"Starting from page {startPage}")
    scrape_page(startPage, maxRecords)
    #print(f"Saving {len(records)} records to {applicant_data_file}")
    #save_data(records, applicant_data_file)
    end_time = time.time()
    print(f"Scraping completed in {end_time - start_time} seconds.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <param1> <param2>")
        sys.exit(1)
    startPage  = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    maxRecords = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    main(startPage, maxRecords)
    

