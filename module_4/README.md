

# Graduate School Application Data Analysis

[![Documentation Status](https://readthedocs.org/projects/jhu-m4/badge/?version=latest)](https://jhu-m4.readthedocs.io/en/latest/?badge=latest)

📚 [Read the full documentation](https://jhu-m4.readthedocs.io/en/latest/)

A Python application for analyzing graduate school application data from GradCafe, featuring web scraping, data analysis, and a Flask web interface.

## Features
- Web scraping from GradCafe
- Database storage with PostgreSQL
- Data analysis and statistics
- Web interface using Flask
- LLM-based data processing
- Comprehensive test coverage
- Sphinx documentation

## Setup Instructions

### Prerequisites
- Python 3.13 or higher
- PostgreSQL database
- Virtual environment tool (venv)

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/pvpradeep/jhu_software_concepts.git
cd module_4
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

4. Install required packages:
```bash
pip install -r requirements.txt
pip install -r docs/requirements.txt  # for documentation
```

5. Configure PostgreSQL:
- Create a database
- Update database connection settings in `src/config.py`

### Running Tests

Run tests with coverage:
```bash
pytest --cov=src/ -v
```

### Building Documentation

```bash
cd docs
make html
```
Documentation will be available at `docs/build/html/index.html`

## Project Structure
```
module_4/
├── docs/                    # Documentation
│   ├── source/             # Documentation source
│   ├── build/              # Built documentation
│   └── requirements.txt    # Documentation dependencies
├── src/                    # Source code
│   ├── app.py             # Flask application
│   ├── clean.py           # Data cleaning
│   ├── config.py          # Configuration
│   ├── load_data.py       # Database operations
│   ├── query_data.py      # Data analysis
│   ├── scrape.py          # Web scraping
│   └── templates/         # Flask templates
├── tests/                  # Test files
├── setup.py               # Package setup
└── requirements.txt       # Project dependencies
```

## Development Notes

### Original Implementation Notes
1. Initial package setup and testing:
   - Installed required packages (see requirements.txt)
   - Added comprehensive tests with pytest
   - Configured test coverage

2. Test coverage improvements:
   - Added sample HTML file and test environment flag for scrape.py to read from local HTML instead of live GradCafe website
   - Modified original design to not load data by default (previously loaded DB with queried results from applicant_data_*.json files)
   - Added '#pragma no cover' for print/reference functions and exception handling
   - Implemented test code to cleanup data files for iterative testing

### Recent Updates and Fixes
1. Reorganized project structure:
   - Moved documentation to `docs/` directory
   - Updated Sphinx configuration
   - Added Read the Docs support

2. Fixed import issues:
   - Updated relative imports to use `src.` prefix
   - Fixed module path in Sphinx conf.py
   - Added proper package installation support

3. Testing improvements:
   - Added sample HTML for offline testing
   - Implemented test cleanup utilities
   - Added pragmas for coverage exclusions

4. Documentation:
   - Added Sphinx documentation
   - Organized into logical sections
   - Added proper docstrings

### Known Issues and Solutions
- If you get "Module not found" errors:
  - Ensure you've installed the package: `pip install -e .`
  - Check PYTHONPATH includes project root
  - Verify virtual environment is activated

- For documentation build issues:
  - Install documentation requirements: `pip install -r docs/requirements.txt`
  - Run `make clean` before `make html`
  - Check conf.py path settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and build documentation
5. Submit a pull request

```
../module_4 % tree -L 2
module_4 % tree -L 2
.
├── coverage.txt
├── docs
│   ├── build
│   ├── make.bat
│   ├── Makefile
│   ├── requirements.txt
│   └── source
├── github_details.txt
├── m4_pytestDoc.egg-info
├── models
│   └── tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
├── pytest.ini
├── README.md
├── requirements.txt
├── setup.py
├── src
│   ├── __init__.py
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


```