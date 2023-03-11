from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

URL = 'https://www.naukri.com/python-jobs?k=python'


def get_driver():
    """ Adds the arguments to the selenium driver """
    options = Options()
    options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36')
    driver = webdriver.Chrome(options=options)
    return driver

def get_jobs(driver):
    """ Returns all the jobs available in the current page as webElement """
    jobs = driver.find_elements(By.CLASS_NAME, 'jobTuple')
    return jobs 

def parse_job(job):
    """ Returns the dictionary for job details of single webElement """
    #job_role 
    job_tag = job.find_element(By.CLASS_NAME, 'title')
    job_role = job_tag.text
    job_url = job_tag.get_attribute('href')
    #Company 
    cmpny_tag = job.find_element(By.CLASS_NAME, 'companyInfo')
    cmpny_name = cmpny_tag.find_element(By.TAG_NAME, 'a').text
    # Loaction 
    location_tag = job.find_element(By.CLASS_NAME, 'location')
    location = location_tag.find_element(By.TAG_NAME, 'span').text
    # Key Skills
    key_skill_tag = job.find_element(By.CLASS_NAME, 'has-description')
    key_skills = [i.text for i in key_skill_tag.find_elements(By.TAG_NAME, 'li')]
    # Posted date 
    posted_date = job.find_element(By.CLASS_NAME, 'postedDate').text
    return {
        'Job' : job_role,
        'CompanyName' : cmpny_name,
        'Location' : location,
        'KeySkills' : key_skills,
        'PostedDate':posted_date,
        'Link':job_url
    }

def current_page_data(driver, wait):
    # Wait till the page get ;paded
    wait.until(lambda driver: driver.find_element(By.CLASS_NAME, 'companyInfo'))
    jobs = get_jobs(driver)
    current_pg_jobs = [parse_job(job) for job in jobs[:len(jobs)]]
    jobs_df = pd.DataFrame(current_pg_jobs, index=None)
    return jobs_df


# Setting up the driver
driver = get_driver()
driver.get(URL)


# Explicit wait declaration
wait = WebDriverWait(driver, 30)


# Sorting the jobs by date
sort_wait = wait.until(lambda driver: driver.find_element(By.CLASS_NAME, 'sort-droop-label'))
driver.find_element(By.CLASS_NAME, 'sort-droop-label').click()
driver.find_element(By.CSS_SELECTOR, 'li[data-value="f"]').click()


# Accept the cookies if pop up appears
try :
    driver.find_element(By.XPATH, "//button[text()='Got it']").click()
except:
    print("Cookie request not found")


# Initializing the dataframe
jobs_df = pd.DataFrame(columns=[ 'Job','CompanyName','Location','KeySkills','PostedDate','Link'], index=None)


for i in range(40): # this 40 can be raised till we want multiples of 20 jobs
    jobs_df = pd.concat(
        [jobs_df,(current_page_data(driver, wait))]
        )
    wait.until(lambda driver: driver.find_element(By.CLASS_NAME, 'naukicon-arrow-2'))
    next_page_tag = driver.find_elements(By.CLASS_NAME, 'naukicon-arrow-2')
    next_page_tag[1].click()

jobs_df.to_csv('Python_jobs.csv', index=None)

