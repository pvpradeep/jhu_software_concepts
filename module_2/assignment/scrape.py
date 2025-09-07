
import urllib3
from bs4 import BeautifulSoup
import json
import time
from clean import clean_data, print_record


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
    print("Searching ", url)

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

def save_data(records, filename):
    # Save records to a JSON file
    with open(filename, 'a', encoding='utf-8') as f:
        for record in records:
            json_line = json.dumps(record, ensure_ascii=False)
            f.write(json_line + '\n')

def scrape_page(max_records):
    nPage = 1
    nRecords = 0
    
    while nRecords < max_records:
        scrape_one_page(nPage)
        nPage += 1
        nRecords += len(records)
        time.sleep(1) # Be polite and avoid overwhelming the server

        #Append each page data to the file
        print(f"Saving {len(records)} records to {applicant_data_file}, total records: {nRecords}, nPage: {nPage}")
        if len(records) != 0:
            save_data(records, applicant_data_file)
            records.clear()


if __name__ == "__main__":
    start_time = time.time()
    scrape_page(200)  # Scrape up to 200 records
    end_time = time.time()
    print(f"Scraping completed in {end_time - start_time} seconds.")

