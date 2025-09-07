
urlBase = "https://www.thegradcafe.com"

def print_record(record, indent=0):
    indent_str = " " * indent
    for key, value in record.items():
        # If value is a dictionary, print recursively with extra indent
        if isinstance(value, dict):
            print(f"{indent_str}{key}:")
            print_record(value, indent + 4)
        else:
            print(f"{indent_str}{key}: {value}")
    print()  # Blank line after each record


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

def isNotesRow(row):
    # this seems to be the only way to identify Notes row    
    div = row.find('p', class_='tw-text-gray-500 tw-text-sm tw-my-0')

    #there should be some text in the div
    if div and div.get_text(strip=True):
        #print("Notes row found:", div.get_text(strip=True))
        return True
    return False

# to ensure empty fields have a "none" or "" value
record_template = {
    "program": "",
    "Degree": "",
    "date_added": "",
    "status": "",
    "url": "",
    "term": "",
    "US/International": "",
    "GRE": "",
    "GRE V": "",
    "GRE AW": "",
    "GPA": "",
    "comments": ""
}       

def clean_data(rows, i):        
        row1 = rows[i]
        row2 = rows[i+1]
        row3 = rows[i+2]
        record = record_template.copy()
            
        row1_cols = row1.find_all('td')
        row1_data = [col.get_text(strip=True) or "N/A" for col in row1_cols]
        #print("Row1 Data:", row1_data)
        spans = row1_cols[1].find_all('span')
        
        #record["program"]     = spans[0].get_text(strip=True) if len(spans) > 0 else "N/A"
        #record["University"]  = row1_data[0] if len(row1_data[0]) > 0 else "N/A"

        program = spans[0].get_text(strip=True) if len(spans) > 0 else "N/A"
        university  = row1_data[0] if len(row1_data[0]) > 0 else "N/A"
        if program != "N/A" and university != "N/A":
            record["program"] = f"{program}, {university}"
        else:
            record["program"] = program if program != "N/A" else university 
        record["Degree"]      = spans[1].get_text(strip=True) if len(spans) > 1 else "N/A"
        record["date_added"]  = row1_data[2] if len(row1_data) > 2 and len(row1_data[2]) > 1 else "N/A"        
        record["status"]      = row1_data[3] if len(row1_data) > 3 and len(row1_data[3]) > 1 else "N/A"

        '''
        #print("Row2 Data:", row2_data)
        print("Row2 Data:")
        for item in row2_data:
            print(item)
        
        print("Spans in Row2 Col2:")
        for span in spans:
            print(span.get_text(strip=True) or "N/A")
        
        Row2 Data:
            Wayne State University              >> university [0]
            Civil And Environmental EngineeringPhD
            September 06, 2025              >> date Added [2]
            Accepted on 28 Aug              >> Accepted , accepeted date
            Total commentsOpen optionsSee MoreReport
            Spans in Row2 Col2:
            Civil And Environmental Engineering.  >> program.  spans[0]
            PhD                                 >> degree.     spans[1]
        '''

        detail_url = getDetailUrlFromRow(row1)
        record["url"]      = detail_url if len(detail_url) > 1 else "N/A"
        #print("Detail URL from Row2:", detail_url)
        
        #row2_cols = row2.find_all('td')
        #row2_data = [col.get_text(strip=True) or "N/A" for col in row2_cols]
        
        all_divs = row2.find_all('div')
        row2_divs = [div.get_text(strip=True) or "N/A" for div in all_divs]
        record["term"]              = row2_divs[2] if len(row2_divs) > 2 and len(row2_divs[2]) > 1 else "N/A"
        record["US/International"]  = row2_divs[3] if len(row2_divs) > 3 and len(row2_divs[3]) > 1 else "N/A"

        ## Rest of the fields may / may not be present, this is sorted with longest first to avoid partial matches
        ## maybe try regex later
        for div in row2_divs:                
            if div.startswith("GRE AW "):
                record["GRE AW"] = div[len("GRE AW "):].strip() or "N/A"
            elif div.startswith("GRE V "):
                record["GRE V"] = div[len("GRE V "):].strip() or "N/A"
            elif div.startswith("GRE "):
                record["GRE"] = div[len("GRE "):].strip() or "N/A"
            elif div.startswith("GPA "):
                record["GPA"] = div[len("GPA "):].strip() or "N/A"

        '''
        record["GRE"]               = row3_divs[4] if len(row3_divs) > 3 else "N/A"
        record["GRE V"]             = row3_divs[5] if len(row3_divs) > 4 else "N/A"
        record["GRE AW"]            = row3_divs[6] if len(row3_divs) > 5 else "N/A"
        record["GPA"]               = row3_divs[7] if len(row3_divs) > 6 else "N/A" 
        '''
        '''
        print("Row3 Data:")
        for item in row3_data:
            print(item)
        
        print("Row3 Divs:")
        for item in row3_divs:
            print(item)

        Accepted on 28 AugSpring 2026InternationalGRE 310GRE V 150GRE AW 3.5GPA 3.62 [0]
        Accepted on 28 Aug     >>> status [1]
        Spring 2026            >>> term.  [2]
        International.         >>> US/Internaltional. [3]
        GRE 310
        GRE V 150
        GRE AW 3.5
        GPA 3.62
        '''
        commentRow = False
        if (isNotesRow(row3)):
            row3_cols = row3.find_all('td')
            row3_data = [col.get_text(strip=True) or "N/A" for col in row3_cols]
            record["comments"] = row3_data[0] if len(row3_data[0]) > 1 else "N/A" 
            commentRow = True

        #print_record(record)
        return record, commentRow

        '''
        print("Row4 Data:")
        for item in row4_data:
            print(item)
        Row4 Data:
            professor took interview and then offer letter come
        '''

        """
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
        
        """

def open_data(filename):
    # Open and read records from a JSON file
    records = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            record = json.loads(line)
            records.append(record)
    return records