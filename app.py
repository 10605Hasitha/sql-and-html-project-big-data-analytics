from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import pandas as pd

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['movie_recommendation']
movies_collection = db['movies']

# Load movies from MongoDB into a DataFrame
movies_data = list(movies_collection.find())
movies_df = pd.DataFrame(movies_data)

# Ensure fields exist in the DataFrame
for field in ['description', 'hero', 'heroine', 'poster', 'year', 'cast', 'where_to_watch']:
    if field not in movies_df.columns:
        movies_df[field] = ""

# Preprocess the data to combine genres into a single string
movies_df['genres_combined'] = movies_df['genres'].apply(lambda x: ' '.join(x))

def recommend_movies_by_genre(genre):
    normalized_genre = genre.strip().lower()
    genre_movies = movies_df[movies_df['genres'].apply(lambda x: normalized_genre in [g.lower() for g in x])]
    if genre_movies.empty:
        return []
    sorted_movies = genre_movies.sort_values(by='rating', ascending=False)
    recommendations = sorted_movies[['title', 'rating', 'description', 'hero', 'heroine', 'poster', 'year', 'cast', 'where_to_watch']].drop_duplicates(subset=['title']).to_dict(orient='records')
    return recommendations

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    genre = request.form.get('genre')
    recommendations = recommend_movies_by_genre(genre)
    return jsonify({'recommendations': recommendations}) if recommendations else jsonify({'recommendations': []})

# New route for movie details
@app.route('/movie/<title>')
def movie_details(title):
    # Find movie by title in the database
    movie = movies_collection.find_one({'title': title})
    if movie:
        return render_template('movie_details.html', movie=movie)
    return "Movie not found", 404

if __name__ == '__main__':
    app.run(debug=True)
