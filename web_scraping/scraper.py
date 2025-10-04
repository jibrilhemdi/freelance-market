import time
import pandas as pd
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import re
import random
from tqdm import tqdm

categories = [
    'data-science', 'data-analysis', 'r', 'artificial-intelligence',
    'bot-development', 'chatbot-development', 'computer-vision',
    'data-extraction', 'data-visualization', 'data-mining',
    'deep-learning', 'data-cleansing', 'imageobject-recognition',
    'ocr-tesseract',
]
job_data = []

options = uc.ChromeOptions()
# options.add_argument("--headless=new")
driver = uc.Chrome(options=options)

for category in tqdm(categories, desc="Scraping progress"):
    print(f"Scraping category: {category}")
    url = f"https://www.upwork.com/freelance-jobs/{category}/"
    driver.get(url)
    time.sleep(random.uniform(4, 7))

    while True:
        try:
            load_more = driver.find_element(By.CSS_SELECTOR, 'a[data-qa="load-more"]')
            driver.execute_script("arguments[0].scrollIntoView();", load_more)
            load_more.click()
            time.sleep(random.uniform(3, 5))
        except:
            break

    job_cards = driver.find_elements(By.CSS_SELECTOR, 'section[data-qa="job-tile"]')

    for card in job_cards:
        try:
            title_elem = card.find_element(By.CSS_SELECTOR, 'a[data-qa="job-title"]')
            title = title_elem.text.strip()
            link = "https://www.upwork.com" + title_elem.get_attribute("href")

            # Price
            price = ""
            try:
                price_elem = card.find_element(By.CSS_SELECTOR, 'strong')
                price_text = price_elem.text.strip()
                if "$" in price_text:
                    price = price_text
            except:
                pass

            # Working hours
            working_hour = ""
            try:
                hour_elem = card.find_element(By.CSS_SELECTOR, 'strong[data-qa="value"]')
                hour_text = hour_elem.text.strip().lower()
                if "hrs/week" in hour_text or "hours" in hour_text or "not sure" in hour_text:
                    working_hour = hour_text
            except:
                pass

            # Expertise level
            expertise_level = ""
            try:
                level_elem = card.find_elements(By.CSS_SELECTOR, 'strong[data-qa="value"]')
                for elem in level_elem:
                    level_text = elem.text.strip().lower()
                    if "entry" in level_text or "intermediate" in level_text or "expert" in level_text:
                        expertise_level = level_text
                        break
            except:
                pass

            # Post date
            post_date = ""
            try:
                date_elem = card.find_element(By.CSS_SELECTOR, 'small.text-muted-on-inverse')
                date_text = date_elem.text.strip().lower()
                if re.search(r"(\\d+\\s+(day|days|hour|hours)\\s+ago)", date_text):
                    post_date = date_text
            except:
                pass

            # Skills
            skills_elems = card.find_elements(By.CSS_SELECTOR, 'span[data-qa*="skill"]')
            skills = [skill.text.strip() for skill in skills_elems]

            job_data.append({
                "Category": category,
                "Title": title,
                "Price": price,
                "Working Hour": working_hour,
                "Expertise Level": expertise_level,
                "Post Date": post_date,
                "Skills": ", ".join(skills),
                "Link": link
            })
        except:
            continue

driver.quit()

df = pd.DataFrame(job_data)
df.to_csv("upwork_jobs.csv", index=False)
# print(df.head())
