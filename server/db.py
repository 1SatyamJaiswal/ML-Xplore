import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH', './database.db')

# Connect to the database
conn = sqlite3.connect(DATABASE_PATH)
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

# SQL query to create the 'users' table with preferences column
create_users_table_query = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- Storing hashed password is recommended
    preferences TEXT,        -- JSON or CSV string to store preferences for article, model, etc.
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""
cursor.execute(create_users_table_query)
print("Table 'users' created successfully.")

# SQL query to create the 'user_source_interaction' table without resource_type
create_user_source_interaction_table_query = """
CREATE TABLE IF NOT EXISTS user_source_interaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,  -- Foreign Key to users table
    resource_url TEXT NOT NULL,  -- Resource URL the user interacts with
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resource_url) REFERENCES resources(url) ON DELETE CASCADE
);
"""
cursor.execute(create_user_source_interaction_table_query)
print("Table 'user_source_interaction' created successfully.")

conn.commit()
conn.close()
