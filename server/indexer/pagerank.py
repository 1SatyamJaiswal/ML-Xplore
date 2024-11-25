import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH', './database.db')

DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), DATABASE_PATH))

# Function to fetch all links from the database
def fetch_links():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT source_url, destination_url FROM links")
    links = cursor.fetchall()
    conn.close()
    return links

# Function to initialize the PageRank dictionary with equal values
def initialize_pagerank(links):
    pages = set()
    for source, destination in links:
        pages.add(source)
        pages.add(destination)

    pagerank = {page: 1.0 for page in pages}  # Initialize each page with a rank of 1.0
    return pagerank, pages

# Function to calculate the PageRank of all pages
def calculate_pagerank(links, damping_factor=0.85, iterations=20):
    # Initialize the pagerank and set of pages
    pagerank, pages = initialize_pagerank(links)

    # Create an inbound and outbound link structure
    inbound_links = {page: [] for page in pages}  # Pages that link to a given page
    outbound_links = {page: 0 for page in pages}  # Count of outbound links for each page

    # Fill inbound and outbound link data
    for source, destination in links:
        inbound_links[destination].append(source)
        outbound_links[source] += 1

    # Perform iterations to update the PageRank values
    for _ in range(iterations):
        new_pagerank = {}
        for page in pages:
            rank_sum = 0
            for inbound_page in inbound_links[page]:
                rank_sum += pagerank[inbound_page] / outbound_links[inbound_page] if outbound_links[inbound_page] > 0 else 0
            new_pagerank[page] = (1 - damping_factor) + damping_factor * rank_sum

        # Update pagerank values after each iteration
        pagerank = new_pagerank

    return pagerank

# Function to store the PageRank scores in the database
def store_pagerank(pagerank):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    for url, score in pagerank.items():
        cursor.execute("UPDATE resources SET popularity_score = ? WHERE url = ?", (score, url))
    conn.commit()
    conn.close()
    print("PageRank scores updated successfully.")

# Main function to calculate and store PageRank scores
def main():
    # Fetch all links from the database
    links = fetch_links()

    # Calculate PageRank scores
    pagerank = calculate_pagerank(links)

    # Store PageRank scores in the database
    store_pagerank(pagerank)

# Run the main function
if __name__ == "__main__":
    main()
