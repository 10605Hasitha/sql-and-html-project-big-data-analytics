import json
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['movie_recommendation']
collection = db['movies']

# Drop the existing collection to start fresh
collection.drop()

# Load movies from the JSON file
with open('movies.json') as file:
    movies = json.load(file)
    collection.insert_many(movies)

print("Data loaded into MongoDB!")
