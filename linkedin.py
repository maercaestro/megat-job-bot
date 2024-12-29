import time
import math
import random
import os
import pickle
import hashlib
from dotenv import load_dotenv
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
import openai

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri)
db = mongo_client["linkedin_bot"]
applications_collection = db["applications"]

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

class Linkedin:
    def __init__(self):
        # Set up Chrome options
        self.driver = webdriver.Chrome(options=self.chrome_browser_options())
        
        # Start LinkedIn automation
        self.cookies_path = f"{os.path.join(os.getcwd(), 'cookies')}/{self.get_hash('YourEmail@example.com')}.pkl"
        self.driver.get("https://www.linkedin.com")
        self.load_cookies()

        if not self.is_logged_in():
            self.driver.get("https://www.linkedin.com/login")
            print("🔄 Logging in to LinkedIn...")
            self.login()

        self.link_job_apply()

    def chrome_browser_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        # Uncomment the next line to enable headless mode
        # options.add_argument("--headless")
        return options
    
    def get_hash(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    def load_cookies(self):
        if os.path.exists(self.cookies_path):
            cookies = pickle.load(open(self.cookies_path, "rb"))
            self.driver.delete_all_cookies()
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def save_cookies(self):
        pickle.dump(self.driver.get_cookies(), open(self.cookies_path, "wb"))

    def is_logged_in(self):
        self.driver.get('https://www.linkedin.com/feed')
        try:
            self.driver.find_element(By.XPATH, '//*[@id="global-nav-typeahead"]')
            return True
        except:
            return False

    def login(self):
        try:
            self.driver.find_element("id", "username").send_keys(os.getenv("LINKEDIN_EMAIL"))
            self.driver.find_element("id", "password").send_keys(os.getenv("LINKEDIN_PASSWORD"))
            self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
            time.sleep(5)
            self.save_cookies()
        except Exception as e:
            print(f"❌ Login failed: {e}")

    def analyze_job_with_ai(self, job_title, job_description):
        """Analyze the job description using OpenAI GPT."""
        prompt = f"""
        Analyze the following job posting:
        Job Title: {job_title}
        Job Description: {job_description}
        
        Determine if this job is suitable for someone with the following profile:
        - Experienced Process Engineer.
        - Expertise in optimization and hydroprocessing.
        - Proficient in Python and Power BI.
        
        Provide a summary in one paragraph starting with "Yes" or "No".
        """
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=150
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"❌ AI analysis failed: {e}")
            return "Error in analysis."

    def save_application_result(self, job_id, title, company, status, url):
        application_data = {
            "job_id": job_id,
            "title": title,
            "company": company,
            "status": status,
            "url": url,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        applications_collection.insert_one(application_data)
        print(f"Saved application result for {title} at {company}.")

    def link_job_apply(self):
        # Assuming job URLs are stored in a file 'job_urls.txt'
        with open('job_urls.txt', 'r') as file:
            urls = file.readlines()

        for url in urls:
            self.driver.get(url.strip())
            time.sleep(random.uniform(1, 3))  # Random delay to mimic human behavior

            try:
                job_title = self.driver.find_element(By.XPATH, "//h1[contains(@class, 'job-title')]").text
                job_description = self.driver.find_element(By.XPATH, "//div[contains(@class, 'job-description')]").text
                company_name = self.driver.find_element(By.XPATH, "//a[contains(@class, 'topcard__org-name-link')]").text
                job_id = url.split("/")[-1]  # Extract job ID from URL

                # AI Analysis
                analysis = self.analyze_job_with_ai(job_title, job_description)
                if analysis.startswith("Yes"):
                    easy_apply_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Easy Apply')]")
                    easy_apply_button.click()
                    time.sleep(random.uniform(1, 3))
                    print(f"✅ Successfully applied to {job_title} at {company_name}.")
                    self.save_application_result(job_id, job_title, company_name, "Success", url)
                else:
                    print(f"❌ Skipping {job_title} at {company_name}: {analysis}")
                    self.save_application_result(job_id, job_title, company_name, "Skipped", url)

            except Exception as e:
                print(f"❌ Failed to apply to job: {e}")
                self.save_application_result(job_id, "Unknown", "Unknown", "Failed", url)

if __name__ == "__main__":
    Linkedin()
