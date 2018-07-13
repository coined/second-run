#!/usr/local/bin/python3

import re
from moviescraper import moviescraper
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List movies currently playing in a set of specified theaters via web scraping.
#
# Each theater has its own class. On request, it returns a list of movies currently playing,
# scraped from its site. This script prompts for an optional filter, restricting output to matching movies.

# To do:
#
#   * Scraping / DOM details for each theater are stored in a config file, and there's only
#     one class for theaters (i.e. it's all in MovieSite).
#   * User movie interests can be saved and loaded.
#   * Cached movie lists from theaters, expiring after a day.
#   * A web interface allowing multiple users.
#   * Daily notifications of matching movies.
#   * Intelligent limits to those daily notifications (e.g. only notify once per theater per movie).

def main():
    user_movies = _create_filter()
    logging.debug('>>> main(): Created filter')
    theaters = moviescraper.Theaters()
    logging.debug('>>> main(): Using default theater list "{}"'.format(theaters))

    movie_list = {}

    logging.info('Starting movie list generation')
    for theater in theaters.theater_list():
        logging.debug('*** Starting {} ***'.format(theater.theater_name))
        theater.movie_filter = user_movies.movies()
        logging.debug('Got movie filter {}'.format(theater.movie_filter))
        if len(theater.movies()) == 0:
            logging.debug('{} returned 0 movies.'.format(theater.theater_name))
        else:
            for movie in theater.movies():
                logging.debug('Starting movie {} for theater {}'.format(movie, theater.theater_name))
                if movie in movie_list:
                    movie_list[movie].append(theater.theater_name)
                    logging.debug('Added {} to {}, user_movies is now {}'.format(
                        movie, theater.theater_name, user_movies.movies())
                    )
                else:
                    movie_list[movie] = [ theater.theater_name ]
                    logging.debug('\tAdded {} to {}, user_movies is now {}'.format(
                        movie, theater.theater_name, user_movies.movies())
                    )
        logger.debug('*** Ending theater loop for {}, theater filter is now {}, user_movies is now {} ***'.format(
            theater.theater_name, theater.movie_filter, user_movies.movies()))

    print()

    for movie, theaters in sorted(movie_list.items()):
        print('{:<40} {}'.format(movie, ', '.join(theaters)))

    print()

def _create_filter():
    user_movies = UserMovies()
    for x in range(10):
        filter_string = input("Enter a movie string, or press enter to begin search: ")
        if bool(not filter_string or filter_string.isspace()):
            break
        else:
            logging.debug('Adding {} to user movie filter'.format(filter_string))
            user_movies.add_movies([filter_string])
    return user_movies

class UserMovies:
    def __init__(self, movies = []):
        self.movie_filter = set(movies)

    def movies(self):
        return self.movie_filter

    def add_movies(self, movies):
        self.movie_filter.update(movies)

    def remove_movies(self, movies):
        self.movie_filter = self.movie_list.difference(movies)

main()
