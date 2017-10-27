import requests
from bs4 import BeautifulSoup
import sqlite3
import fabric


def find_movies(html):
    """
    Takes an html dump and returns a list of divs that contain the movie entries
    """
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all("div", class_="browse-movie-wrap")


def get_title(match_obj):
    pass


def get_year(match_obj):
    pass


def get_category(match_obj):
    pass


def get_rating(match_obj):
    pass


def get_download(match_obj):
    pass


def get_movie_details(match_obj):
    """
    Given a match obj, will return a tuple of:
    (title, year, category, rating, download)
    """
    return (
        get_title(match_obj),
        get_year(match_obj),
        get_category(match_obj),
        get_rating(match_obj),
        get_download(match_obj),
    )



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

def html_stub_a():
    with open("tests/Page1.html") as f:
        return f.read()

test = html_stub_a()
test = find_movies(test)
print(test[0])


# https://yts.gs/browse-movies/all/1080p/all/7/latest
# https://yts.gs/browse-movies/all/1080p/all/7/latest?page=2