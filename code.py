import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime, timedelta

# Set up Selenium WebDriver
chrome_options = Options()
# Remove headless mode to see the browser window
# chrome_options.add_argument("--headless")  # Comment this line out to see the browser window
service = Service('C:/chromedriver-win64/chromedriver.exe')  # Specify path to your WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# LinkedIn URLs for the companies
urls = [
    "https://www.linkedin.com/jobs/search?location=India&geoId=102713980&f_C=1035&position=1&pageNum=0",
    "https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_C=1441",
    "https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_TPR=r86400&f_C=1586&position=1&pageNum=0"
]

# Function to parse posted date
def parse_posted_date(posted_text):
    now = datetime.now()
    if "hour" in posted_text.lower():
        return now.strftime("%d-%m-%Y")
    elif "day" in posted_text.lower():
        days_ago = int(posted_text.split()[0])
        date = now - timedelta(days=days_ago)
        return date.strftime("%d-%m-%Y")
    elif "week" in posted_text.lower():
        weeks_ago = int(posted_text.split()[0])
        date = now - timedelta(weeks=weeks_ago)
        return date.strftime("%d-%m-%Y")
    else:
        return "Unknown"

# List to store all job data
all_jobs = []

# Scrape job postings from each URL
for url in urls:
    driver.get(url)
    time.sleep(5)  # Allow time for the page to load
    
    # Scroll down to load more jobs
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
    # Parse the page content
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_cards = soup.find_all('li', class_='jobs-search-results__list-item')  # Selector targeting job cards

    # Collect 15 jobs from each URL
    jobs_collected = 0
    for job in job_cards:
        if jobs_collected >= 15:
            break
        
        job_data = {}
        
        # Extract job title and link
        job_title_tag = job.find('a', class_='job-card-container__link')
        if job_title_tag:
            job_data["job_title"] = job_title_tag.text.strip()
            job_data["job_link"] = "https://www.linkedin.com" + job_title_tag['href']
        else:
            job_data["job_title"] = "null"
            job_data["job_link"] = "null"
        
        # Extract company name
        company_tag = job.find('span', class_='job-card-container__primary-description')
        job_data["company"] = company_tag.text.strip() if company_tag else "null"
        
        # Extract location
        location_tag = job.find('li', class_='job-card-container__metadata-item')
        job_data["location"] = location_tag.text.strip() if location_tag else "null"

        # Extract posted date
        posted_date_tag = job.find('time')
        posted_text = posted_date_tag.text.strip() if posted_date_tag else "null"
        job_data["posted_on"] = posted_text
        job_data["posted_date"] = parse_posted_date(posted_text)
        
        # Add placeholders for Employment type and Seniority level
        job_data["Employment type"] = 'null'  # Placeholder, add scraping logic if possible
        job_data["Seniority level"] = 'null'  # Placeholder, add scraping logic if possible
        
        all_jobs.append(job_data)
        jobs_collected += 1

driver.quit()

# Check the length of the jobs list
print(f"Number of jobs collected: {len(all_jobs)}")

# Ensure there is always data to save
if not all_jobs:
    all_jobs.append({
        "job_title": "null",
        "job_link": "null",
        "company": "null",
        "location": "null",
        "posted_on": "null",
        "posted_date": "null",
        "Employment type": "null",
        "Seniority level": "null"
    })

# Save to CSV
df = pd.DataFrame(all_jobs)
df.to_csv(r'jobs.csv', index=False)
print("Data saved to jobs.csv")

# Save to JSON
with open('jobs.json', 'w', encoding='utf-8') as f:
    json.dump(all_jobs, f, ensure_ascii=False, indent=4)
print("Data saved to jobs.json")


