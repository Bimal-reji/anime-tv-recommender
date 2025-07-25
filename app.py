from flask import Flask, render_template, request, jsonify
import random
import requests

app = Flask(__name__)

ANIME_GENRES = {
    "Action": 1,
    "Adventure": 2,
    "Comedy": 4,
    "Drama": 8,
    "Fantasy": 10,
    "Horror": 14,
    "Mystery": 7,
    "Psychological": 40,
    "Romance": 22,
    "Sci-Fi": 24,
    "Slice of Life": 36,
    "Sports": 30,
    "Thriller": 41
}

TV_GENRES = [
    "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary",
    "Drama", "Family", "Fantasy", "Horror", "Mystery", "Romance",
    "Science-Fiction", "Thriller", "War", "Western"
]

@app.route('/')
def home():
    return render_template("index.html", anime_genres=ANIME_GENRES, tv_genres=TV_GENRES)

@app.route('/recommend')
def recommend():
    content_type = request.args.get("type", "anime")
    genre = request.args.get("genre")

    if content_type == "anime":
        return jsonify(get_random_anime_by_genre(int(genre)))
    elif content_type == "tv":
        return jsonify(get_random_tvmaze_show_by_genre(genre.lower()))
    else:
        return jsonify({"title": "Error", "description": "Invalid type", "image": None})

def get_random_anime_by_genre(genre_id: int) -> dict:
    BASE_URL = "https://api.jikan.moe/v4/anime"
    for _ in range(5):
        page = random.randint(1, 20)
        params = {
            "genres": genre_id,
            "page": page,
            "order_by": "score",
            "sort": "desc"
        }
        try:
            r = requests.get(BASE_URL, params=params, timeout=10)
            if r.status_code != 200:
                continue
            data = r.json().get("data", [])
            if not data:
                continue
            anime = random.choice(data)
            image_url = anime.get("images", {}).get("jpg", {}).get("image_url")
            return {
                "title": anime.get("title"),
                "description": anime.get("synopsis", "No synopsis available."),
                "image": image_url
            }
        except Exception as e:
            continue

    return {
        "title": "No result",
        "description": "Could not fetch anime. Try again later.",
        "image": None
    }

def get_random_tvmaze_show_by_genre(genre: str) -> dict:
    try:
        response = requests.get("https://api.tvmaze.com/shows", timeout=10)
        if response.status_code != 200:
            return {"title": "Error", "description": "TVMaze API error.", "image": None}
        shows = response.json()
        filtered = [s for s in shows if genre in [g.lower() for g in s.get("genres", [])]]
        if not filtered:
            return {"title": "No match", "description": "No shows found in this genre.", "image": None}
        show = random.choice(filtered)
        return {
            "title": show.get("name"),
            "description": show.get("summary", "No description available.").replace("<p>", "").replace("</p>", ""),
            "image": show.get("image", {}).get("medium")
        }
    except Exception as e:
        return {"title": "Error", "description": str(e), "image": None}

if __name__ == "__main__":
    app.run(debug=True)
