from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import os
from pymongo import MongoClient

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

mongo_client = MongoClient(mongo_uri,tls=True,tlsAllowInvalidCertificates=True)
mongo_db = mongo_client['job_scraper']  # Replace with your database name
mongo_collection = mongo_db['processeng_jobs']  # Replace with your collection name



def analyze_job_with_ai(job_title, job_description):
    """Send job details to GPT-4 for analysis."""
    prompt = f"""
    Analyze the following job posting:
    Job Title: {job_title}
    Job Description: {job_description}


    Determine if this job is suitable for someone with experience below:
    "Bachelor in Chemical Engineering, an experienced process control engineer specializing in the design 
    and optimization of hydroprocessing units, with a strong focus on operational efficiency. 
    As a Senior Operation Engineer, I developed MEGAT, a virtual assistant that leverages Power BI and Python 
    to streamline reporting and optimize unit operations. I have successfully managed complex projects, 
    including the commissioning of new plants, ensuring adherence to safety protocols as the Resident Engineer for a 
    Group III+ base oil plant. My expertise extends to safety governance, where I implemented critical procedures 
    to enhance safety culture. Proficient in data analysis and process simulations, I excel in troubleshooting high-pressure 
    situations and leading multidisciplinary teams. With advanced technical skills in programming and engineering software, 
    I am dedicated to driving innovation and achieving project success in fast-paced environments."


    Provide a summary of one paragraphs why or why not and include any recommendations.
    Always start your analysis with "Yes" or "No".
    """
    response = openai_client.chat.completions.create(  
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are an AI assistant for analyzing job postings."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# MongoDB Function
def insert_job_into_mongo(collection, job_data):
    """Insert job data into MongoDB, avoiding duplicates."""
    existing_job = collection.find_one({"Job ID": job_data['Job ID']})
    if not existing_job:
        job_data['Applied'] = False  # Add the 'Applied' field
        collection.insert_one(job_data)
        print(f"Inserted job: {job_data['Title']} ({job_data['Job ID']})")
    else:
        print(f"Job already exists: {job_data['Title']} ({job_data['Job ID']})")


def scrape_jobs(base_url, keyword="Process Engineer", location="", num_jobs=30):
    # Initialize Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(base_url)

    try:
        # Perform search
        keyword_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.keywordsearch-q"))
        )
        location_input = driver.find_element(By.CSS_SELECTOR, "input.keywordsearch-locationsearch")
        search_button = driver.find_element(By.CSS_SELECTOR, "input.keywordsearch-button")

        keyword_input.clear()
        keyword_input.send_keys(keyword)
        location_input.clear()
        location_input.send_keys(location)
        search_button.click()

        time.sleep(3)

    except Exception as e:
        print("Search interaction failed:", e)
        driver.quit()
        return []

    try:
        jobs = []
        scraped_job_ids = set()  # To track scraped job IDs in the current session
        while len(jobs) < num_jobs:
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_rows = soup.select('tr.data-row')  # Ensure this matches your HTML structure

            if not job_rows:
                print("No job rows found.")
                break

            for row in job_rows:
                try:
                    # Extract job details
                    title_elem = row.find('a', class_='jobTitle-link')
                    job_id_elem = row.find('span', class_='jobFacility')
                    location_elem = row.find('span', class_='jobLocation')
                    department_elem = row.find('span', class_='jobDepartment')

                    # Ensure elements are valid
                    title = title_elem.text.strip() if title_elem else "N/A"
                    job_id = job_id_elem.text.strip() if job_id_elem else "N/A"
                    location = location_elem.text.strip() if location_elem else "N/A"
                    department = department_elem.text.strip() if department_elem else "N/A"
                    link = "https://careers.aramco.com" + title_elem['href'] if title_elem else "N/A"

                    # Skip job if it already exists in MongoDB or was scraped earlier
                    if mongo_collection.find_one({"Job ID": job_id}) or job_id in scraped_job_ids:
                        continue

                    # Fetch job details
                    driver.get(link)
                    time.sleep(3)

                    detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    description_elem = detail_soup.find('span', class_='jobdescription')
                    job_description = description_elem.text.strip() if description_elem else "No description available."

                    # Analyze with AI
                    analysis = analyze_job_with_ai(title, job_description)

                    # Add job data
                    job_data = {
                        'Title': title,
                        'Job ID': job_id,
                        'Location': location,
                        'Department': department,
                        'Link': link,
                        'AI Analysis': analysis,
                        'Apply': analysis[0],
                        'Applied': False  # Initialize as False
                    }

                    insert_job_into_mongo(mongo_collection, job_data)
                    jobs.append(job_data)
                    scraped_job_ids.add(job_id)

                    if len(jobs) >= num_jobs:
                        break

                except Exception as e:
                    print(f"Error parsing job row: {e}")

            # Check for next page using pagination
            try:
                pagination = soup.select_one('ul.pagination')
                if not pagination:
                    print("Pagination not found.")
                    break

                current_page = pagination.find('li', class_='active')
                if not current_page:
                    print("Current page not found in pagination.")
                    break

                # Find the next page anchor
                next_page = current_page.find_next_sibling('li')
                if not next_page or not next_page.find('a'):
                    print("No next page available.")
                    break

                # Click the next page link
                next_page_link = next_page.find('a')['href']
                driver.get(base_url + next_page_link)

            except Exception as e:
                print("Pagination navigation failed:", e)
                break

    finally:
        driver.quit()

    return jobs




# URL for Aramco Careers
base_url = "link to website"
jobs_data = scrape_jobs(base_url, keyword="Process Engineer", num_jobs=20)
# Insert into MongoDB
print("Job scraping completed. Data saved to MongoDB.")