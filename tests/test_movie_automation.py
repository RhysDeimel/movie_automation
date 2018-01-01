from bs4 import BeautifulSoup
import pytest
import movie_automation as mva
import sqlite3
import os
import shutil
import secrets

test_names = """
2.22.2017.1080p.BluRay.H264.AAC-RARBG
47.Meters.Down.2017.1080p.BluRay.H264.AAC-RARBG
All.The.Kings.Men.2006.1080p.BluRay.H264.AAC-RARBG
A.Woman.a.Part.2016.WEBRip.x264-RARBG
A.World.Apart.1988.1080p.BluRay.H264.AAC-RARBG
Cabaret.1972.1080p.BluRay.H264.AAC-RARBG
Cameraman.The.Life.and.Work.of.Jack.Cardiff.2010.WEBRip.x264-RARBG
Churchill.2017.1080p.BluRay.H264.AAC-RARBG
Death.Trap.1982.1080p.BluRay.H264.AAC-RARBG
Dying.To.Do.Letterman.2011.WEBRip.x264-RARBG
Dying.to.Know.Ram.Dass.and.Timothy.Leary.2014.WEBRip.x264-RARBG
Grizzly.Man.2005.1080p.BluRay.H264.AAC-RARBG
Hachiko.A.Dogs.Story.2009.1080p.BluRay.H264.AAC-RARBG
Heaven.and.Earth.1993.1080p.BluRay.H264.AAC-RARBG
Here.One.Minute.2015.WEBRip.x264-RARBG
Key.of.Brown.2013.WEBRip.x264-RARBG
Macbeth.2010.WEBRip.x264-RARBG
Map.of.the.Human.Heart.1992.1080p.BluRay.H264.AAC-RARBG
Mysterious.Skin.2004.720p.BluRay.H264.AAC-RARBG
Raid.on.Rommel.1971.WEBRip.x264-RARBG
Residue.2017.WEBRip.x264-RARBG
Rough.Night.2017.1080p.BluRay.H264.AAC-RARBG
Starship.Troopers.Traitor.of.Mars.2017.1080p.BluRay.H264.AAC-RARBG
The.Last.Laugh.2016.WEBRip.x264-RARBG
They.Shoot.Horses.Dont.They.1969.1080p.BluRay.H264.AAC-RARBG
"""

###########################
# Scraping tests
###########################


def test_find_movies(html_stub):
    """
    20 movies exist on the page
    """
    matches = mva.find_movies(html_stub)
    assert len(matches) == 20


# TODO - move these to integration testing and replace with unit tests
# in the style of test_get_rating_10_of_10

def test_get_title(movie_div):
    expected = "angel heart"
    assert mva.get_title(movie_div) == expected


def test_get_year(movie_div):
    expected = "1987"
    assert mva.get_year(movie_div) == expected


def test_get_category(movie_div):
    expected = "horror"
    assert mva.get_category(movie_div) == expected


def test_get_rating_decimal(movie_div):
    expected = "7.3"
    assert mva.get_rating(movie_div) == expected


def test_get_rating_10_of_10():
    html = '<div class="browse-movie-wrap"><h4 class="rating">10 / 10</h4></div>'
    movie_div = mock_div_parser(html)
    expected = "10"
    assert mva.get_rating(movie_div) == expected


def test_get_rating_whole_number():
    html = '<div class="browse-movie-wrap"><h4 class="rating">8 / 10</h4></div>'
    movie_div = mock_div_parser(html)
    expected = "8"
    assert mva.get_rating(movie_div) == expected


def test_get_download(movie_div):
    expected = "/download/9994"
    assert mva.get_download(movie_div) == expected


def test_get_movie_details(movie_div):
    expected = ('angel heart', '1987', 'horror', '7.3', '/download/9994')

    actual = mva.get_movie_details(movie_div)
    assert actual == expected


# def test_download_torrent():
#     assert False

###########################
# DB tests
###########################


def test_movie_in_DB_when_not_in_DB(test_db):
    movie = ('fake movie', '1900', 'musical', '10', '/download/0000')
    assert mva.movie_in_DB(movie, 'test.db') is False


def test_movie_in_DB_when_in_DB(test_db):
    assert os.path.exists('test.db')
    movie = ('angel heart', '1987', 'horror', '7.3', '/download/9994')
    assert mva.movie_in_DB(movie, 'test.db') is True


def test_init_DB_creates_db():
    assert not os.path.exists('test.db')
    mva.init_DB(db_filename='test.db')
    assert os.path.exists('test.db')
    os.remove('test.db')


def test_init_DB_can_create_in_different_dir():
    db_path = os.path.join('tests', 'test.db')
    assert not os.path.exists(db_path)
    mva.init_DB('tests', 'test.db')
    assert os.path.exists(db_path)
    os.remove(db_path)


def test_init_DB_creates_table_and_schema():
    mva.init_DB(db_filename='test.db')
    with sqlite3.connect('test.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='movies'
            """)
        result = cursor.fetchone()
    assert result
    os.remove('test.db')


def test_write_DB_writes_entry(test_db):
    movie = ('fake movie', '1900', 'musical', '10', '/download/0000')
    mva.write_DB(movie, 'test.db')
    assert mva.movie_in_DB(movie, 'test.db')


###########################
# Download tests
###########################

# TODO
# Figure out a sane way to test download_torrent and download_magnet

def test_catch_magnet():
    given = ("No connection adapters were found for 'magnet:?xt=urn:btih:f0b681341f8740eaee513ca742350a599d9d811d&dn=archlinux-2017.11.01-x86_64.iso&tr=udp://tracker.archlinux.org:6969&tr=http://tracker.archlinux.org:6969/announce'",)
    expected = "magnet:?xt=urn:btih:f0b681341f8740eaee513ca742350a599d9d811d&dn=archlinux-2017.11.01-x86_64.iso&tr=udp://tracker.archlinux.org:6969&tr=http://tracker.archlinux.org:6969/announce"
    assert mva.catch_magnet(given) == expected


###########################
# Remote tests
###########################

def test_move_torrents_will_move_single_file(mock_NAS):
    # create test file
    open('this_is_a_test.torrent', 'w').close()

    test_info = {
        'hostname': '127.0.0.1',
        'username': None,
        'password': secrets.test_ssh_pass,
        'torrents': ['this_is_a_test.torrent'],
        'target_dir': '~/volume1/Shared/torrents',
    }

    mva.move_torrents(**test_info)
    assert os.path.exists(mock_NAS + 'volume1/Shared/torrents/this_is_a_test.torrent')

    # remove test file
    os.remove('this_is_a_test.torrent')


def test_move_torrents_will_move_multiple_files(mock_NAS):
    file_list = ['file1.torrent', 'file2.torrent', 'file3.torrent']
    for file in file_list:
        open(file, 'w').close()

    test_info = {
        'hostname': '127.0.0.1',
        'username': None,
        'password': secrets.test_ssh_pass,
        'torrents': file_list,
        'target_dir': '~/volume1/Shared/torrents',
    }

    mva.move_torrents(**test_info)

    for file in file_list:
        assert file in os.listdir(mock_NAS + 'volume1/Shared/torrents/')
        # remove test file
        os.remove(file)


def test_get_finished_will_return_a_list_of_finished_names(mock_NAS):
    expected = ["This.is.a.Fake.Movie.2014.WEBRip.x264-RARBG",
                "Yet.Another.Fake.2017.1080p.BluRay.H264.AAC-RARBG",
                "FakeMovie.2016.1080p.BluRay.H264.AAC-RARBG"]

    test_info = {
        'hostname': '127.0.0.1',
        'username': None,
        'password': secrets.test_ssh_pass,
        'target_dir': '~/volume1/Shared/torrents/finished_torrents',
    }

    returned = mva.get_finished(**test_info)
    assert set(returned) == set(expected)


def test_delete_unwanted_will_remove_unneccesary_files(mock_NAS):
    finished_dir = mock_NAS + "/volume1/Shared/torrents/finished_torrents/"

    expected = ["This.is.a.Fake.Movie.2014.WEBRip.x264-RARBG/RARBG.txt",
                "This.is.a.Fake.Movie.2014.WEBRip.x264-RARBG/Subs/2_Eng.asdf",
                "Yet.Another.Fake.2017.1080p.BluRay.H264.AAC-RARBG/RARBG.txt",
                "Yet.Another.Fake.2017.1080p.BluRay.H264.AAC-RARBG/randomfile.nco",
                "FakeMovie.2016.1080p.BluRay.H264.AAC-RARBG/somepic.jpg",
                "FakeMovie.2016.1080p.BluRay.H264.AAC-RARBG/RARBG.txt"]

    test_info = {
        'hostname': '127.0.0.1',
        'username': None,
        'password': secrets.test_ssh_pass,
        'target_dir': '~/volume1/Shared/torrents/finished_torrents',
        'shell': 'bash',
    }

    mva.delete_unwanted(**test_info)

    # check files deleted
    for file in expected:
        assert not os.path.exists(finished_dir + file)


def test_delete_unwanted_keeps_movies_and_subtitles(mock_NAS):
    finished_dir = mock_NAS + "/volume1/Shared/torrents/finished_torrents/"

    expected = ["This.is.a.Fake.Movie.2014.WEBRip.x264-RARBG/This.is.a.Fake.Movie.2014.WEBRip.x264-RARBG.mp4",
                "This.is.a.Fake.Movie.2014.WEBRip.x264-RARBG/Subs/2_Eng.srt",
                "Yet.Another.Fake.2017.1080p.BluRay.H264.AAC-RARBG/Yet.Another.Fake.2017.1080p.BluRay.H264.AAC-RARBG.avi",
                "Yet.Another.Fake.2017.1080p.BluRay.H264.AAC-RARBG/Subs/2_Eng.srt",
                "FakeMovie.2016.1080p.BluRay.H264.AAC-RARBG/FakeMovie.2016.1080p.BluRay.H264.AAC-RARBG.mkv"]

    test_info = {
        'hostname': '127.0.0.1',
        'username': None,
        'password': secrets.test_ssh_pass,
        'target_dir': '~/volume1/Shared/torrents/finished_torrents',
        'shell': 'bash',
    }

    mva.delete_unwanted(**test_info)

    for file in expected:
        assert os.path.exists(finished_dir + file)


# def test_match_movie_to_folder_returns_word_based_titles():

#     given = ["This.is.a.Fake.Movie.2014.WEBRip.x264-RARBG",
#              "Yet.Another.Fake.2017.1080p.BluRay.H264.AAC-RARBG",
#              "FakeMovie.2016.1080p.BluRay.H264.AAC-RARBG"]

#     expected = ["This is a Fake Movie (2014)",
#                 "Yet Another Fake Movie (2017)",
#                 "FakeMovie (2016)"]

#     for item in given:
#         assert mva.match_movie_to_folder(item) in expected


# def test_match_movie_to_folder_returns_numeric_titles():

#     given = ["3.33.2017.1080p.BluRay.H264.AAC-RARBG",
#              "24.Meters.Sideways.2017.1080p.BluRay.H264.AAC-RARBG",
#              "Winter.1942.2008.1080p.BluRay.H264.AAC-RARBG"]

#     expected = ["3:33 (2017)",
#                 "24 Meters Sideways (2017)",
#                 "Winter 1942 (2008)"]

#     for item in given:
#         assert mva.match_movie_to_folder(item) in expected


# def test_rename_and_move_will_move_folders(mock_NAS):
#     expected_dir = mock_NAS + "volume1/Shared/movies"

#     given_folders = os.listdir(expected_dir)

#     mva.rename_and_move_finished()

#     assert len(given_folders) == 3


# def test_rename_and_move_will_rename_folders_and_files_correctly(mock_NAS):
#     expected_dir = mock_NAS + "volume1/Shared/movies"

#     expected_folders = ["This is a Fake Movie (2014)",
#                         "Yet Another Fake (2017)",
#                         "FakeMovie (2016)"]

#     given_folders = os.listdir(expected_dir)

#     mva.rename_and_move_finished()

#     assert set(given_folders) == set(expected_folders)


###########################
# Fixtures & helpers
###########################

# this is also bad
def mock_div_parser(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find("div", class_="browse-movie-wrap")


@pytest.fixture
def html_stub():
    with open("tests/Page1.html") as f:
        return f.read()


# this is bad. Make an independent stub
@pytest.fixture
def movie_div(html_stub):
    divs = mva.find_movies(html_stub)
    return divs[0]


@pytest.fixture(scope="function")
def test_db():

    test_movies = [("angel heart", "1987", "horror", "7.3", "/download/9994"),
                   ("this is a fake movie", "2014", "thriller", "8", "/download/asdf"),
                   ("yet another fake", "2017", "musical", "9.2", "/download/qwert"),
                   ("fakemovie", "2016", "action", "2", "/download/yuiop"),
                   ("3:33", "2017", "horror", "10", "/download/asdf"),
                   ("24 meters sideways", "2017", "comedy", "6", "/download/asdf"),
                   ("winter 1942", "2008", "Animation", "9", "/download/asdf")]

    assert not os.path.exists('test.db')

    with sqlite3.connect('test.db') as conn:
        conn.execute('''CREATE TABLE movies
        (id integer primary key autoincrement not null, title text, year text,
        genre text, rating text, download text)''')

        query = '''INSERT INTO movies (title, year, genre, rating, download)
        VALUES (?, ?, ?, ?, ?)'''

        conn.executemany(query, test_movies)

    yield

    # destroy the DB
    os.remove('test.db')


@pytest.fixture(scope="function")
def mock_NAS():
    # setup
    user = os.path.expanduser("~/")
    os.makedirs(user + "volume1/Shared/torrents/finished_torrents", exist_ok=True)
    os.makedirs(user + "volume1/Shared/movies", exist_ok=True)

    finished_dir = user + "/volume1/Shared/torrents/finished_torrents/"
    # fake movies
    os.makedirs(finished_dir + "This.is.a.Fake.Movie.2014.WEBRip.x264-RARBG/Subs", exist_ok=True)
    open(finished_dir + "This.is.a.Fake.Movie.2014.WEBRip.x264-RARBG/This.is.a.Fake.Movie.2014.WEBRip.x264-RARBG.mp4", 'w').close()
    open(finished_dir + "This.is.a.Fake.Movie.2014.WEBRip.x264-RARBG/RARBG.txt", 'w').close()
    open(finished_dir + "This.is.a.Fake.Movie.2014.WEBRip.x264-RARBG/Subs/2_Eng.srt", 'w').close()
    open(finished_dir + "This.is.a.Fake.Movie.2014.WEBRip.x264-RARBG/Subs/2_Eng.asdf", 'w').close()

    os.makedirs(finished_dir + "Yet.Another.Fake.2017.1080p.BluRay.H264.AAC-RARBG/Subs", exist_ok=True)
    open(finished_dir + "Yet.Another.Fake.2017.1080p.BluRay.H264.AAC-RARBG/Yet.Another.Fake.2017.1080p.BluRay.H264.AAC-RARBG.avi", 'w').close()
    open(finished_dir + "Yet.Another.Fake.2017.1080p.BluRay.H264.AAC-RARBG/RARBG.txt", 'w').close()
    open(finished_dir + "Yet.Another.Fake.2017.1080p.BluRay.H264.AAC-RARBG/randomfile.nco", 'w').close()
    open(finished_dir + "Yet.Another.Fake.2017.1080p.BluRay.H264.AAC-RARBG/Subs/2_Eng.srt", 'w').close()

    os.makedirs(finished_dir + "FakeMovie.2016.1080p.BluRay.H264.AAC-RARBG", exist_ok=True)
    open(finished_dir + "FakeMovie.2016.1080p.BluRay.H264.AAC-RARBG/FakeMovie.2016.1080p.BluRay.H264.AAC-RARBG.mkv", 'w').close()
    open(finished_dir + "FakeMovie.2016.1080p.BluRay.H264.AAC-RARBG/somepic.jpg", 'w').close()
    open(finished_dir + "FakeMovie.2016.1080p.BluRay.H264.AAC-RARBG/RARBG.txt", 'w').close()


    yield user

    # teardown
    shutil.rmtree(user + "/volume1/")
