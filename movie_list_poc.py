#!/usr/local/bin/python3

import pickle
import re
import requests
from bs4 import BeautifulSoup
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List movies currently playing in a set of specified theaters via web scraping.
#
# Each theater has its own class. On request, it returns a list of movies currently playing,
# scraped from its site. The script can take a filter, restricting output to matching movies.

# Planned changes (short term):
#
#   * Scraping / DOM details for each theater are stored in a config file, and there's only
#     one class for theaters (i.e. it's all in MovieSite).
#   * User movie interests can be saved and loaded.
#   * Better contextual data is returned, so that we can distinguish between e.g. which theaters
#     failed due to scraping problems vs. which returned nothing due to user filter matching.

# Planned changes (long term):
#
#   * Cached movie lists from theaters, expiring after a day.
#   * A web interface allowing multiple users.
#   * Daily notifications of matching movies.
#   * Intelligent limits to notifications (e.g. only notify once per theater per movie).

class UserMovies:
    def __init__(self, movies = []):
        self.movie_filter = set(movies)

    def movies(self):
        return self.movie_filter

    def add_movies(self, movies):
        self.movie_filter.update(movies)

    def remove_movies(self, movies):
        self.movie_filter = self.movie_list.difference(movies)

class MovieSite:
    def __init__(self):
        self.site_url = "http://example.com"
        self.theater_name = "Example Theater"
        self.movie_list = ([])
        self.movie_filter = ([])

    def __str__(self):
        return "\n".join(['    {}'.format(movie) for movie in self.movies()])
    
    def movies(self):
        # Only generate list if we haven't already done so
        logging.debug('Existing movie_list has {} elements'.format(len(list(self.movie_list))))
        if len(list(self.movie_list)) == 0:
            logging.info('Generating movie list for {}'.format(self.theater_name))
            soup = BeautifulSoup(requests.get(self.site_url).text, 'html.parser')
            try:
                self.movie_list = set(self.generate_movie_list(soup))
            # Trap errors due to a mismatch between our expectations and the actual site structure
            except (AttributeError, IndexError):
                logging.error('{} returned no movies -- check configuration.'.format(self.theater_name))
                self.movie_list = []
            logging.debug('Got movie list: {}'.format(self.movie_list))
            if len(self.movie_filter) > 0:
                logging.info('Applying user filter to movie list for {}'.format(self.theater_name))
                self.movie_list = self.filter_movie_list(self.movie_list, self.movie_filter)
                logging.debug('Filtered to {}'.format(self.movie_list))
            else:
                logging.info('No user filter found during {} generation'.format(self.theater_name))
            self.movie_list = sorted(map(str.strip, self.movie_list))
        else:
            logging.info('Skipping movie list generation for {} because we already have it'.format(self.theater_name))
        logging.debug('Completed movies() method for {}, filter is now {}'.format(self.theater_name, self.movie_filter))
        return self.movie_list

    def filter_movie_list(self, movie_list, movie_filter):
        logging.debug('Movie list is {}'.format(movie_list))
        logging.debug('User filter is {}'.format(movie_filter))
        return list(filter(
            (lambda x: any(filter_string in x for filter_string in movie_filter)), movie_list
        ))

    def generate_movie_list(self, soup):
        pass


class LaurelhurstSite(MovieSite):
    def __init__(self):
        super(LaurelhurstSite, self).__init__()
        self.site_url = 'http://laurelhursttheater.com/'
        self.theater_name = "Laurelhurst"

    def generate_movie_list(self, soup):
        movie_section = soup.find("div", { "class" : "movieListingMargins" })
        movies = [re.sub(r'^\W+', '', movie.a.string) for movie in movie_section.find_all(
            "span", {"class" : "movieListing_title"}
        )]
        return movies


class LakeTheaterSite(MovieSite):
    def __init__(self):
        super(LakeTheaterSite, self).__init__()
        self.site_url = 'http://laketheatercafe.com/'
        self.theater_name = "Lake Theater"

    def generate_movie_list(self, soup):
        movie_section = soup.find("section", { "id" : "nowplaying" }).div.div.p.span.string
        movie_list = [re.sub('’', '\'', re.sub(r' //.*', '', movie)) for movie in re.search(
            'Now Playing: (.+)$', movie_section
        ).group(1).split(', ')]
        return movie_list


class AcademyTheaterSite(MovieSite):
    def __init__(self):
        super(AcademyTheaterSite, self).__init__()
        self.site_url = 'http://www.academytheaterpdx.com/'
        self.theater_name = "Academy Theater"

    def generate_movie_list(self, soup):
        movie_section = soup.find("div", { "class" : "now_playing" }).section.ul
        movies = [movie.a.string for movie in movie_section.find_all("li") if 'post_type=movie' in movie.a.get('href')]
        return movies


class LivingRoomTheatersSite(MovieSite):
    def __init__(self):
        super(LivingRoomTheatersSite, self).__init__()
        self.site_url = 'http://pdx.livingroomtheaters.com/'
        self.theater_name = "Living Room Theaters"

    def generate_movie_list(self, soup):
        movie_section = soup.find("ul", { "class" : "movie_titles" })
        movies = [movie.a.string for movie in movie_section.find_all("li") if movie.a and 'movie_detail' in movie.a.get('href')]
        return movies


class MilwaukieWunderlandCinema(MovieSite):
    def __init__(self):
        super(MilwaukieWunderlandCinema, self).__init__()
        self.site_url = 'http://www.wunderlandgames.com/gettimes.asp?house=3054'
        self.theater_name = "Milwaukie Wunderland Cinema"

    def generate_movie_list(self, soup):
        movie_section = soup.find("table", { "class" : "a1table" })
        movies = [movie.b.string for movie in movie_section.find_all("a") if movie['class'] == ['a1title']]
        return movies


class MorelandTheater(MovieSite):
    def __init__(self):
        super(MorelandTheater, self).__init__()
        # self.site_url = 'http://www.morelandtheater.com/'
        self.site_url = 'https://ticketing.us.veezi.com/sessions/?siteToken=v0v9bscth4zdgv6ezczt5ecsjm'
        self.theater_name = "Moreland Theater"

    def generate_movie_list(self, soup):
        # Yes, it's "conent"
        movie_section = soup.find("div", { "id" : "sessionsByFilmConent" })
        movies = [movie.string for movie in movie_section.find_all("h3", {"class" : "title"})]
        return movies


user_movies = UserMovies()
for x in range(10):
    filter_string = input("Enter a movie string, or press enter to begin search: ")
    if bool(not filter_string or filter_string.isspace()):
        break
    else:
        logging.info('Adding {} to user movie filter'.format(filter_string))
        user_movies.add_movies([filter_string])

movie_list = {}

logging.info('Starting movie list generation')
for site in [ LaurelhurstSite(), LakeTheaterSite(), AcademyTheaterSite(), LivingRoomTheatersSite(), MilwaukieWunderlandCinema(), MorelandTheater() ]:
    logging.info('*** Starting {} ***'.format(site.theater_name))
    site.movie_filter = user_movies.movies()
    logging.debug('Got movie filter {}'.format(site.movie_filter))
    if len(site.movies()) == 0:
        print('{} returned no movies -- check configuration.'.format(site.theater_name))
    else:
        for movie in site.movies():
            logging.debug('Starting movie {} for theater {}'.format(movie, site.theater_name))
            if movie in movie_list:
                movie_list[movie].append(site.theater_name)
                logging.debug('\tAdded {} to {}, user_movies is now {}'.format(
                    movie, site.theater_name, user_movies.movies())
                )
            else:
                movie_list[movie] = [ site.theater_name ]
                logging.debug('\tAdded {} to {}, user_movies is now {}'.format(
                    movie, site.theater_name, user_movies.movies())
                )
    logger.debug('*** Ending site loop for {}, site filter is now {}, user_movies is now {} ***'.format(
        site.theater_name, site.movie_filter, user_movies.movies()))

print()

for movie, theaters in sorted(movie_list.items()):
    print('{:<40} {}'.format(movie, ', '.join(theaters)))

print()

