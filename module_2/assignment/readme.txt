# Web Scrape assignment

## Name : Pradeep Prasanna  pprasan2@jh.edu

## Module Info : Week 2, Module 2, Wen Scraping

## Approach
    1. use BeautifulSoup and urllib3 to open and parse thegradcafe.com survey results.
    . Check robots.txt for restrictions and legality to scrape data
    . Manually find the right links and how to progress to next page
    . Initial attempt was to find the "See More" tag to get to the
      individual record and scrape each record. This failed since those pages
      did not have all info.
      . print the html and identify the tags and rows and how to fetch the required
        content
      . Started with one page and fetch all records in the page(only printing to confirm output is correct)
      . found a way around with some records not having the "comments" information
      . added functions to identify start of record, does-comment-exists etc
      . Implement iteration over multiple pages and count records
      . Implement output to json, correction required to add indentaion
      . since idea was to save to json intermittently (to avoid holding all record data in memory)
        the output to json was getting messed up sometimes - fixed.
      . Implemented requirement to have empty strings for absent fields using a record_template.
      . tested llm-hosting with small subset of applicant_data.json first
      . Since it was not clear and its possible that some older pages might have missing fields or formatting the program cannot handle
        - added a way to pass page-number and records to fetch
        - this way the program can be restarted after a failure from the page it failed.
        - the records fetched in previous runs can be retained - no need to start from page-1 always.

## Known bugs
    . not sure if saving intermittently to json is counter productive. - needs tuning(profiling).

## Testing logs
    Final Iteration:
    ```
    Scraping  https://www.thegradcafe.com/survey/index.php?page=2499
    Got 20 records to applicant_data.json, total records: 49980, nPage: 2500
    Saved 20 records to applicant_data.json
    Scraping  https://www.thegradcafe.com/survey/index.php?page=2500
    Got 20 records to applicant_data.json, total records: 50000, nPage: 2501
    Saved 20 records to applicant_data.json
    Scraping completed in 4218.534202098846 seconds.
    ```
