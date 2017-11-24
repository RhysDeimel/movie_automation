import requests
from bs4 import BeautifulSoup
import sqlite3
from fabric.api import env, execute, run, task
import re
import sqlite3
import os
import subprocess
import urllib.parse
import signal

#############################
# Scraping
#############################


def find_movies(html):
    """
    Takes an html dump and returns a list of divs that contain the movie entries
    """
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all("div", class_="browse-movie-wrap")


def get_title(movie_div):
    title_elem = movie_div.find("a", class_="browse-movie-title")
    return title_elem.text


def get_year(movie_div):
    year_elem = movie_div.find("div", class_="browse-movie-year")
    return year_elem.text.strip()


def get_category(movie_div):
    def in_categories(tag):
        categories = ["Family", "Crime", "Biography", "Comedy", "Drama", "Adult",
                      "Horror", "Adventure", "War", "Sport", "Sci-Fi", "Short",
                      "Animation", "Thriller", "Romance", "History", "Mystery",
                      "Action", "Western", "Film-Noir", "Documentary", "Musical",
                      "Music", "Fantasy"]
        return tag.text in categories
    category_elem = movie_div.find(in_categories)
    return category_elem.text


def get_rating(movie_div):
    rating_elem = movie_div.find("h4", class_="rating")
    # match "7.2" from "7.2 / 10"
    pattern = re.compile("(\d.\d)|(\d+)")
    re_result = pattern.match(rating_elem.text)
    return re_result.group()


def get_download(movie_div):
    def is_1080p(tag):
        return tag.text == '1080p'
    # Filters through elements based on above
    download_elem = movie_div.find(is_1080p)
    return download_elem.get('href')


def get_movie_details(movie_div):
    return (
        get_title(movie_div),
        get_year(movie_div),
        get_category(movie_div),
        get_rating(movie_div),
        get_download(movie_div),
    )


#############################
# DB functions
#############################


def init_DB(db_dir="", db_filename="movies.db"):
    db_path = os.path.join(db_dir, db_filename)
    with sqlite3.connect(db_path) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS movies
        (id integer primary key autoincrement not null, title text, year text,
        genre text, rating text, download text)''')


def movie_in_DB(movie_details, db_filename="movies.db"):
    """Returns Bool if movie in DB"""
    with sqlite3.connect(db_filename) as conn:
        cursor = conn.cursor()

        query = """
        SELECT count(*) FROM movies
        WHERE title = ? AND year = ?
        """
        cursor.execute(query, (movie_details[0], movie_details[1]))

        result = cursor.fetchone()[0]

    return bool(result)


def write_DB(movie_details, db_filename="movies.db"):
    with sqlite3.connect(db_filename) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS movies
        (id integer primary key autoincrement not null, title text, year text,
        genre text, rating text, download text)''')

        query = '''INSERT INTO MOVIES (title, year, genre, rating, download)
        VALUES (?, ?, ?, ?, ?)'''

        conn.execute(query, (
            movie_details[0],
            movie_details[1],
            movie_details[2],
            movie_details[3],
            movie_details[4])
        )


#############################
#
#############################


def download_torrent(movie_details, dl_dir=""):
    """Takes a tuple of movie details and writes .torrent to directory"""

    # .ag has way less movies than .gs, but uses torrents instead of magnets

    url = "https://yts.gs" + movie_details[-1]
    filename = movie_details[0].strip() + ".torrent"
    r = requests.get(url)
    with open(dl_dir + filename.replace(" ", "_"), "wb") as file:
        file.write(r.content)


def catch_magnet(error):
    start = error[0].find("magnet")
    magnet = error[0][start:-1]
    return urllib.parse.unquote(magnet)


def download_magnet(movie_details, magnet_link, dir='./'):
    assert os.path.exists(dir)

    try:
        output = subprocess.check_output([
            'aria2c', '--bt-metadata-only=true', '--bt-save-metadata=true', '-d {}'.format(dir),
            magnet_link
        ], timeout=960)

        return 'download completed' in output.decode()

    except subprocess.TimeoutExpired:
        return False
    else:
        print('Something went wrong trying to download a magnet link')
        print(movie_details[0])
        print(magnet_link)

#############################
#
#############################


def main():
    # latest 1080p movies with 7+ rating
    url_stub = "https://yts.gs/browse-movies/all/1080p/all/7/latest?page=1"
    # subsequent pages
    # https://yts.gs/browse-movies/all/1080p/all/7/latest?page=2
    r = requests.get(url_stub)
    r.raise_for_status()
    movie_divs = find_movies(r.text)

    movies = [get_movie_details(div) for div in movie_divs]

    init_DB()

    for movie in movies:
        if not movie_in_DB(movie):

            try:
                download_torrent(movie)
                write_DB(movie)
            except requests.exceptions.InvalidSchema as e:
                magnet_link = catch_magnet(e.args)
                if download_magnet(movie, magnet_link):
                    write_DB(movie)





    # log into NAS
    #   move torrent files to watch directory

    # Check finished download directory
    #   Rename files based on best match
    #   Delete unimportant files
    #   Move to storage dir




if __name__ == "__main__":
    main()
