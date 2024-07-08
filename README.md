# PrivacyCourseExtraction

This repository contains scripts to extract privacy-related content from university course listings. The process involves web scraping to gather HTML pages of course listings, downloading linked pages, and analyzing the content for privacy-related keywords.

## Repository Structure

- `webScraper.py`: A script to perform Google searches for university course listings and save the HTML pages.
- `downloadHop1Links.py`: A script to download all linked pages from the main course listing pages.
- `findPrivacyContent.py`: A script to analyze the downloaded HTML pages for privacy-related content and save the results to CSV files.

## Prerequisites

- Python 3.6+
- Selenium
- BeautifulSoup
- Pandas
- Requests
- WebDriver Manager for Chrome
- ChromeDriver

## Setup

1. **Install required Python packages:**
   `pip install selenium beautifulsoup4 pandas requests webdriver-manager chromedriver-autoinstaller`

2. Ensure ChromeDriver is installed and compatible with your version of Chrome.
The scripts use chromedriver-autoinstaller to handle this automatically.

3. Directory Structure:
Ensure the courseListings/ directory exists in the root of your repository. This is where HTML files will be saved and read from.


## Usage

**Step 1**: Scrape University Course Listings
Run webScraper.py to perform Google searches for the list of universities and save the HTML pages of the course listings

This script:
- Reads a list of university names.
- Searches for the undergraduate computer science courses page for each university on Google.
- Saves the HTML of the first search result to the courseListings/ directory.
- Updates the universityLinkMapping.json with the URLs of the course listings.

Expected output: 
- A series of HTML files, each named after the college's webpage.

**Universities in `universityLinkMapping.json` will be skipped. Delete the file for a fresh run.**

**Step 2**: Download Linked Pages
Run downloadHop1Links.py to download all linked pages from the main course listing pages saved in Step 1.

This script:
- Reads the main course listing HTML files.
- Extracts all links from each main page.
- Downloads the content of each link and saves it to the respective university directory under `courseListings/
Expectred Output:
- A series of folders, each named after their university

May need to `pip install lxml`

**Step 3**: Find Privacy-Related Content
Run findPrivacyContent.py to analyze the downloaded HTML pages for privacy-related content and save the results to CSV files.


This script:
- Reads the main and linked HTML files.
- Searches for privacy-related keywords in the content.
- Saves the extracted content to privacyContent.csv, privacyRelatedTitleContent.csv, and universitiesWithNoPrivacyRelatedContent.csv.


## Note:

- We will first extract university cours catalog pages using webScraper.py
- This should be followed by running the downloadHop1Links.py in order to extract all the hop 1 links from the course catalog pages.
- findPrivacyContent.py - will extract the course title/descriptions from the web pages downloaded using downloadHop1Links.py. Important - It is necessary to do a manual review and filtering of the data resulting from findPrivacyContent.py in order to get best results.

## Debugging Tips

`downloadHop1Links.py` will process all files in your `courseListings` directory. If you have many files in `courseListings`, each run may take a long time. Delete all but 10 of the `html` files in the `courseListings` directory to make a quick run of the script for faster debugging.

## Contributors

- Kristen Vaccaro
- Aishwarya Manjunath