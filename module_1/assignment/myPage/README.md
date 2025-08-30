# myPage

A simple Flask-based personal website - W1 assignment at JHU

## Setup Instructions

### 1. Install Python

Make sure you have Python 3.7 or newer installed.  
Check with:
```sh
python3 --version
```
If not installed, download from [python.org](https://www.python.org/downloads/).

---

### 2. Create and Activate a Virtual Environment

Navigate to your project folder and run:
```sh
python3 -m venv venv
```

Activate the virtual environment:

- **macOS/Linux:**
  ```sh
  source venv/bin/activate
  ```

---

### 3. Install Flask

With the virtual environment activated, install Flask:
```sh
pip install Flask
```

---

### 4. Run the Application on Port 8080

In your project directory, run:
```sh
python -m flask --app myPage run --port 8080 --debug
```

---

### 5. Open in Browser

Visit [http://localhost:8080](http://localhost:8080) to view your site.

---

## Project Structure

```
myPage/
  __init__.py
  pages.py
  static/
    styles.css
    tmpProfile.jpg
  templates/
    base.html
    pages/
      home.html
      projects.html
      contact.html
```

---

## Notes
