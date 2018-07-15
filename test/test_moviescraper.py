#!/usr/local/bin/python3

import unittest
from bs4 import BeautifulSoup
from moviescraper import moviescraper

class TestMovieSite(unittest.TestCase):
    def setUp(self):
        self.test_theater = moviescraper.MovieSite(
            site_url = 'http://testtheatersite.com/', theater_name = 'Test Theater',
            list_selector = 'div.test_1 > div#test_2 > span',
            text_search = 'Test (.+)$'
        )

    def test_init(self):
        self.assertEqual(self.test_theater.site_url, 'http://testtheatersite.com/')
        self.assertEqual(self.test_theater.theater_name, 'Test Theater')
        self.assertEqual(self.test_theater.list_selector, 'div.test_1 > div#test_2 > span')
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

    def test_generate_movie_list_without_text_search(self):
        soup = BeautifulSoup('<html><body><div class="test_1"><div id="test_2">\
                <span>Test Movie</span><span>Test Movie Two</span>\
                </div></div></body></html>', 'html.parser')
        self.test_theater.text_search = None
        movie_list = self.test_theater._generate_movie_list(soup)
        self.assertEqual(movie_list, ['Test Movie', 'Test Movie Two'])

    def test_generate_movie_list_with_text_search(self):
        soup = BeautifulSoup('<html><body><div class="test_1"><div id="test_2">\
                <span>Awesome Movies: Test Movie, Test Movie Two</span>\
                </div></div></body></html>', 'html.parser')
        self.test_theater.text_search = 'Awesome Movies: (.+)'
        movie_list = self.test_theater._generate_movie_list(soup)
        self.assertEqual(movie_list, ['Test Movie', 'Test Movie Two'])

if __name__ == '__main__':
    unittest.main()
