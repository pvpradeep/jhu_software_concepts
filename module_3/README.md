

### Design
    1. create database if not already exists from abc.json.  create_database()
    2. for each json file with  abc_*.json matching name (they are newly scrapped data)
        update db with files  for any files matching this name. update_database()
    3. scrape new data and update
        a. maintain a two record table - as latest/newest update from
           scraped-data to db
        b.  for each new record scraped (while scraping)
                compare new record with entries in gradRecords_latest
                - if reasonable sure that new record matches with the one in db
                    - stop scraping
                    - we already have the remaining records from gradcafe
                      in the db.
        c. two records is an optimization - can be improved to a ring buffer/similar later.



