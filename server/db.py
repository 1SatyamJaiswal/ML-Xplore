import sqlite3

# Connect to the database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# SQL query to create the 'resources' table
create_resources_table_query = """
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    description TEXT,
    summary TEXT,               -- Concise summary generated based on TF-IDF
    tags TEXT,                  -- Keywords or categories
    last_crawled DATETIME DEFAULT CURRENT_TIMESTAMP,
    popularity_score FLOAT DEFAULT 0.0
);
"""
cursor.execute(create_resources_table_query)
print("Table 'resources' created successfully.")

# SQL query to create the 'links' table
create_links_table_query = """
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_url TEXT NOT NULL,
    destination_url TEXT NOT NULL,
    FOREIGN KEY (source_url) REFERENCES resources(url) ON DELETE CASCADE,
    FOREIGN KEY (destination_url) REFERENCES resources(url) ON DELETE CASCADE,
    UNIQUE (source_url, destination_url)
);
"""
cursor.execute(create_links_table_query)
print("Table 'links' created successfully.")

conn.commit()
conn.close()
