import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
import time
import os

# Function to fetch all page URLs from resources
def fetch_all_pages():
    conn = sqlite3.connect('../database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT url, description FROM resources")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Set up Selenium WebDriver
def setup_driver():
    PATH = os.getenv('DRIVER_PATH')  # Set your webdriver path
    chrome_options = Options()
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")  # Run in headless mode for efficiency
    service = Service(PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to fetch the body text of a webpage
def fetch_page_body(url, driver):
    driver.get(url)
    time.sleep(5)  # Wait for the page to load completely
    body = driver.find_element(By.TAG_NAME, 'body').text # Extract the text of the body tag
    return body

# Index and store summaries with TF-IDF
def generate_summaries():
    pages = fetch_all_pages()
    urls, descriptions = zip(*pages)

    # Set up Selenium driver
    driver = setup_driver()

    # Generate TF-IDF vectors for page descriptions and body content
    vectorizer = TfidfVectorizer(max_features=30, stop_words='english')

    summaries = []
    for url in urls:
        try:
            print(f"Processing URL: {url}")
            # Fetch the page body content
            page_body = fetch_page_body(url, driver)

            # Combine the description and page body for better results
            full_content = descriptions[urls.index(url)] + " " + page_body

            # Apply TF-IDF vectorizer to the full content (description + body)
            tfidf_matrix = vectorizer.fit_transform([full_content])

            # Get the top TF-IDF terms
            terms = vectorizer.get_feature_names_out()
            sorted_terms = [terms[i] for i in tfidf_matrix[0].indices]
            summary = " ".join(sorted_terms[:20])  # Take top 20 words as summary
            summaries.append((url, summary))

        except Exception as e:
            print(f"Error processing {url}: {e}")
            summaries.append((url, ''))  # If error occurs, assign empty summary

    # Update summaries in the database
    conn = sqlite3.connect('../database.db')
    cursor = conn.cursor()
    for url, summary in summaries:
        cursor.execute("UPDATE resources SET summary = ? WHERE url = ?", (summary, url))
    conn.commit()
    conn.close()
    print("Summaries updated successfully.")

    # Close the driver after all operations
    driver.quit()

# Run the indexer to generate summaries
generate_summaries()
