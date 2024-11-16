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
    cursor.execute("SELECT url, description FROM resources WHERE summary IS NULL OR summary = ''")
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
    body = driver.find_element(By.TAG_NAME, 'body').text  # Extract the text of the body tag
    return body

# Index and store summaries with TF-IDF
def generate_summaries():
    pages = fetch_all_pages()
    urls, descriptions = zip(*pages)

    # Set up Selenium driver
    driver = setup_driver()

    # Generate TF-IDF vectors for page descriptions and body content
    vectorizer = TfidfVectorizer(max_features=30, stop_words='english')

    # Open database connection
    conn = sqlite3.connect('../database.db')
    cursor = conn.cursor()

    for url, description in zip(urls, descriptions):
        try:
            print(f"Processing URL: {url}")
            # Fetch the page body content
            page_body = fetch_page_body(url, driver)

            # Combine the description and page body for better results
            full_content = (description or '') + " " + page_body

            # Apply TF-IDF vectorizer to the full content (description + body)
            tfidf_matrix = vectorizer.fit_transform([full_content])

            # Get the top TF-IDF terms
            terms = vectorizer.get_feature_names_out()
            sorted_terms = [terms[i] for i in tfidf_matrix[0].indices]
            summary = " ".join(sorted_terms[:20])  # Take top 20 words as summary

            # Update the summary in the database immediately
            cursor.execute("UPDATE resources SET summary = ? WHERE url = ?", (summary, url))
            conn.commit()
            print(f"Updated summary for {url}")

        except Exception as e:
            print(f"Error processing {url}: {e}")
            # Update the summary with an empty value in case of error
            cursor.execute("UPDATE resources SET summary = ? WHERE url = ?", ('', url))
            conn.commit()

    # Close the database connection and driver
    conn.close()
    driver.quit()
    print("Summaries updated successfully.")

# Run the indexer to generate summaries
generate_summaries()
