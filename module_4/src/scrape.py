
import urllib3
from bs4 import BeautifulSoup
import json
import time
from src.clean import clean_data
import sys
from src.query_data import print_records

import os
from src.config import DSN, JSON_DATA_FILEPATH, JSON_DATA_FILENAME

surveys = "https://www.thegradcafe.com/survey/index.php?page={}"
http = urllib3.PoolManager()
applicant_data_file = 'applicant_data_new.json'
records = []

def _isStartOfNewRecord(row):
    """
    Check if a table row represents the start of a new grad record.

    This internal function identifies the start of a new record by looking for
    a specific div element with certain CSS classes and non-empty text content.

    :param row: BeautifulSoup row element from the scraped table
    :type row: bs4.element.Tag
    :return: True if row is start of new record, False otherwise
    :rtype: bool
    """
    # this seems to be the only way to identify start of new record
    div = row.find('div', class_='tw-font-medium tw-text-gray-900 tw-text-sm') 
    #there should be some text in the div
    if div and div.get_text(strip=True):
        return True
    return False

def _is_existing_record(record, latest_records_in_db):
    """
    Check if a scraped record already exists in the database.

    Compares the URL of the new record against URLs in the most recent database
    records to prevent duplicate entries. URL comparison is used instead of date
    due to potential format differences.

    :param record: Newly scraped record to check
    :type record: dict
    :param latest_records_in_db: Recent records from database for comparison
    :type latest_records_in_db: list[dict]
    :return: True if record exists in database, False otherwise
    :rtype: bool
    """
    if not record or not latest_records_in_db:
        return False    
    for latest_r in latest_records_in_db:
        # Date time comparison did not work since format might be different
        #record.get('date_added') == latest_r.get('date_added') and
        #print(f"comparing\n NEW : {record.get('url')} \nvs \nDB : {latest_r.get('url')}\n")
        if record.get('url') == latest_r.get('url'):
            print(f"Found record in DB(stop scraping) : {latest_r.get('url')}\n")
            return True
    return False


def fetch_html_or_sample(url):
    """
    Fetch HTML content from URL or return sample data for testing.

    This function either fetches live data from a URL or returns sample data
    based on the USE_SAMPLE_HTML environment variable. This allows for
    consistent testing without hitting the live website.

    :param url: URL to fetch HTML content from
    :type url: str
    :return: HTML content as string
    :rtype: str
    :raises Exception: If live URL fetch fails with non-200 status
    
    Environment Variables:
        USE_SAMPLE_HTML: If "1", uses sample data instead of live fetching
    """
    # Custom variable to control use of sample HTML for testing
    USE_SAMPLE_HTML = os.environ.get("USE_SAMPLE_HTML") == "1"
    print(f"USE_SAMPLE_HTML = {USE_SAMPLE_HTML}")

    # If running under pytest, use the local sample HTML file
    if USE_SAMPLE_HTML:
        sample_path = os.path.join(os.path.dirname(__file__), "../tests/sample_page.html")
        with open(sample_path, "r", encoding="utf-8") as f:
            return f.read()
    # avoid in coverage since we load from a html file during tests    
    else:   # pragma: no cover
        response = http.request('GET', url)
        if response.status != 200:
            raise Exception(f"Error: Unable to fetch {url}, errno = {response.status}")
        return response.data.decode("utf-8")

def _scrape_one_page(page_number, latest_records_in_db):
    """
    Scrape a single page of grad records and process the content.

    Fetches and parses one page of graduate admissions records, checking each
    record against the database to avoid duplicates. Stops when finding an
    existing record.

    :param page_number: Page number to scrape from GradCafe
    :type page_number: int
    :param latest_records_in_db: Recent records from database for comparison
    :type latest_records_in_db: list[dict]
    :return: True if an existing record was found (indicating to stop scraping)
    :rtype: bool
    
    Global variables:
        - records: List where new records are appended
        - surveys: Base URL format string for GradCafe pages
    """
    url = surveys.format(page_number)
    print("Scraping ", url)
    found_old_record = False

    html = fetch_html_or_sample(url)
    soup = BeautifulSoup(html, 'html.parser')

    # Find the first table on the page (adjust if needed)
    table = soup.find('table')

    # Get all rows (tr elements) in the table
    rows = table.find_all('tr')[1:]  # 1: Skip header row

    i = 0
    while i < len(rows):
        row = rows[i]
        commentRow = False
        if _isStartOfNewRecord(row):
            record, commentRow = clean_data(rows, i)
            if record:
                if _is_existing_record(record, latest_records_in_db):
                    found_old_record = True
                    print(f"Found existing record, break: {record}")
                    break
                else:
                    records.append(record)
            i += 2  # move to next record (2 rows ahead)
            if commentRow:
                i += 1
        else:
            i += 1  # move to next row

    return found_old_record


def save_data(records, filename):
    """
    Save scraped records to a JSON file, appending to existing data if present.

    Handles both creating new files and updating existing ones. Preserves any
    existing records while adding new ones. Uses UTF-8 encoding and pretty
    printing for the JSON output.

    :param records: New records to save
    :type records: list[dict]
    :param filename: Name of the file to save to
    :type filename: str

    Global variables:
        - JSON_DATA_FILEPATH: Directory where JSON files are stored
    """
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
    """
    Main scraping function to collect new graduate admission records.

    Scrapes GradCafe pages sequentially until either reaching the maximum
    record count or finding an existing record. Includes rate limiting
    to be respectful to the server.

    :param nPage: Starting page number to scrape from, defaults to 1
    :type nPage: int
    :param max_records: Maximum number of records to collect, defaults to 400
    :type max_records: int
    
    Global variables:
        - records: List storing scraped records
        - applicant_data_file: File where records are saved
    
    Note:
        Includes a 0.25 second delay between pages to avoid overwhelming the server
    """
    from src.load_data import get_grad_records_latest
    start_time = time.time()
    print(f"Starting from page {nPage}")
    nRecords = 0
    
    while nRecords < max_records:        
        latest_records_in_db = get_grad_records_latest()
        print(f"Latest in db, stop at \n: {latest_records_in_db}")

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

  

