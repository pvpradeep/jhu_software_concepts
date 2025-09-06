
import urllib3
from bs4 import BeautifulSoup
import json
import time

urlBase = "http://www.thegradcafe.com/survey/index.php?page={}"
http = urllib3.PoolManager()

def scrape_page(page_number):
    url = urlBase.format(page_number)
    print(url)

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

    print("Headers:", headers)  # Print header names
    # Skip the header row usually at index 0
    #data_rows = rows[1:]
    data_rows = table.find_all('tr')[1:]

    results = []
    for i, row in enumerate(data_rows):
        #print("***************", row)
        #print("***************")
        if i > 20:
            break
        # Search for the <a> tag with href containing '/result/' anywhere inside the row:
        detail_link = row.find('a', string='See More')

        if detail_link and detail_link.has_attr('href'):
            relative_url = detail_link['href']
            # Normalize URL if needed, e.g. ignore fragment identifiers or trailing spaces
            relative_url = relative_url.split()[0]  # To handle any trailing content after href link
            detail_url = "https://www.thegradcafe.com" + relative_url
            #print("Detail URL found:", detail_url)
            summary_cols = row.find_all('td')
            summary_data = [col.get_text(strip=True) or "N/A" for col in summary_cols]
            record = {
                "summary": summary_data,
                "detail_url": detail_url
            }
            print(record)
        else:
            print("No detail link found in this row ",i , "***\n" , row, "***\n")
    
"""
## somewhat working
    for row in data_rows:
        cols = row.find_all('td')
        if len(cols) >= 5:
            entry = {
                "School": cols[0].get_text(strip=True),
                "Program": cols[1].get_text(strip=True),
                "Date": cols[2].get_text(strip=True),
                "Decision": cols[3].get_text(strip=True),
                "notes": cols[4].get_text(strip=True)
            }
            print(entry)
            results.append(entry)
"""        
## did not work
"""
    results = soup.find_all('div', class_='result')
    for result in results:
        school = result.find('span', class_='school').text
        program = result.find('span', class_='program').text
        decision = result.find('span', class_='decision').text
        date = result.find('span', class_='date').text
        print(f"School: {school}, Program: {program}, Decision: {decision}, Date: {date}")
"""

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
