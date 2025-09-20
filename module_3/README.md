

### Design
    1. create database if not already exists from abc.json.  create_database()
    2. for each json file with  abc_*.json matching name (they are newly scrapped data)
        update db with files  for any files matching this name. update_database()
    3. scrape new data and update
        a. maintain a two record table - as latest/newest update from
           scraped-data to db
        b.  for each new record scraped (while scraping)
                compare new record with entries in gradRecords_latest
                - if reasonably sure that new record matches with the one in db
                    - stop scraping
                    - we already have the remaining records from gradcafe
                      in the db.
        c. two records is an optimization - can be improved to a ring buffer/similar later.
    4. Installed pgAdmin4 to run queries and see db entries etc on a GUI.
    5. Fetch new data - flow
       Start scraping from page-1 on grad-cafe
       for each record compare with gradrecord_latest
       stop if a matching entry is found
       push the newly got records into applicant_data_new.json
       run llm/app-py on this file-> applicant_data_new_clean.json
       add new entries to db
       rename  to applicant_data_X.json
       delete temp files

# directory structure
../module_3 % tree -L 2
.
├── __pycache__
├── app.py
├── clean.py
├── config.py
├── data
│   ├── applicant_data_0.json
│   ├── applicant_data_1.json
├── llm_hosting
│   ├── canon_programs.txt
│   ├── canon_universities.txt
│   ├── llm_app.py
│   ├── models
│   ├── out.json
│   ├── README.md
│   ├── requirements.txt
│   └── runLogs.txt
├── load_data.py
├── models
│   └── tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
├── query_data.py
├── README.md
├── requirements.txt
├── scrape.py
├── templates
│   ├── base.html
│   ├── create.html
│   └── summary.html
└── venv    



