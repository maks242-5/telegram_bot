import json
import os

DATA_FILE = "data.json"


def get_films(film_id=None):
    
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        with open(DATA_FILE, "w", encoding="utf-8") as fp:
            fp.write("[]")

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as fp:
            films = json.load(fp)
    except json.JSONDecodeError:
        films = []
        with open(DATA_FILE, "w", encoding="utf-8") as fp:
            json.dump(films, fp)

    if film_id is not None:
        return films[film_id] if 0 <= film_id < len(films) else None
    return films


def add_film(film: dict):
    films = get_films()
    films.append(film)
    with open(DATA_FILE, "w", encoding="utf-8") as fp:
        json.dump(films, fp, ensure_ascii=False, indent=2)


class Film:
    def __init__(self, name, description, rating, genre, actors, poster, year=None):
        self.name = name
        self.description = description
        self.rating = rating
        self.genre = genre
        self.actors = actors
        self.poster = poster
        self.year = year

    def model_dump(self):
        return {
            "name": self.name,
            "description": self.description,
            "rating": self.rating,
            "genre": self.genre,
            "actors": self.actors,
            "poster": self.poster,
            "year": self.year,
        }
