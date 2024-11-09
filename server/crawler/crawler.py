import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from collections import deque
import time
import os
import re

# Define keywords for each category
category_keywords = {
    "dataset": ["dataset", "data collection", "data source"],
    "model": ["model", "algorithm", "training", "inference"],
    "article": ["article", "guide", "tutorial", "how-to"],
    "research paper": ["research paper", "study", "journal", "publication"]
}

# Function to determine tags based on content
def assign_tags(content):
    tags = []
    for category, keywords in category_keywords.items():
        if any(re.search(r'\b' + keyword + r'\b', content, re.IGNORECASE) for keyword in keywords):
            tags.append(category)
    return ", ".join(tags)

# Database setup
def setup_database():
    conn = sqlite3.connect('../database.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT,
            description TEXT,
            summary TEXT,
            tags TEXT,
            last_crawled DATETIME DEFAULT CURRENT_TIMESTAMP,
            popularity_score FLOAT DEFAULT 0.0
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_url TEXT NOT NULL,
            destination_url TEXT NOT NULL,
            FOREIGN KEY (source_url) REFERENCES resources(url) ON DELETE CASCADE,
            FOREIGN KEY (destination_url) REFERENCES resources(url) ON DELETE CASCADE,
            UNIQUE (source_url, destination_url)
        );
    """)
    conn.commit()
    conn.close()

# Insert a new resource into the database
def store_resource(url, title, description, tags):
    conn = sqlite3.connect('../database.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO resources (url, title, description, tags)
        VALUES (?, ?, ?, ?)
    """, (url, title, description, tags))
    conn.commit()
    conn.close()

# Insert a link between two pages in the database
def store_link(source_url, destination_url):
    conn = sqlite3.connect('../database.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO links (source_url, destination_url)
        VALUES (?, ?)
    """, (source_url, destination_url))
    conn.commit()
    conn.close()

# Condition to check if the page is a Kaggle dataset, model or article
def check_kaggle_page(url):
    # Skip URLs containing special characters or ending with unwanted sections
    if any(symbol in url for symbol in ['#', '?', '%']):
        return None
    
    if url.endswith(('/discussions', '/code', '/suggestions')):
        return None

    # Classify URL based on the type of page on Kaggle
    if 'kaggle.com/dataset' in url:
        return 'dataset'
    elif 'kaggle.com/models' in url:
        return 'model'
    elif 'kaggle.com/learn' in url:
        return 'article'
    elif url == 'https://kaggle.com':
        return 'home'
    else:
        return None

# Set up Selenium WebDriver
PATH = os.getenv('DRIVER_PATH')
chrome_options = Options()
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
service = Service(PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Recursive crawler function
visited_links = set()

def crawl_page(start_url, max_depth):
    # Initialize a queue for breadth-first search with (url, current_depth)
    queue = deque([(start_url, 1)])

    while queue:
        url, depth = queue.popleft()  # Get the next URL and its depth

        # If max depth is reached, skip further crawling from this URL
        if depth > max_depth:
            continue
        
        # Check if the URL has already been visited
        if url in visited_links:
            continue
        visited_links.add(url)  # Mark this URL as visited

        # Check if the page matches a specific category; skip if it doesn't
        if check_kaggle_page(url) is None:
            continue

        # Open the page with Selenium
        try:
            driver.get(url)
            time.sleep(5)  # Allow time for the page to load
        except Exception as e:
            print(f"Failed to load {url}: {e}")
            continue

        # Get page title and description
        title = driver.title
        try:
            description = driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]').get_attribute('content')
        except Exception:
            description = ''  # Default to empty if no description is found

        # Get the page's text content
        content = driver.find_element(By.TAG_NAME, 'body').text
        tags = assign_tags(content)

        # Store the page information in the database
        store_resource(url, title, description, tags)

        # Find all links on the page
        links = driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            try:
                href = link.get_attribute('href')
            except Exception:
                continue

            # Check if the link is valid and should be crawled
            if href and href.startswith('http') and href not in visited_links:
                print(f"Found link from {url} to {href}, current depth is {depth}")
                store_link(url, href)  # Store the link in the database
                # Add the link to the queue with increased depth
                queue.append((href, depth + 1))

# Initialize the database and start crawling
setup_database()
start_url = 'https://kaggle.com'
crawl_page(start_url, max_depth=3)

# Close the WebDriver after crawling
driver.quit()
