# Apartment Analytics

## Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Pipeline](#pipeline)
* [Technologies Used](#technologies-used)
* [Dashboard](#dashboard)
* [Installation](#installation)
* [Requirements](#requirements)
* [Notes](#notes)

## Overview

This project is an Apartment Listing Tracker that scrapes property data from [MyHome.ge](https://www.myhome.ge/), [Livo.ge](https://livo.ge/) and [Home.ss.ge](https://home.ss.ge/ka/udzravi-qoneba/), processes and stores the data, and generates visual analytics presented in a web dashboard. It enables ongoing monitoring of real estate trends and prices across different cities and districts in Georgia.

## Features

* **Web scraping**: Data extraction from real estate websites
* **Data cleaning**: Structured formatting and transformation of raw data
* **Database storage**: Uses SQLite to store cleaned data
* **Data analysis**: Generates a variety of charts for insights
* **Web dashboard**: Interactive HTML interface to view visual analytics

## Pipeline

The main data pipeline runs as follows:

```
Step 1: Scrape the data and save it to a csv file

Step 2: Data cleaning and transformation. Saved cleaned data in a seperate csv file

Step 3: Save cleaned data in the database

Step 4: Extract all the data from the database and do data analysis

Step 5: An interactive website to view visual analytics
```

Each step is modular, allowing individual components to be run or debugged separately.

## Technologies Used

* **Python 3**
* **Selenium** for web scraping
* **Pandas** for data manipulation
* **Matplotlib & Seaborn** for visualization
* **SQLite** as the database
* **HTML/CSS/JS** for the dashboard

## Dashboard

The dashboard (`frontend/index.html`) provides:

* City distribution pie chart
* Average price per city by listing type
* Average price per m² per city
* Price by area bin per city
* Average price by street (with dropdown selector for city)

Charts are dynamically displayed using JavaScript and loaded from pre-generated `.png` files.

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/GiorgiEz/apartment-analytics.git
cd apartment-analytics
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the pipeline**
   Run `main.py`:

```bash
cd scrape_clean_analyze
python main.py
```

4. **View the dashboard**
    ```bash
    cd frontend
    python -m http.server
    ```
    Open http://localhost:8000/src/index.html in a web browser.

    To use Tailwind CSS, run:
    ```bash
    npx @tailwindcss/cli -i ./scrape_clean_analyze/css/input.css -o ./scrape_clean_analyze/css/output.css --watch
    ```

## Requirements

```text
selenium~=4.34.0
pandas~=2.3.0
seaborn~=0.13.2
matplotlib~=3.10.3
```

## Notes

* Scraping takes a couple of minutes to fully complete.
* SQLite is used for simplicity and local storage. Might be extended to PostgreSQL or another RDBMS.
