

### Notes
    1. Installed required packages - requirements.txt
    2. Added tests with pytest
    3. Test coverage - following changes done from previous working code - module3
        a. Added a sample html file and added a test env to indicate to scrape.py
           to read from html instead of gradcafe website.
        b. tweaked original design to not load any data by default
            Original design was to load db with previously queried results that
            would be stored in applicant_data_*.json files
        c. Some print and reference function - added #pragma no cover
        d. Few line of code handling exceptions - added #pragma no cover
    4. Added test code to cleanup data files - to help with running the test iteratively.   
        


# directory structure
../module_4 % tree -L 2
.
├── coverage.txt
├── github_details.txt
├── models
│   └── tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
├── pytest.ini
├── README.md
├── requirements.txt
├── src
│   ├── __pycache__
│   ├── app.py
│   ├── clean.py
│   ├── config.py
│   ├── data
│   ├── llm_hosting
│   ├── load_data.py
│   ├── models
│   ├── query_data.py
│   ├── scrape.py
│   └── templates
├── tests
│   ├── __pycache__
│   ├── conftest.py
│   ├── sample_page.html
│   ├── test_analysis_format.py
│   ├── test_buttons.py
│   ├── test_db_insert.py
│   ├── test_flask_page.py
│   └── test_integration_end_to_end.py
└── venv




