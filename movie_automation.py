import requests
from bs4 import BeautifulSoup
import sqlite3
import fabric
import re
import sqlite3

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
    # <h4>Horror</h4>
    category_elem = movie_div.find(in_categories)
    return category_elem.text


def get_rating(movie_div):
    rating_elem = movie_div.find("h4", class_="rating")
    pattern = re.compile("(\d.\d)|(\d?)")
    re_result = pattern.match(rating_elem.text)
    return re_result.group()


def get_download(movie_div):
    def is_1080p(tag):
        return tag.text == '1080p'
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


def movie_in_DB(movie_details, db_filename):
    with sqlite3.connect(db_filename) as conn:
        cursor = conn.cursor()

        query = """
        select stuff from movies
        where title = ? and year = ?
        """

        cursor.execute(query (stuff))

        # make a selection from title and year
        # if result == 0, return False, else True



# go to website

# get listings from the first 5 pages
#   get title
#   get year
#   get category
#       if not in DB
#       download .torrent
#       move .torrent to correct directory
#       store in DB for use when naming

# check completed folder for finished movies
#   if not empty
#       get folder & file names
#       delete anything that isn't a movie or subtitle file
#       rename folder and files based on DB cross reference
#       move to movies folder on the NAS

# table schema?
#
# id # title # year # category # rating # started # completed

# def html_stub_a():
#     with open("tests/Page1.html") as f:
#         return f.read()

# test = html_stub_a()
# test = find_movies(test)
# print(get_rating(test[0]))
def main():
    # latest 1080p movies with 7+ rating
    url = "https://yts.gs/browse-movies/all/1080p/all/7/latest"
    # subsequent pages
    # https://yts.gs/browse-movies/all/1080p/all/7/latest?page=2





if __name__ == "__main__":
    pass
