#!/usr/local/bin/python3

import re
import requests
from bs4 import BeautifulSoup
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieSite:
    def __init__(self, site_url = None, theater_name = None, list_selector = None, text_search = None):
        self.site_url = site_url
        self.theater_name = theater_name
        self.list_selector = list_selector
        self.text_search = text_search
        self.movie_list = ([])
        self.movie_filter = ([])

    def __str__(self):
        return "\n".join(['    {}'.format(movie) for movie in self.movies()])
    
    def movies(self):
        # Only generate list if we haven't already done so
        # Doesn't currently handle cases where we have already done so but got 0 movies
        if len(list(self.movie_list)) == 0:
            logging.info('Generating movie list for {}'.format(self.theater_name))
            soup = BeautifulSoup(requests.get(self.site_url).text, 'html.parser')
            try:
                self.movie_list = set(self._generate_movie_list(soup))
            except (AttributeError, IndexError):
                logging.error('Error retrieving data for {} -- check configuration.'.format(self.theater_name))
                self.movie_list = []
            logging.debug('Got movie list: {}'.format(self.movie_list))

            if len(self.movie_filter) > 0:
                logging.info('Applying user filter to movie list for {}'.format(self.theater_name))
                self.movie_list = self._filter_movie_list(self.movie_list, self.movie_filter)
                logging.debug('Filtered to {}'.format(self.movie_list))
            else:
                logging.info('No user filter found during {} generation'.format(self.theater_name))

            logging.debug('Returning list is type {}, value {}'.format(type(self.movie_list), self.movie_list))
            if self.movie_list == {None}:
                logging.debug('Movie list is "None", setting to []')
                self.movie_list = []
            else:
                logging.debug('Movie list is {}, stripping titles'.format(self.movie_list))
                self.movie_list = sorted(self._strip_movie_titles(self.movie_list))
        else:
            logging.debug('Skipping movie list generation for {} because we already have it'.format(self.theater_name))
        logging.debug('Completed movies() method for {}, filter is now {}'.format(self.theater_name, self.movie_filter))
        return self.movie_list

    def _strip_movie_titles(self, movie_titles):
        # Could do multiple regexes in one pass but let's start simple
        logging.debug('Stripping titles: {}'.format(movie_titles))
        movie_titles = [re.sub(r'^\W+', '', title) for title in movie_titles]
        movie_titles = [re.sub(r'\W+$', '', title) for title in movie_titles]
        movie_titles = [re.sub(r' //.*', '', title) for title in movie_titles]
        movie_titles = [re.sub(u"\u2019", '\'', title) for title in movie_titles]
        logging.debug('Stripped titles: {}'.format(movie_titles))
        return movie_titles

    def _filter_movie_list(self, movie_list, movie_filter):
        # It would be more efficient to apply this only once after retrieving from all theaters
        logging.debug('Movie list is {}'.format(movie_list))
        logging.debug('User filter is {}'.format(movie_filter))
        return list(filter(
            (lambda x: any(filter_string in x for filter_string in movie_filter)), movie_list
        ))

    def _generate_movie_list(self, soup):
        logging.debug('Using list_selector {} for URL {}'.format(self.list_selector, self.site_url))
        movie_list = soup.select(self.list_selector)
        logging.debug('Selected data from soup.select() is {}'.format(movie_list))
        movies = [movie.string for movie in movie_list]
        logging.debug('Movie strings are {}'.format(movies))
        if self.text_search is not None:
            # Special case to handle multiple movies in one text string
            logging.debug('Applying custom text search {}'.format(self.text_search))
            movies = re.search(self.text_search, ', '.join(movies)).group(1).split(', ')
        return movies


class Theaters:
    def __init__(self):
        laurelhurst_theater = MovieSite(
            site_url = 'http://laurelhursttheater.com/', theater_name = 'Laurelhurst',
            list_selector = 'div.movieListing_titleContainer > span.movieListing_title > a'
        )
        lake_theater = MovieSite(
            site_url = 'http://laketheatercafe.com/', theater_name = 'Lake Theater',
            list_selector = 'section#nowplaying > div.section-inner > div.section-content > p > span',
            text_search = 'Now Playing: (.+)$'
        )
        academy_theater = MovieSite(
            site_url = 'http://www.academytheaterpdx.com/', theater_name = 'Academy Theater',
            list_selector = 'div.now_playing > section.board > ul > li > a'
        )
        livingroom_theater = MovieSite(
            site_url = 'http://pdx.livingroomtheaters.com/', theater_name = 'Living Room Theaters',
            list_selector = 'ul.movie_titles > li > a'
        )
        wunderland_theater = MovieSite(
            site_url = 'http://www.wunderlandgames.com/gettimes.asp?house=3054',
            theater_name = 'Milwaukie Wunderland Cinema', list_selector = 'a.a1title > b'
        )
        moreland_theater = MovieSite(
            site_url = 'https://ticketing.us.veezi.com/sessions/?siteToken=v0v9bscth4zdgv6ezczt5ecsjm',
            theater_name = 'Moreland Theater',
            list_selector = 'div#sessionsByFilmConent > div.film > div > h3.title'
        )
        self.theaters = [ laurelhurst_theater, lake_theater, academy_theater, 
                livingroom_theater, wunderland_theater, moreland_theater ]

    def theater_list(self):
        return self.theaters

