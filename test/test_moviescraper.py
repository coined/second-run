#!/usr/local/bin/python3

import unittest
from unittest.mock import MagicMock
from bs4 import BeautifulSoup
import logging
from moviescraper import moviescraper
import os
import shutil
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestTheater(unittest.TestCase):
    def setUp(self):
        logging.debug('TEST: Creating base test theater Theater')
        self.test_theater = moviescraper.Theater(
            site_url = 'http://testtheatersite.com/', theater_name = 'Test Theater',
            list_selector = 'div#test-id > div.test-class > span',
            text_search = 'Test (.+)$'
        )
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_init(self):
        self.assertEqual(self.test_theater.site_url, 'http://testtheatersite.com/')
        self.assertEqual(self.test_theater.theater_name, 'Test Theater')
        self.assertEqual(self.test_theater.list_selector, 'div#test-id > div.test-class > span')
        self.assertEqual(self.test_theater.text_search, 'Test (.+)$')

    def test_strip_movie_titles(self):
        unstripped_titles = [
            ' A movie',
            'Another movie // with some following text',
            'The Apostrophe' + u"\u2019" + 's Movie'
        ]
        expected_stripped_titles = [
            'A movie',
            'Another movie',
            'The Apostrophe\'s Movie'
        ]

        stripped_titles = self.test_theater._strip_movie_titles(unstripped_titles)

        self.assertEqual(stripped_titles, expected_stripped_titles)

    def test_filter_movie_list(self):
        unfiltered_list = [
            'A movie',
            'Another movie',
            'The Apostrophe\'s Movie'
        ]
        movie_filter = [
            'other',
            'Movie'
        ]
        expected_filtered_list = [
            'Another movie',
            'The Apostrophe\'s Movie'
        ]

        filtered_list = self.test_theater._filter_movie_list(unfiltered_list, movie_filter)

        self.assertEqual(filtered_list, expected_filtered_list)

    def test_generate_movie_list(self):
        self.test_theater._get_soup = MagicMock()
        self.test_theater._get_soup.return_value = BeautifulSoup(
            '''<html><body><div class="test_1"><div id="test_2">
            <span>Test Movie</span><span>Test Movie Two</span>
            </div></div></body></html>''', 'html.parser'
        )
        logging.debug('_get_soup() currently returns {}'.format(self.test_theater._get_soup()))
        self.test_theater.list_selector = 'div.test_1 > div#test_2 > span'
        self.test_theater.text_search = None
        movie_list = self.test_theater._generate_movie_list()
        self.assertEqual(movie_list, ['Test Movie', 'Test Movie Two'])

    def test_generate_movie_list_with_text_search(self):
        self.test_theater._get_soup = MagicMock()
        self.test_theater._get_soup.return_value = BeautifulSoup(
            '''<html><body><div class="test_1"><div id="test_2">\
            <span>Awesome Movies: Test Movie, Test Movie Two</span>\
            </div></div></body></html>''', 'html.parser'
        )
        self.test_theater.list_selector = 'div.test_1 > div#test_2 > span'
        self.test_theater.text_search = 'Awesome Movies: (.+)'
        movie_list = self.test_theater._generate_movie_list()
        self.assertEqual(movie_list, ['Test Movie', 'Test Movie Two'])

    def test_generate_movie_list_from_html_page(self):
        self.test_theater.site_url = os.path.join(os.path.dirname(__file__), 'sample_site.html')
        self.test_theater.text_search = None
        movie_list = self.test_theater._generate_movie_list()
        self.assertEqual(movie_list, [
            'First Sample Movie',
            '  Second Sample Movie: The Return // Other Details',
            'Third Sample Movie  '
        ])

    def test_save_load_theater_info(self):
        logging.debug('TEST: Saving theater info in test_save_load_theater_info()')
        self.test_theater._save_theater_info(os.path.join(self.test_dir, 'test_theater.p'))

        logging.debug('TEST: Loading theater info in test_save_load_theater_info()')
        test_theater_reloaded = moviescraper.Theater(filepath=os.path.join(self.test_dir, 'test_theater.p'))

        self.assertEqual(test_theater_reloaded.site_url, 'http://testtheatersite.com/')
        self.assertEqual(test_theater_reloaded.theater_name, 'Test Theater')
        self.assertEqual(test_theater_reloaded.list_selector, 'div#test-id > div.test-class > span')
        self.assertEqual(test_theater_reloaded.text_search, 'Test (.+)$')

class TestTheaterList(unittest.TestCase):
    def setUp(self):
        test_theater_one = moviescraper.Theater(
            site_url = 'http://testtheatersite1.com/',
            theater_name = 'Test Theater One',
            list_selector = 'div#test-id > div.test-class > span',
        )
        test_theater_two = moviescraper.Theater(
            site_url = 'http://testtheatersite2.com/',
            theater_name = 'Test Theater Two',
            list_selector = 'div#test-id > div.test-class > span'
        )
        self.test_theater_list = moviescraper.TheaterList()
        self.test_theater_list.add_theater(test_theater_one)
        self.test_theater_list.add_theater(test_theater_two)

    def test_list_theaters(self):
        self.assertEqual(
            self.test_theater_list.list_theaters(),
            ['Test Theater One', 'Test Theater Two']
        )

    def test_add_theater(self):
        self.test_theater_list.add_theater(moviescraper.Theater(
            site_url = 'http://testtheatersite3.com/',
            theater_name = 'Test Theater Three',
            list_selector = 'div#test-id > div.test-class > span'
        ))
        self.assertEqual(
            self.test_theater_list.list_theaters(),
            ['Test Theater One', 'Test Theater Two', 'Test Theater Three']
        )

    def test_remove_theater(self):
        self.test_theater_list.remove_theater(self.test_theater_list.theater_list[0])
        self.assertEqual(
            self.test_theater_list.list_theaters(),
            ['Test Theater Two']
        )

    def test_init_with_config(self):
        config = [
            {
                'site_url' : 'http://testtheatersite1.com/',
                'theater_name': 'Test Theater One',
                'list_selector' : 'div > span'
            },
            {
                'site_url' : 'http://testtheatersite2.com/',
                'theater_name': 'Test Theater Two',
                'list_selector' : 'div > span'
            }
        ]
        self.test_theater_list = moviescraper.TheaterList(config)
        self.assertEqual(
            self.test_theater_list.list_theaters(),
            ['Test Theater One', 'Test Theater Two']
        )
        self.assertEqual(
            self.test_theater_list.theater_list[0].site_url,
            'http://testtheatersite1.com/'
        )
        self.assertEqual(
            self.test_theater_list.theater_list[1].theater_name,
            'Test Theater Two'
        )
        self.assertEqual(
            self.test_theater_list.theater_list[1].list_selector,
            'div > span'
        )

    def test_movies(self):
        test_theater_one = moviescraper.Theater(
            site_url = os.path.join(os.path.dirname(__file__), 'sample_site.html'),
            theater_name = 'Test Theater One',
            list_selector = 'div#test-id > div.test-class > span',
        )
        test_theater_two = moviescraper.Theater(
            site_url = os.path.join(os.path.dirname(__file__), 'sample_site.html'),
            theater_name = 'Test Theater Two',
            list_selector = 'div#test-id > div.test-class > span',
        )
        self.test_theater_list = moviescraper.TheaterList()
        self.test_theater_list.add_theater(test_theater_one)
        self.test_theater_list.add_theater(test_theater_two)

        self.assertEqual(
            self.test_theater_list.movies(), {
                'Test Theater One' : [
                    'First Sample Movie',
                    'Second Sample Movie: The Return',
                    'Third Sample Movie'
                ],
                'Test Theater Two' : [
                    'First Sample Movie',
                    'Second Sample Movie: The Return',
                    'Third Sample Movie'
                ]
            }
        )


if __name__ == '__main__':
    unittest.main()
