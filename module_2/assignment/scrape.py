
import urllib3
from bs4 import BeautifulSoup
import json
import time

urlBase = "https://www.thegradcafe.com"
surveys = "https://www.thegradcafe.com/survey/index.php?page={}"
http = urllib3.PoolManager()

def getValueOfField(soup, field_name):
    field = soup.find(string=field_name)
    if field:
        value = field.find_next().get_text(strip=True)
        if value:
            return value
    return "N/A"


def getRecordFromDetailPage(detail_url):
    response = http.request('GET', detail_url)
    if (response.status != 200):
        print("Error: Unable to fetch {detail_url}, errno = {response.status}")
        return None

    page = urllib3.PoolManager().request('GET', detail_url)
    soup = BeautifulSoup(page.data, 'html.parser')

    fields = {'Institution', 'Program', 'Degree Type', 'Degree\'s Country of Origin', 'Decision', 'Notification', 'Notes'}
    details = {}
    for field in fields:
        details[field] = getValueOfField(soup, field)
    #print(details)
    return details

def getDetailUrlFromRow(row):
    # Search for the <a> tag with href containing '/result/' anywhere inside the row:
    detail_link = row.find('a', string='See More')
    detail_url = None

    if detail_link and detail_link.has_attr('href'):
        relative_url = detail_link['href']
        # Normalize URL if needed, e.g. ignore fragment identifiers or trailing spaces
        relative_url = relative_url.split()[0]  # To handle any trailing content after href link
        detail_url = urlBase + relative_url
        #print("Detail URL found:", detail_url)
    return detail_url
    
def scrape_page(page_number):
    url = surveys.format(page_number)
    print("Searching ", url)

    response = http.request('GET', url)
    if (response.status != 200):
        print("Error: Unable to fetch {url}, errno = {response.status}")
        return

    page = urllib3.PoolManager().request('GET', url)
    soup = BeautifulSoup(page.data, 'html.parser')

    #Find the first table on the page (adjust if needed)
    table = soup.find('table')

    # Get all rows (tr elements) in the table
    rows = table.find_all('tr')

    # Get header row (th elements)
    header_row = table.find('tr')
    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]

    data_rows = table.find_all('tr')[1:]
    i = 0
    for row in data_rows:
        #print("***************", row)
        #print("***************")
        detail_url = getDetailUrlFromRow(row)
        summary_cols = row.find_all('td')
        summary_data = [col.get_text(strip=True) or "N/A" for col in summary_cols]
        if detail_url != None:
            record = {                
                "detail_url": detail_url,
                #"summary": summary_data
            }
            record.update(getRecordFromDetailPage(detail_url) or {})
            print(record)
        #else:
            #print("No detail URL found for row:", summary_data)
        i += 1
        if i > 3:
            break
        

for page_number in range(1, 1):  # Scrape first 5 pages
    scrape_page(page_number)


if __name__ == "__main__":
    start_time = time.time()
    scrape_page(1)
    end_time = time.time()
    print(f"Scraping completed in {end_time - start_time} seconds.")

#page = urllib3.PoolManager().request('GET', url)
#soup = BeautifulSoup(page.data, 'html.parser')

#print(soup.title.string)
