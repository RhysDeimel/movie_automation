import pytest
import movie_automation as mva

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
# Scraper tests
###########################


def test_find_movies(html_stub_a):
    """
    20 movies exist on the page
    """
    matches = mva.find_movies(html_stub_a)
    assert len(matches) == 20


def test_get_title(movie_div):
    expected = "Angel Heart"
    assert mva.get_title(movie_div) == expected


def test_get_year(movie_div):
    expected = "1987"
    assert mva.get_year(movie_div) == expected


def test_get_category(movie_div):
    expected = "Horror"
    assert mva.get_category(movie_div) == expected


def test_get_rating(movie_div):
    expected = "7.3"
    assert mva.get_rating(movie_div) == expected


def test_get_download(movie_div):
    expected = "/download/9994"
    assert mva.get_download(movie_div) == expected


def test_get_movie_details(movie_div):
    expected = ('Angel Heart', '1987', 'Horror', '7.3', '/download/9994')

    actual = mva.get_movie_details(movie_div)
    assert actual == expected


###########################
# DB tests
###########################

def test_movie_in_DB_when_not_in_DB():
    movie = ('Angel Heart', '1987', 'Horror', '7.3', '/download/9994')
    assert mva.movie_in_DB(movie) is False


def test_movie_in_DB_when_in_DB():
    assert False


###########################
# Fixtures
###########################


@pytest.fixture
def html_stub_a():
    with open("tests/Page1.html") as f:
        return f.read()


@pytest.fixture
def html_stub_b():
    with open("tests/Page2.html") as f:
        return f.read()


@pytest.fixture
def movie_div(html_stub_a):
    divs = mva.find_movies(html_stub_a)
    return divs[0]
