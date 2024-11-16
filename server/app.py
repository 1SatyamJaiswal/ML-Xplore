from flask import Flask, request, jsonify  # type: ignore
from flask_cors import CORS  # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
import sqlite3
import jwt # type: ignore
import os
import datetime

app = Flask(__name__)

JWT_SECRET = "secret"

# Function to fetch all resources
def fetch_all_resources():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, url, title, description, summary FROM resources")
    resources = cursor.fetchall()
    conn.close()
    return resources

# Function to search resources based on the user's query
def search_resources(query):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT description, summary, url, title, tags, popularity_score FROM resources")
    rows = cursor.fetchall()
    conn.close()

    descriptions, summaries, urls, titles, tags, popularity_scores = zip(*rows) if rows else ([], [], [], [], [])

    # Handle None values and prepare combined texts
    combined_texts = [
        (desc if desc else "") + " " + (summ if summ else "")
        for desc, summ in zip(descriptions, summaries)
    ]

    # Use TF-IDF for searching
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(combined_texts)
    

    # Compute similarity scores for the query
    query_vec = vectorizer.transform([query])
    similarity_scores = (tfidf_matrix @ query_vec.T).toarray().ravel()

    # Normalize similarity scores and popularity scores
    if similarity_scores.any():
        max_sim = max(similarity_scores)
        similarity_scores = [score / max_sim for score in similarity_scores]
    if popularity_scores:
        max_popularity = max(popularity_scores)
        popularity_scores = [score / max_popularity for score in popularity_scores]

    # Combine similarity scores and popularity scores
    combined_scores = [
        0.8 * sim_score + 0.2 * pop_score  # Adjust weights as needed
        for sim_score, pop_score in zip(similarity_scores, popularity_scores)
    ]

    # Pair combined scores with metadata
    results = [
        {"url": url, "title": title, "description": description, "tags": tags, "score": score}
        for url, title, description, tags, score in zip(urls, titles, descriptions, tags, combined_scores)
    ]

    # Sort by similarity score in descending order
    results.sort(key=lambda x: x["score"], reverse=True)

    return results

# Flask route to handle search queries
@app.route('/search', methods=['GET'])
def search_endpoint():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    results = search_resources(query)
    return jsonify(results[:10]), 200

# Combined function to calculate weighted score based on matching tags and popularity
def calculate_weighted_score(resource_tags, user_preferences, popularity_score):
    # Count the number of matching tags
    matching_tags = set(resource_tags) & set(user_preferences)
    tag_score = len(matching_tags)
    
    # Simple weighted average: You can adjust these weights based on your needs
    weighted_score = tag_score * 0.5 + popularity_score * 0.5  # 30% for tag match, 70% for popularity
    return weighted_score

@app.route('/resources', methods=['GET'])
def fetch_resources():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    # Fetch user preferences from the database based on user_id
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT preferences FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    # Fetch all resources from the database
    cursor.execute("""
        SELECT id, url, title, description, tags, popularity_score 
        FROM resources 
        WHERE url NOT LIKE '%privacy%' 
        AND url NOT LIKE '%copyright%'
        AND url NOT LIKE '%terms%'
        AND url NOT LIKE '%policy%'
    """)
    resources = cursor.fetchall()
    conn.close()

    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    user_preferences = user[0].split(',')  # Assuming preferences are stored as comma-separated tags
    
    # Calculate the weighted score for each resource based on matching tags and popularity
    scored_resources = []
    for resource in resources:
        # Split tags and calculate score
        resource_tags = resource[4].split(',')
        score = calculate_weighted_score(resource_tags, user_preferences, resource[5])
        
        # Collect resource details along with score
        scored_resources.append({
            'url': resource[1],
            'title': resource[2],
            'description': resource[3],
            'tags': resource[4],
            'popularity_score': resource[5],
            'score': score
        })
    
    # Sort resources based on their score in descending order
    scored_resources.sort(key=lambda x: x['score'], reverse=True)

    # Return the sorted resources with metadata
    return jsonify(scored_resources[:10]), 200

# Flask route to create a new user
@app.route('/register', methods=['POST'])
def create_user():
    data = request.json
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Extract data from the request
    email = data.get('email')
    name = data.get('name', '')  # Default to empty string if not provided
    password = data.get('password')
    preferences = data.get('preferences', [])  # Default to empty list if not provided

    # Input validation
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if not isinstance(preferences, list):
        return jsonify({"error": "Preferences should be a list"}), 400

    # Convert preferences list to a lowercase, comma-separated string
    preference_csv = ",".join(
        [preference.strip().lower()[:-1] if preference.lower().endswith('s') else preference.strip().lower() for preference in preferences]
    )

    # Store the user in the database
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, name, password, preferences) VALUES (?, ?, ?, ?)",
            (email, name, password, preference_csv)
        )
        conn.commit()
    except sqlite3.Error as e:
        return jsonify({"error": "Database error: " + str(e)}), 500
    finally:
        conn.close()

    return jsonify({"message": "User registered successfully"}), 201

# Flask route to authenticate a user
@app.route('/login', methods=['POST'])
def authenticate_user():
    data = request.json
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Extract data from the request
    email = data.get('email')
    password = data.get('password')

    # Input validation
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Authenticate the user
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, password FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    # Generate a JWT token
    user_id, email, _ = user
    token = jwt.encode({"user_id": user_id, "email": email, "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)}, JWT_SECRET, algorithm="HS256")

    return jsonify({"token": token, "user": user}), 200

def token_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            # Remove "Bearer " if present
            token = token.split(" ")[1] if " " in token else token
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        # Add user info to the request context
        request.user = decoded
        return f(*args, **kwargs)

    return decorated

# Flask route to fetch user details
@app.route('/user', methods=['GET'])
@token_required
def get_user_details():
    user = request.user
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, preferences FROM users WHERE id = ?", (user["user_id"],))
        user = cursor.fetchone()
        conn.close()
    except sqlite3.Error as e:
        return jsonify({"error": "Database error: " + str(e)}), 500
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({"id": user[0], "email": user[1], "name": user[2], "preferences": user[3]}), 200

# Flask route to add user source interaction
@app.route('/route', methods=['POST'])
@token_required
def add_user_source_interaction():
    data = request.json
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Extract data from the request
    user_id = data.get('user_id')
    resource_url = data.get('resource_url')

    # Input validation
    if not resource_url:
        return jsonify({"error": "Source URL and destination URL are required"}), 400

    # Store the user interaction in the database
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_source_interaction (user_id, resource_url) VALUES (?, ?)",
            (user_id, resource_url)
        )
        conn.commit()
    except sqlite3.Error as e:
        return jsonify({"error": "Database error: " + str(e)}), 500
    finally:
        conn.close()

    return jsonify({"message": "User interaction recorded successfully"}), 201

# Flask route to get user history
@app.route('/history', methods=['GET'])
@token_required
def get_user_history():
    user = request.user
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT resource_url FROM user_source_interaction WHERE user_id = ?", (user["user_id"],))
        interactions = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        return jsonify({"error": "Database error: " + str(e)}), 500
    
    data = []
    
    for interaction in interactions:
        data.append(interaction[0])

    return jsonify(data[:10]), 200

# Run Flask app
if __name__ == "__main__":
    CORS(app)
    app.run(debug=True, host='0.0.0.0')
